"""Teste de contrato GraphRAG sem depender de GPU ou banco externo."""
import unittest
from unittest.mock import Mock
from graphpath_v2.graphrag import build_documents, ask
from graphpath_v2.config import Settings


class TestGraphRAG(unittest.TestCase):
    def test_documents_include_graph_neighborhood(self):
        store = Mock()
        store.graph.return_value = {
            'nodes': [{'id': 'GP-WEB', 'kind': 'Asset', 'criticality': 'unspecified', 'description': ''},
                      {'id': 'GP-DB', 'kind': 'Asset', 'criticality': 'high', 'description': ''}],
            'edges': [{'source': 'GP-WEB', 'target': 'GP-DB', 'type': 'CAN_REACH'}]
        }
        docs = build_documents(store, 'base')
        self.assertEqual(len(docs), 2)
        self.assertIn('CAN_REACH -> GP-DB', docs[0]['text'])
        self.assertIn('base:GP-WEB', docs[0]['key'])

    def test_ask_returns_grounded_sources(self):
        store = Mock()
        client = Mock()
        client.embed.return_value = [[0.1, 0.2, 0.3]]
        client.generate.return_value = 'O GP-WEB é um componente intermediário modelado [base:GP-WEB].'
        store.run.return_value = [{'key': 'base:GP-WEB', 'id':'GP-WEB','context': 'GP-WEB modelado', 'score':0.9}]
        result = ask(store, client, Settings(), 'Quais são os caminhos?', 'base')
        self.assertEqual(result['sources'][0]['id'], 'GP-WEB')
        self.assertIn('GP-WEB', result['answer'])

    def test_expanded_routes_come_from_neo4j_not_the_llm(self):
        store, client = Mock(), Mock()
        store.graph.return_value = {'nodes': [
            {'id': name} for name in (
                'LAB-ID-01', 'LAB-WEB-01', 'LAB-APP-01',
                'LAB-JUMP-01', 'LAB-DB-01'
            )
        ]}
        store.paths.return_value = [
            ['LAB-ID-01', 'LAB-WEB-01', 'LAB-APP-01', 'LAB-DB-01'],
            ['LAB-ID-01', 'LAB-WEB-01', 'LAB-JUMP-01', 'LAB-DB-01'],
        ]
        result = ask(store, client, Settings(),
                     'Quais os caminhos entre LAB-ID-01 e LAB-DB-01?', 'expanded')
        self.assertEqual(result['method'], 'cypher')
        self.assertIn('2 (consulta direta ao Neo4j)', result['answer'])
        self.assertIn('LAB-JUMP-01', result['answer'])
        store.paths.assert_called_once_with('expanded', 'LAB-ID-01', 'LAB-DB-01')
        client.embed.assert_not_called()
        client.generate.assert_not_called()

    def test_mismatched_scenario_does_not_produce_false_answer(self):
        store, client = Mock(), Mock()
        result = ask(store, client, Settings(),
                     'Caminhos de LAB-ID-01 ate LAB-DB-01?', 'base')
        self.assertEqual(result['method'], 'validation')
        self.assertIn('Selecione Expandido', result['answer'])
        store.paths.assert_not_called()
        client.generate.assert_not_called()

    def test_no_modelled_route_has_bounded_negative(self):
        store, client = Mock(), Mock()
        store.graph.return_value = {'nodes': [
            {'id': 'GP-EXT'}, {'id': 'GP-RH'}
        ]}
        store.paths.return_value = []
        result = ask(store, client, Settings(),
                     'Existe caminho de GP-EXT ate GP-RH?', 'base')
        self.assertEqual(result['method'], 'cypher')
        self.assertIn('seis arestas', result['answer'])
        self.assertEqual(result['sources'], [])
        client.generate.assert_not_called()

    def test_empty_corpus_does_not_generate_hallucination(self):
        store,client=Mock(),Mock()
        client.embed.return_value=[[0.5,0.5]]
        store.run.return_value=[]
        result=ask(store,client,Settings(),'Onde estão os ativos?','base')
        self.assertEqual(result['sources'],[])
        client.generate.assert_not_called()


if __name__ == '__main__':
    unittest.main()

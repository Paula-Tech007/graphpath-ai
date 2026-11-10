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

    def test_empty_corpus_does_not_generate_hallucination(self):
        store,client=Mock(),Mock()
        client.embed.return_value=[[0.5,0.5]]
        store.run.return_value=[]
        result=ask(store,client,Settings(),'Onde estão os ativos?','base')
        self.assertEqual(result['sources'],[])
        client.generate.assert_not_called()


if __name__ == '__main__':
    unittest.main()

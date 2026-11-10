"""Testes ao vivo: executados somente mediante variáveis de ambiente.

RUN_GRAPH_E2E=1: Neo4j real + cenário ampliado e duas rotas base.
RUN_OLLAMA_E2E=1: além disso, Ollama embeddinggemma+Qwen e índice vetorial.
"""
import os
import unittest
from graphpath_v2.config import load_config
from graphpath_v2.graph import GraphStore
from graphpath_v2.ollama import OllamaClient
from graphpath_v2.graphrag import index_documents, ask


@unittest.skipUnless(os.getenv('RUN_GRAPH_E2E') == '1', 'Ative RUN_GRAPH_E2E=1 para testar no Neo4j real')
class TestGraphPathV2E2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.settings = load_config()
        cls.store = GraphStore(cls.settings)
        cls.store.seed_expanded()

    @classmethod
    def tearDownClass(cls):
        cls.store.close()

    def test_original_remains_valid(self):
        graph = self.store.graph('base')
        self.assertEqual(len(graph['nodes']), 6)
        self.assertEqual(len(graph['edges']), 5)
        paths = self.store.paths('base', 'GP-EXT', 'GP-DB')
        self.assertEqual(len(paths), 2)
        self.assertTrue(all('GP-WEB' in path for path in paths))

    def test_extended_32_nodes_60_relationships(self):
        graph = self.store.graph('expanded')
        self.assertEqual((len(graph['nodes']), len(graph['edges'])), (32, 60))
        self.assertGreater(len(self.store.paths('expanded', 'LAB-ID-01', 'LAB-DB-01')), 0)

    def test_gds_extended(self):
        result = self.store.centrality('expanded')
        self.assertEqual(len(result), 32)
        self.assertTrue(all('score' in item for item in result))

    @unittest.skipUnless(os.getenv('RUN_OLLAMA_E2E') == '1', 'Ollama opcional; ative RUN_OLLAMA_E2E=1')
    def test_graphrag_real(self):
        client = OllamaClient(self.settings)
        out = index_documents(self.store, client, self.settings)
        self.assertEqual(out['indexed'], 38)
        result = ask(self.store, client, self.settings, 'Quais dependências chegam ao GP-DB?', 'base')
        self.assertTrue(result['sources'])
        self.assertTrue(result['answer'])


if __name__ == '__main__':
    unittest.main()

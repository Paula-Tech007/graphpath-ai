"""Testes rápidos sem servidor Neo4j nem Ollama."""
import unittest
from unittest.mock import patch
from graphpath_v2.sample_data import build_extended_scenario
from graphpath_v2.config import Settings
from graphpath_v2.ollama import OllamaClient


class TestGraphPathV2(unittest.TestCase):
    def test_scenario_size_and_ids(self):
        nodes, edges = build_extended_scenario()
        self.assertEqual((len(nodes), len(edges)), (32, 60))
        ids = {n['id'] for n in nodes}
        self.assertEqual(len(ids), 32)
        self.assertTrue(all(e['source'] in ids and e['target'] in ids for e in edges))

    def test_original_scenario_not_reused(self):
        nodes, _ = build_extended_scenario()
        self.assertTrue(all(n['id'].startswith('LAB-') for n in nodes))
        self.assertNotIn('GP-DB', {n['id'] for n in nodes})

    def test_ollama_http_contract(self):
        settings = Settings(ollama_transport='http')
        client = OllamaClient(settings)
        with patch.object(client, '_request_http', return_value={'embeddings': [[1.0, 0.2]]}) as http:
            self.assertEqual(client.embed(['teste']), [[1.0, 0.2]])
            http.assert_called_once()
        with patch.object(client, '_request_http', return_value={'response': 'Resposta baseada em evidências.'}):
            self.assertIn('evidências', client.generate('Exemplo'))

    def test_settings_reject_external_ollama(self):
        with self.assertRaises(ValueError):
            Settings(ollama_url='http://example.com:11434')

    def test_api_contract(self):
        from fastapi.testclient import TestClient
        from graphpath_v2.api import app
        with patch('graphpath_v2.api._run') as mocked:
            mocked.return_value = {'scenario':'base','nodes':[],'edges':[]}
            r = TestClient(app).get('/api/graph?scenario=base')
            self.assertEqual(r.status_code, 200)
            self.assertEqual(r.json()['nodes'], [])
        self.assertEqual(TestClient(app).get('/api/graph?scenario=other').status_code, 422)
        self.assertEqual(TestClient(app).post('/api/graphrag/ask', json={'question':'x'}).status_code, 422)


if __name__ == '__main__':
    unittest.main()

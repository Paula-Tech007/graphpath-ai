import ast
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TestGraphPathAI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.texto = (ROOT / "evidencias.txt").read_text(
            encoding="utf-8"
        )
        cls.relatorio = (ROOT / "relatorio_tecnico.md").read_text(
            encoding="utf-8"
        )

        bloco = cls.texto.split("CENTRALIDADE GDS:")[0]
        cls.caminhos = [
            ast.literal_eval(linha)
            for linha in bloco.splitlines()
            if linha.startswith("[")
        ]

        cls.centralidades = {
            nome: float(valor)
            for nome, valor in re.findall(
                r'"([^"]+)",\s*([0-9.]+)',
                cls.texto.split("CENTRALIDADE GDS:")[1]
                         .split("IMPACTO:")[0]
            )
        }

    def test_quantidade_de_caminhos(self):
        self.assertEqual(len(self.caminhos), 2)

    def test_rotas_ate_banco_critico(self):
        for caminho in self.caminhos:
            self.assertEqual(caminho[0], "GP-EXT")
            self.assertEqual(caminho[-1], "GP-DB")

    def test_gp_web_obrigatorio(self):
        for caminho in self.caminhos:
            self.assertIn("GP-WEB", caminho)

    def test_centralidade_gds(self):
        self.assertEqual(len(self.centralidades), 6)
        self.assertEqual(
            self.centralidades["GP-WEB"], 3.0
        )
        self.assertGreater(
            self.centralidades["GP-WEB"],
            self.centralidades["GP-APP"]
        )

    def test_impacto(self):
        bloco = self.texto.split("IMPACTO:")[1]
        valores = re.search(
            r'(\d+)\s*,\s*(\d+)\s*$',
            bloco
        )
        self.assertIsNotNone(valores)
        self.assertEqual(
            tuple(map(int, valores.groups())),
            (2, 0)
        )

    def test_relatorio_tecnico(self):
        self.assertIn("GraphPath AI", self.relatorio)
        self.assertIn("GP-WEB", self.relatorio)
        self.assertIn("Graph Data Science", self.relatorio)


if __name__ == "__main__":
    unittest.main()

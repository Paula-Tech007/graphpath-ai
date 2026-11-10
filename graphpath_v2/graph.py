"""Consultas Cypher parametrizadas e cenários de laboratório isolados."""
from .config import Settings
from .sample_data import build_extended_scenario


class GraphStore:
    def __init__(self, settings: Settings):
        from neo4j import GraphDatabase
        user, password = settings.db_auth()
        self.driver = GraphDatabase.driver(settings.neo4j_uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def run(self, cypher: str, **params):
        with self.driver.session(database="neo4j") as session:
            return [r.data() for r in session.run(cypher, params)]

    def seed_expanded(self):
        nodes, links = build_extended_scenario()
        # Somente LAB_*: preserva integralmente as entidades GP_* do MVP.
        self.run("""
        UNWIND $rows AS row
        MERGE (n:LabNode:LabIdentity {id: row.id})
        SET n.kind=row.kind, n.description=row.description, n.criticality=row.criticality
        """, rows=[n for n in nodes if n["label"] == "LabIdentity"])
        self.run("""
        UNWIND $rows AS row
        MERGE (n:LabNode:LabAsset {id: row.id})
        SET n.kind=row.kind, n.description=row.description, n.criticality=row.criticality
        """, rows=[n for n in nodes if n["label"] == "LabAsset"])
        for rel in ("LAB_ACCESS", "LAB_REACH"):
            self.run(f"""
            UNWIND $rows AS row
            MATCH (a:LabNode {{id:row.source}}), (b:LabNode {{id:row.target}})
            MERGE (a)-[:{rel}]->(b)
            """, rows=[x for x in links if x["rel"] == rel])
        return {"nodes": len(nodes), "edges": len(links)}

    def graph(self, scenario="base"):
        if scenario == "base":
            node_query = """MATCH (n) WHERE n:Asset OR n:Identity
                RETURN n.id AS id, head(labels(n)) AS kind,
                       coalesce(n.description,'') AS description,
                       coalesce(n.criticality,'unspecified') AS criticality ORDER BY id"""
            edge_query = """MATCH (a)-[r:HAS_ACCESS|CAN_REACH]->(b)
                WHERE (a:Asset OR a:Identity) AND (b:Asset OR b:Identity)
                RETURN a.id AS source, b.id AS target, type(r) AS type
                ORDER BY source, target"""
        elif scenario == "expanded":
            node_query = """MATCH (n:LabNode) RETURN n.id AS id, n.kind AS kind,
                       n.description AS description, n.criticality AS criticality ORDER BY id"""
            edge_query = """MATCH (a:LabNode)-[r:LAB_ACCESS|LAB_REACH]->(b:LabNode)
                RETURN a.id AS source, b.id AS target, type(r) AS type ORDER BY source, target"""
        else:
            raise ValueError("Cenário inválido: use base ou expanded")
        return {"scenario": scenario, "nodes": self.run(node_query), "edges": self.run(edge_query)}

    def paths(self, scenario: str, source: str, target: str, limit: int = 30):
        if scenario == "base":
            query = """MATCH p=(s:Identity {id:$source})-[:HAS_ACCESS|CAN_REACH*1..6]->(t:Asset {id:$target})
                RETURN [n IN nodes(p) | n.id] AS path ORDER BY length(p) ASC LIMIT $limit"""
        elif scenario == "expanded":
            query = """MATCH p=(s:LabNode {id:$source})-[:LAB_ACCESS|LAB_REACH*1..6]->(t:LabNode {id:$target})
                RETURN [n IN nodes(p) | n.id] AS path ORDER BY length(p) ASC LIMIT $limit"""
        else:
            raise ValueError("Cenário inválido")
        return [x["path"] for x in self.run(query, source=source, target=target, limit=limit)]

    def ensure_gds(self, scenario: str):
        if scenario not in ("base", "expanded"):
            raise ValueError("Cenário inválido")
        name = "graphpath-ai" if scenario == "base" else "graphpath-expanded"
        exists = self.run("RETURN gds.graph.exists($name) AS ok", name=name)[0]["ok"]
        if not exists:
            labels = ["Identity", "Asset"] if scenario == "base" else ["LabIdentity", "LabAsset"]
            rels = ["HAS_ACCESS", "CAN_REACH"] if scenario == "base" else ["LAB_ACCESS", "LAB_REACH"]
            self.run("CALL gds.graph.project($name, $labels, $rels) YIELD graphName RETURN graphName",
                     name=name, labels=labels, rels=rels)
        return name

    def centrality(self, scenario="base"):
        name = self.ensure_gds(scenario)
        return self.run("""CALL gds.betweenness.stream($name) YIELD nodeId, score
            RETURN gds.util.asNode(nodeId).id AS id, score
            ORDER BY score DESC, id""", name=name)

    def health(self):
        return self.run("RETURN 1 AS ok")[0]["ok"] == 1

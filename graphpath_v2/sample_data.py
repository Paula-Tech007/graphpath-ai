"""Cenário ampliado determinístico e estritamente fictício.

32 ativos/identidades e 60 conexões; usa rótulos separados para não mexer
no grafo original GP-EXT/GP-DB nem em sua projeção GDS.
"""


def build_extended_scenario():
    categories = [("ID", 4, "identidade de laboratório", "LabIdentity"),
                  ("WEB", 8, "gateway web de laboratório", "LabAsset"),
                  ("APP", 10, "aplicação fictícia", "LabAsset"),
                  ("JUMP", 4, "servidor de salto fictício", "LabAsset"),
                  ("DB", 6, "base de dados fictícia", "LabAsset")]
    nodes = []
    for prefix, count, desc, label in categories:
        for i in range(1, count + 1):
            id_ = f"LAB-{prefix}-{i:02d}"
            nodes.append({"id": id_, "kind": prefix, "label": label,
                          "description": f"{desc}, identificador {id_}. Dados simulados, sem conexão real.",
                          "criticality": "high" if prefix == "DB" else "unspecified"})
    links = []
    def add(a, b, rel="LAB_REACH"):
        links.append({"source": a, "target": b, "rel": rel})
    def tag(k, i):
        return f"LAB-{k}-{i:02d}"
    for i in range(1, 5):
        for j in (2 * i - 1, 2 * i):
            add(tag("ID", i), tag("WEB", j), "LAB_ACCESS")
    for i in range(1, 9):
        for j in (((i - 1) % 10) + 1, (i % 10) + 1):
            add(tag("WEB", i), tag("APP", j))
        add(tag("WEB", i), tag("JUMP", ((i - 1) % 4) + 1))
    for i in range(1, 11):
        for j in (((i - 1) % 6) + 1, (i % 6) + 1):
            add(tag("APP", i), tag("DB", j))
    for i in range(1, 5):
        for j in (((i - 1) % 6) + 1, (i % 6) + 1):
            add(tag("JUMP", i), tag("DB", j))
    assert len(nodes) == 32 and len(links) == 60
    assert len({n["id"] for n in nodes}) == 32
    assert len({(x["source"], x["target"]) for x in links}) == 60
    return nodes, links

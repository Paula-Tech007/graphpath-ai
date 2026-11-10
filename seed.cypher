MERGE (ext:Identity {id: 'GP-EXT'})
MERGE (web:Asset {id: 'GP-WEB'})
MERGE (app:Asset {id: 'GP-APP'})
MERGE (jump:Asset {id: 'GP-JUMP'})
MERGE (db:Asset {id: 'GP-DB'})
MERGE (rh:Asset {id: 'GP-RH'})
SET db.criticality = 'high',
    rh.criticality = 'medium'
MERGE (ext)-[:HAS_ACCESS]->(web)
MERGE (web)-[:CAN_REACH]->(app)
MERGE (app)-[:CAN_REACH]->(db)
MERGE (web)-[:CAN_REACH]->(jump)
MERGE (jump)-[:CAN_REACH]->(db)
RETURN 'Grafo carregado' AS status;

MATCH (ext:Identity {id: 'GP-EXT'})
      -[:HAS_ACCESS]->(web:Asset)
MATCH p = (web)-[:CAN_REACH*1..3]->
          (db:Asset {id: 'GP-DB'})
RETURN [ext.id] + [n IN nodes(p) | n.id]
       AS caminho
ORDER BY caminho;

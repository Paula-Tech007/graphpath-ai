CALL gds.graph.project(
  'graphpath-ai',
  ['Identity', 'Asset'],
  ['HAS_ACCESS', 'CAN_REACH']
)
YIELD graphName, nodeCount, relationshipCount
RETURN graphName, nodeCount, relationshipCount;

CALL gds.betweenness.stream('graphpath-ai')
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).id AS ativo,
       score AS centralidade
ORDER BY centralidade DESC, ativo;

MATCH p = (:Identity {id: 'GP-EXT'})
  -[:HAS_ACCESS|CAN_REACH*1..4]->
  (:Asset {id: 'GP-DB'})
WITH collect(p) AS caminhos
RETURN
  size(caminhos) AS caminhos_atuais,
  size([p IN caminhos
    WHERE none(n IN nodes(p)
    WHERE n.id = 'GP-WEB')])
    AS caminhos_sem_gp_web;

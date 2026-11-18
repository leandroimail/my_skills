---
tags: [skill-creator]
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

terminei a mudança na coparticipação e preciso da descrição do PR em português e em inglês (o time de Lisboa e o fornecedor da Índia leem o mesmo PR). salva em pr.md. meus rascunhos:

- mexi em src/billing/calc.py, função calc_coparticipacao. antes ela consultava a tabela de teto a cada item da guia, agora consulta uma vez por guia e guarda em memória
- tempo médio de cálculo de uma guia de 200 itens caiu de 2.3s pra 0.4s (medi 10 execuções na minha máquina, não medi em homologação)
- rodei os testes unitários de tests/billing: 41 de 42 passam. o que falha é test_teto_mensal. acho que é arredondamento do teto quando a guia vira o mês, mas não confirmei
- não rodei os testes de integração porque o banco de homologação tava fora
- não muda contrato de API nem precisa de migração

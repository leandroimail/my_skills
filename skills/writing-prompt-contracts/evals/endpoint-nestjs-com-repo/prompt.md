---
tags: [skill-creator]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

preciso mandar o agente criar um endpoint novo na api da rede credenciada (o repo é o diretório atual). é um GET /prestadores/{id}/agenda que devolve os horários livres do prestador nos próximos 30 dias, lendo do Oracle. quem vai consumir é a tela de agendamento do portal. é só leitura e não pode mexer no schema do banco. escreve o prompt-contrato pra eu mandar pro agente. agora não vou conseguir responder pergunta nenhuma, então preenche o que der e marca o resto pra eu ver depois.

Input files: package.json, .nvmrc, README.md, src/prestadores/prestadores.module.ts, src/prestadores/prestadores.controller.ts, src/prestadores/prestadores.service.ts, src/prestadores/prestadores.repository.ts, test/jest-e2e.json, test/prestadores.e2e-spec.ts

# Restart da api-autorizacao

Antes de mais nada verifica-se se o deploy está saudável, executando o comando abaixo e olhando se as réplicas estão todas prontas.

```bash
kubectl get deployment api-autorizacao -n prod
```

Avisar o plantão no canal #plantao-plataforma, sendo que o restart deve levar uns 5 minutos.

Depois faz-se o restart:

```bash
kubectl rollout restart deployment/api-autorizacao -n prod
```

Atenção: o restart derruba as sessões abertas dos operadores, então só fazer fora do horário de pico (08h às 18h) a menos que o coordenador autorize.

O timeout do health check deve estar com o valor abaixo no values-prod.yaml; caso contrário o mesmo deve ser corrigido antes do restart.

```yaml
healthCheck:
  timeout: 1.5
  retries: 3
```

Aguardar um tempo e conferir o health check em https://api-autorizacao.interno.example/health. Fazer o rollback com `kubectl rollout undo deployment/api-autorizacao -n prod` se o health check falhar.

Por fim, registra-se o restart na planilha de mudanças.

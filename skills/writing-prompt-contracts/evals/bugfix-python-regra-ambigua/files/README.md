# faturamento-relatorios

Gera o relatório mensal de faturamento por beneficiário (CSV enviado ao financeiro todo dia 5).

- `src/faturamento/relatorio.py`: `gerar_relatorio(beneficiarios, planos, competencia)`.
- O CSV é consumido por uma planilha do financeiro que espera as colunas na ordem atual.
- Testes: `make test`. Lint: `make lint`.

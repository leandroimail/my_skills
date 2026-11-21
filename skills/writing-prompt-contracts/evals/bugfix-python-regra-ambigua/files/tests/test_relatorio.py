import pandas as pd
from faturamento.relatorio import gerar_relatorio


def test_um_plano_ativo_gera_uma_linha():
    benef = pd.DataFrame({"cd_beneficiario": [1], "nm_beneficiario": ["Ana"]})
    planos = pd.DataFrame({"cd_beneficiario": [1], "cd_plano": ["P1"], "vl_mensalidade": [300.0],
                           "inicio": ["2026-01"], "fim": [None]})
    rel = gerar_relatorio(benef, planos, "2026-10")
    assert len(rel) == 1

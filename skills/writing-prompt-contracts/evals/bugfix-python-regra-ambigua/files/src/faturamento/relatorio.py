import pandas as pd

COLUNAS = ["cd_beneficiario", "nm_beneficiario", "cd_plano", "vl_mensalidade", "competencia"]


def gerar_relatorio(beneficiarios: pd.DataFrame, planos: pd.DataFrame, competencia: str) -> pd.DataFrame:
    """Uma linha por beneficiário ativo na competência."""
    ativos = planos[(planos["inicio"] <= competencia) & ((planos["fim"].isna()) | (planos["fim"] >= competencia))]
    rel = beneficiarios.merge(ativos, on="cd_beneficiario", how="inner")
    rel["competencia"] = competencia
    return rel[COLUNAS]

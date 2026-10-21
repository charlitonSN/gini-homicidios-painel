"""
Verificação independente do Modelo (1) da Tabela 1 a partir dos dados brutos.

AVISO: script gerado com auxílio de Inteligência Artificial (Claude, Anthropic).

ln(homicídios) = Gini + efeito fixo de país, 2005-2017, países do World Bank,
erros padrão robustos por cluster (país).
Relatório (Stata): coef. 0,864 (EP 0,869); constante 0,620; N = 1044.

Os modelos (2) a (5) não podem ser reproduzidos com os arquivos deste repositório,
pois os dados brutos de matrícula, democracia, pobreza e gasto em educação não
foram preservados.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

BRUTOS = Path(__file__).resolve().parents[2] / "dados" / "brutos"

paises = pd.read_excel(BRUTOS / "desemprego_total.xlsx", sheet_name=0)["Country Code"].dropna().unique()
gini = pd.read_csv(BRUTOS / "gini.csv")
gini.columns = ["pais", "ano", "gini"]
cod = pd.read_csv(BRUTOS / "exp_vida.csv").iloc[:, :2].drop_duplicates()
cod.columns = ["pais", "codigo"]
gini = gini.merge(cod, on="pais", how="left")
hom = pd.read_csv(BRUTOS / "homicidios.csv")
hom.columns = ["pais", "codigo", "ano", "homicidios"]

df = hom.merge(gini[["codigo", "ano", "gini"]], on=["codigo", "ano"])
df = df[df["ano"].between(2005, 2017) & df["codigo"].isin(paises)].dropna()
df = df[df["homicidios"] > 0].copy()
df["ln_homicidio"] = np.log(df["homicidios"])
df = df.set_index(["codigo", "ano"])

res = PanelOLS.from_formula("ln_homicidio ~ 1 + gini + EntityEffects", df).fit(
    cov_type="clustered", cluster_entity=True)
print(res.summary.tables[1])
print(f"N = {res.nobs}, países = {int(res.entity_info['total'])}")

# Quanto da variação do Gini (e dos homicídios) ocorre dentro de cada país?
# Os efeitos fixos usam apenas essa variação "within".
for var in ["gini", "ln_homicidio"]:
    total = df[var].var()
    dentro = (df[var] - df.groupby(level="codigo")[var].transform("mean")).var()
    print(f"{var}: desvio padrão total = {np.sqrt(total):.3f}; "
          f"variação dentro dos países = {100 * dentro / total:.1f}% da variância total")

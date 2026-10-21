"""
Preparação dos dados — versão Python equivalente a `codigo/stata/codigos.do`.

AVISO: este arquivo foi gerado com auxílio de Inteligência Artificial (Claude, Anthropic)
a partir do do-file original em Stata, escrito pelos autores. O objetivo é oferecer uma
alternativa em Python para quem não tem Stata. A análise original do trabalho foi feita
em Stata; em caso de divergência, vale o do-file original.

O script lê os arquivos brutos (World Bank / Our World in Data) da pasta `dados/brutos/`,
converte as bases do World Bank para o formato long (país-ano), renomeia as variáveis
para português e salva cada base em `.dta` na pasta `dados/processados/`, assim como o
do-file original.

Diferenças em relação ao do-file:
  * caminhos relativos ao repositório, em vez de "C:\\trabalho_econometria";
  * na base do índice de Gini, o do-file renomeia a variável para `exp_vida` e, em
    seguida, tenta rotular `gini` (o que interrompe o Stata). Aqui ela se chama `gini`;
  * nas planilhas .xls do World Bank, as linhas de cabeçalho ("Last Updated Date",
    "Country Code", linha vazia) são descartadas antes do reshape.

Uso:
    python codigo/python/preparacao_dados.py
Requisitos: pandas, openpyxl, xlrd
"""

from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
BRUTOS = RAIZ / "dados" / "brutos"
PROCESSADOS = RAIZ / "dados" / "processados"
ANOS = list(range(2005, 2024))


def salvar(df, nome, rotulos):
    """Equivalente ao `label variable` + `save ..., replace` do Stata."""
    PROCESSADOS.mkdir(parents=True, exist_ok=True)
    df.to_stata(PROCESSADOS / f"{nome}.dta", write_index=False, variable_labels=rotulos, version=118)


# --------- LISTA DE PAISES ---------------*
def lista_paises():
    meta = pd.read_excel(BRUTOS / "crescimento_pib_percapta.xls", sheet_name="Metadata - Countries")
    paises = meta[["Country Code"]].rename(columns={"Country Code": "codigo"})
    salvar(paises, "paises", {})


# Planilhas .xls do World Bank (formato "Data Source / World Development Indicators"):
# as colunas AX a BP (posições 49 a 67) correspondem aos anos de 2005 a 2023.
def wdi_xls(arquivo, var, rotulo, nome_saida):
    bruto = pd.read_excel(BRUTOS / arquivo, sheet_name="Data", header=None)
    dados = bruto.iloc[4:, [0, 1] + list(range(49, 68))]
    dados.columns = ["pais", "codigo"] + [f"_{a}" for a in ANOS]
    longo = pd.wide_to_long(dados, stubnames="_", i="codigo", j="ano").reset_index()
    longo = longo.rename(columns={"_": var})
    longo[var] = pd.to_numeric(longo[var], errors="coerce")
    salvar(longo[["codigo", "ano", "pais", var]], nome_saida, {var: rotulo})


# Planilhas .xlsx exportadas do DataBank (colunas "2005 [YR2005]", ...).
def databank_xlsx(arquivo, var, rotulo, nome_saida):
    dados = pd.read_excel(BRUTOS / arquivo, sheet_name=0)
    dados = dados.rename(columns={"Country Code": "codigo", "Country Name": "nome_pais"})
    dados = dados[dados["codigo"].notna() & (dados["codigo"] != "")]
    dados = dados.drop(columns=["Series Name", "Series Code"])
    dados.columns = [c.split("[YR")[-1].rstrip("]") if "[YR" in str(c) else c for c in dados.columns]
    longo = dados.melt(id_vars=["codigo", "nome_pais"], var_name="ano", value_name=var)
    longo["ano"] = longo["ano"].astype(int)
    longo[var] = pd.to_numeric(longo[var], errors="coerce")  # ".." vira ausente
    salvar(longo, nome_saida, {var: rotulo})


# Arquivos .csv do Our World in Data (Entity, Code, Year, valor...).
def owid_csv(arquivo, renomear, rotulos, nome_saida):
    dados = pd.read_csv(BRUTOS / arquivo)
    dados = dados.rename(columns={"Entity": "pais", "Code": "codigo", "Year": "ano"})
    dados.columns = ["pais", "codigo", "ano"] + list(dados.columns[3:])
    dados = dados.rename(columns=dict(zip(dados.columns[3:], renomear)))
    salvar(dados, nome_saida, rotulos)


def main():
    lista_paises()

    # ========== Crescimento PIB Percapta =================*
    wdi_xls("crescimento_pib_percapta.xls", "pib_cresc",
            "Crescimento do PIB per capita anual %", "crescimento_pib_percapt")

    # ============= POPULAÇÃO PRISIONAL ===================
    # Atenção: o arquivo pop_prisional.xls baixado contém, na verdade, o indicador
    # "Unemployment, total (% of total labor force) (national estimate)". Mantido como no do-file.
    wdi_xls("pop_prisional.xls", "pop_prisional", "População prisional", "pop_prisional")

    # ============== PIB PERCAPTA CONSTANTE 2015 ==============
    databank_xlsx("pib_perc_2015.xlsx", "pib_2015", "PIB per capita US$ constante de 2015", "pib_2015")

    # ================= POPULAÇÃO URBANA ====================
    databank_xlsx("populacao_urbana.xlsx", "pop_urb", "População urbana % da população total",
                  "populacao_urbana")

    # ============== CRESCIMENTO POPULAÇÃO URBANA =================
    databank_xlsx("cresc_pop_urbana.xlsx", "pop_cresc", "Crescimento da população urbana anual %",
                  "cresc_pop_urbana")

    # ========== DENSIDADE POPULACIONAL =================*
    owid_csv("densidade_populacional_2025.csv", ["Pop_dens"],
             {"Pop_dens": "Densidade Populacional"}, "pop_dens")

    # ========== EXPECTATIVA DE VIDA =================*
    owid_csv("exp_vida.csv", ["exp_vida"], {"exp_vida": "Expectativa de vida"}, "exp_vida")

    # ========== INDICE DE GINI =================*
    # O csv do Gini não tem a coluna Code (apenas Country, Year, valor).
    gini = pd.read_csv(BRUTOS / "gini.csv")
    gini.columns = ["pais", "ano", "gini"]
    salvar(gini, "gini", {"gini": "Indice de Gini"})

    # ========== TAXA DE HOMICIOS =================*
    owid_csv("homicidios.csv", ["homicidios"], {"homicidios": "taxa de Homicidios"}, "homicidios")

    # ========== POPULAÇÃO POR IDADE =================*
    owid_csv("populacao_idade.csv",
             ["pop_mais65", "pop_25a64", "pop_15a24", "pop_5a14", "pop_0a4"],
             {"pop_mais65": "populacao com mais de 65 anos",
              "pop_25a64": "populacao de 25 a 64 anos",
              "pop_15a24": "populacao de 15 a 24 anos",
              "pop_5a14": "populacao de 5 a14 anos",
              "pop_0a4": "populacao de 0 a 4 anos"},
             "pop_idade")

    # ========== TAXA DE MORTALIDADE =================*
    owid_csv("taxa_mortalidade_infantil.csv", ["mort_inf"],
             {"mort_inf": "mortalidade infantil"}, "mort_inf")

    print(f"Bases salvas em {PROCESSADOS}")


if __name__ == "__main__":
    main()

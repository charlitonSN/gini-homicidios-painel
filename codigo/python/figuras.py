"""
Gera as figuras do relatório (pasta `figuras/`).

AVISO: script gerado com auxílio de Inteligência Artificial (Claude, Anthropic).

* Figuras 1 e 2 são descritivas e usam os dados brutos de `dados/brutos/`.
* Figuras 3 a 5 apenas visualizam os coeficientes já reportados no relatório
  (estimados em Stata pelos autores); nenhum coeficiente é reestimado aqui.
  Intervalos de 95% = coeficiente ± 1,96 × erro padrão reportado.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
BRUTOS = RAIZ / "dados" / "brutos"
FIG = RAIZ / "figuras"

SUPERFICIE = "#fcfcfb"
TEXTO = "#0b0b0b"
TEXTO_2 = "#52514e"
GRADE = "#e4e3df"
CINZA = "#b8b7b1"
REGIOES = {  # regiões do World Bank -> cor categórica fixa
    "Latin America & Caribbean": ("América Latina e Caribe", "#2a78d6"),
    "Europe & Central Asia": ("Europa e Ásia Central", "#eb6834"),
    "East Asia & Pacific": ("Ásia Oriental e Pacífico", "#1baf7a"),
}

plt.rcParams.update({
    "figure.facecolor": SUPERFICIE, "axes.facecolor": SUPERFICIE, "savefig.facecolor": SUPERFICIE,
    "axes.edgecolor": CINZA, "axes.labelcolor": TEXTO_2, "xtick.color": TEXTO_2, "ytick.color": TEXTO_2,
    "text.color": TEXTO, "font.size": 10, "axes.titlesize": 12, "axes.titleweight": "bold",
    "axes.titlelocation": "left", "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRADE, "grid.linewidth": 0.8, "axes.axisbelow": True,
    "legend.frameon": False, "figure.dpi": 150,
})


def fonte(fig, texto):
    fig.text(0.01, 0.01, texto, fontsize=8, color=TEXTO_2, ha="left", va="bottom")


def painel_bruto():
    """Painel Gini x homicídios, 2005-2017, apenas países do World Bank."""
    meta = pd.read_excel(BRUTOS / "crescimento_pib_percapta.xls", sheet_name="Metadata - Countries")
    meta = meta[meta["Region"].notna()][["Country Code", "Region"]]
    meta.columns = ["codigo", "regiao"]
    gini = pd.read_csv(BRUTOS / "gini.csv")
    gini.columns = ["pais", "ano", "gini"]
    cod = pd.read_csv(BRUTOS / "exp_vida.csv").iloc[:, :2].drop_duplicates()
    cod.columns = ["pais", "codigo"]
    gini = gini.merge(cod, on="pais", how="left")
    hom = pd.read_csv(BRUTOS / "homicidios.csv")
    hom.columns = ["pais", "codigo", "ano", "homicidios"]
    df = hom.merge(gini[["codigo", "ano", "gini"]], on=["codigo", "ano"]).merge(meta, on="codigo")
    return df[df["ano"].between(2005, 2017)].dropna(subset=["gini", "homicidios"])


def fig1_dispersao(df):
    medias = df.groupby(["codigo", "pais", "regiao"], as_index=False)[["gini", "homicidios"]].mean()
    medias = medias[medias["homicidios"] > 0]
    fig, ax = plt.subplots(figsize=(8, 5.2))
    outras = medias[~medias["regiao"].isin(REGIOES)]
    ax.scatter(outras["gini"], outras["homicidios"], s=30, color=CINZA, edgecolor=SUPERFICIE,
               linewidth=1, label="Demais regiões", zorder=2)
    for reg, (nome, cor) in REGIOES.items():
        sub = medias[medias["regiao"] == reg]
        ax.scatter(sub["gini"], sub["homicidios"], s=38, color=cor, edgecolor=SUPERFICIE,
                   linewidth=1, label=nome, zorder=3)
    for cod in ["BRA", "MEX", "ZAF", "USA", "JPN"]:
        linha = medias[medias["codigo"] == cod]
        if not linha.empty:
            r = linha.iloc[0]
            ax.annotate(r["pais"], (r["gini"], r["homicidios"]), xytext=(5, 3),
                        textcoords="offset points", fontsize=8, color=TEXTO_2)
    ax.set_yscale("log")
    ax.set_yticks([0.3, 1, 3, 10, 30])
    ax.set_yticklabels(["0,3", "1", "3", "10", "30"])
    ax.set_xlabel("Índice de Gini (antes de impostos, WID) — média 2005–2017")
    ax.set_ylabel("Homicídios por 100 mil hab. (escala log)")
    ax.set_title("Países mais desiguais tendem a ter mais homicídios")
    ax.legend(loc="upper left", fontsize=9)
    fonte(fig, f"Fonte: Our World in Data (UNODC; World Inequality Database). {len(medias)} países, regiões do World Bank.")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(FIG / "fig1_gini_homicidios_dispersao.png")
    plt.close(fig)


def fig2_tendencia(df):
    fig, ax = plt.subplots(figsize=(8, 4.6))
    for reg, (nome, cor) in REGIOES.items():
        serie = df[df["regiao"] == reg].groupby("ano")["homicidios"].median()
        ax.plot(serie.index, serie.values, color=cor, linewidth=2, label=nome)
    ax.set_xlim(2005, 2017.3)
    ax.set_xticks(range(2005, 2018, 2))
    ax.set_ylim(0)
    ax.set_ylabel("Homicídios por 100 mil hab. (mediana)")
    ax.set_title("Taxa mediana de homicídios por região, 2005–2017")
    ax.legend(loc="center left", fontsize=9, bbox_to_anchor=(0.01, 0.42))
    fonte(fig, "Fonte: Our World in Data (UNODC). Mediana entre os países de cada região do World Bank com dado no ano (a composição varia).")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(FIG / "fig2_tendencia_homicidios_regioes.png")
    plt.close(fig)


# ---- Coeficientes reportados no relatório (Tabela 1, efeitos fixos, EP cluster por país) ----
MODELOS = ["(1)", "(2)", "(3)", "(4)", "(5)"]
TABELA = {  # variável: [(coef, ep) ou None por modelo]
    "Índice de Gini": [(0.864, 0.869), (1.381, 0.810), (1.054, 0.937), (1.435, 1.170), (0.574, 1.104)],
    "ln densidade populacional": [None, (-0.789, 0.658), (-1.560, 0.656), (-0.666, 0.679), (-0.300, 0.703)],
    "Desemprego (%)": [None, (-0.006, 0.005), (0.001, 0.005), (-0.017, 0.008), None],
    "Matrícula primária (% bruta)": [None, None, (0.066, 0.018), (0.058, 0.018), (0.076, 0.018)],
    "Índice de democracia": [None, None, (-0.023, 0.089), (-0.106, 0.090), (-0.140, 0.086)],
    "ln pobreza": [None, None, None, (-0.088, 0.057), (-0.086, 0.061)],
    "ln PIB per capita": [None, None, None, (-1.274, 0.332), (-0.856, 0.295)],
    "Despesa pública em educação": [None, None, None, None, (0.004, 0.010)],
}
AZUL = "#2a78d6"


def fig3_gini_modelos():
    fig, ax = plt.subplots(figsize=(8, 4.4))
    for i, (b, se) in enumerate(TABELA["Índice de Gini"]):
        ax.plot([b - 1.96 * se, b + 1.96 * se], [i, i], color=AZUL, linewidth=2, solid_capstyle="round")
        ax.scatter([b], [i], s=60, color=AZUL, edgecolor=SUPERFICIE, linewidth=2, zorder=3)
        ax.annotate(f"{b:.3f}".replace(".", ","), (b, i), xytext=(0, 8), textcoords="offset points",
                    ha="center", fontsize=9, color=TEXTO)
    ax.axvline(0, color=TEXTO_2, linewidth=1)
    ax.set_yticks(range(5))
    ax.set_yticklabels([f"Modelo {m}" for m in MODELOS])
    ax.set_ylim(4.5, -0.8)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Efeito do Gini sobre ln(homicídios) — coeficiente e IC 95%")
    ax.set_title("Coeficiente do Gini é positivo, mas impreciso, em todos os modelos")
    fonte(fig, "Fonte: estimativas próprias (Tabela 1). IC 95% = coef. ± 1,96 × EP robusto por cluster (país).")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(FIG / "fig3_coeficiente_gini_modelos.png")
    plt.close(fig)


def fig4_todos_coeficientes():
    variaveis = [v for v in TABELA if v != "Índice de Gini"]
    fig, eixos = plt.subplots(2, 4, figsize=(11, 5.6), sharey=True)
    for ax, var in zip(eixos.flat, variaveis):
        for i, val in enumerate(TABELA[var]):
            if val is None:
                continue
            b, se = val
            ax.plot([b - 1.96 * se, b + 1.96 * se], [i, i], color=AZUL, linewidth=2, solid_capstyle="round")
            ax.scatter([b], [i], s=36, color=AZUL, edgecolor=SUPERFICIE, linewidth=1.5, zorder=3)
        ax.axvline(0, color=TEXTO_2, linewidth=1)
        ax.set_title(var, fontsize=9.5)
        ax.set_yticks(range(5))
        ax.set_yticklabels([f"Mod. {m}" for m in MODELOS])
        ax.grid(axis="y", visible=False)
        ax.tick_params(labelsize=8)
    eixos[0, 0].invert_yaxis()
    eixos[1, 3].set_visible(False)
    fig.suptitle("Controles: coeficientes e IC 95% por modelo (ausente = variável não incluída)",
                 x=0.01, ha="left", fontsize=12, fontweight="bold")
    fonte(fig, "Fonte: estimativas próprias (Tabela 1). Variável dependente: ln(homicídios por 100 mil hab.).")
    fig.tight_layout(rect=(0, 0.03, 1, 0.95))
    fig.savefig(FIG / "fig4_coeficientes_controles.png")
    plt.close(fig)


# ---- Coeficientes regionais citados no texto do relatório (sem erros padrão reportados) ----
REGIONAL = {
    "Índice de Gini": [(1.212, ""), (-0.128, ""), (6.591, "**")],
    "Educação (matrícula)": [(0.078, "**"), (0.061, "***"), (0.088, "**")],
    "ln PIB per capita": [(-0.778, "***"), (-1.251, "***"), (-1.468, "")],
    "ln densidade pop.": [(-0.516, ""), (-1.608, "**"), (-2.454, "")],
    "ln pobreza": [(0.118, "*"), (-0.071, ""), (-0.771, "**")],
}
NOMES_REG = ["Ásia-Pacífico", "Europa", "América Latina"]
CORES_REG = ["#1baf7a", "#eb6834", "#2a78d6"]


def fig5_regional():
    fig, eixos = plt.subplots(1, 5, figsize=(11, 3.6), sharey=True)
    for ax, (var, vals) in zip(eixos, REGIONAL.items()):
        for i, ((b, est), cor) in enumerate(zip(vals, CORES_REG)):
            ax.barh(i, b, height=0.6, color=cor, edgecolor=SUPERFICIE, linewidth=2)
            rotulo = f"{b:.3f}".replace(".", ",") + est
            ax.annotate(rotulo, (b, i), xytext=(4 if b >= 0 else -4, 0), textcoords="offset points",
                        ha="left" if b >= 0 else "right", va="center", fontsize=8, color=TEXTO)
        ax.axvline(0, color=TEXTO_2, linewidth=1)
        lim = max(abs(b) for b, _ in vals) * 3.6
        ax.set_xlim(-lim, lim)
        ax.set_title(var, fontsize=9.5)
        ax.set_yticks(range(3))
        ax.set_yticklabels(NOMES_REG)
        ax.grid(axis="y", visible=False)
        ax.tick_params(labelsize=8)
    eixos[0].invert_yaxis()
    fig.suptitle("Efeitos por região: a desigualdade só é significativa na América Latina",
                 x=0.01, ha="left", fontsize=12, fontweight="bold")
    fonte(fig, "Fonte: estimativas próprias (modelos regionais de efeitos fixos; erros padrão não reportados). * p<0,10; ** p<0,05; *** p<0,01.")
    fig.tight_layout(rect=(0, 0.04, 1, 0.92), w_pad=2.5)
    fig.savefig(FIG / "fig5_coeficientes_regionais.png")
    plt.close(fig)


def main():
    FIG.mkdir(exist_ok=True)
    df = painel_bruto()
    fig1_dispersao(df)
    fig2_tendencia(df)
    fig3_gini_modelos()
    fig4_todos_coeficientes()
    fig5_regional()
    print(f"Figuras salvas em {FIG}")


if __name__ == "__main__":
    main()

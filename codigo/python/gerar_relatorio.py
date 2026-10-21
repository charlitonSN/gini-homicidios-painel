"""
Gera `relatorio/relatorio.pdf`.

AVISO: script gerado com auxílio de Inteligência Artificial (Claude, Anthropic).
Todos os coeficientes, erros padrão e números de observações vêm do relatório
original (estimações em Stata). Os únicos números calculados aqui são os da
verificação independente do Modelo (1) e da decomposição da variância do Gini
(ver `verificacao_modelo1.py`).

Uso (depois de rodar `figuras.py`):
    python codigo/python/gerar_relatorio.py
"""

from pathlib import Path

import matplotlib
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, KeepTogether, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

RAIZ = Path(__file__).resolve().parents[2]
FIG = RAIZ / "figuras"
SAIDA = RAIZ / "relatorio" / "relatorio.pdf"

# Fonte com suporte a acentos e letras gregas (vem junto com o matplotlib)
TTF = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
pdfmetrics.registerFont(TTFont("DV", str(TTF / "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DV-B", str(TTF / "DejaVuSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("DV-I", str(TTF / "DejaVuSans-Oblique.ttf")))
pdfmetrics.registerFont(TTFont("DV-BI", str(TTF / "DejaVuSans-BoldOblique.ttf")))
pdfmetrics.registerFontFamily("DV", normal="DV", bold="DV-B", italic="DV-I", boldItalic="DV-BI")

AZUL = colors.HexColor("#2a78d6")
TINTA = colors.HexColor("#0b0b0b")
TINTA_2 = colors.HexColor("#52514e")
LINHA = colors.HexColor("#c9c8c2")
FUNDO = colors.HexColor("#f3f2ee")

corpo = ParagraphStyle("corpo", fontName="DV", fontSize=9.5, leading=14, alignment=TA_JUSTIFY,
                       textColor=TINTA, spaceAfter=6)
titulo = ParagraphStyle("titulo", fontName="DV-B", fontSize=17, leading=22, textColor=TINTA,
                        alignment=TA_CENTER, spaceAfter=8)
subtitulo = ParagraphStyle("sub", fontName="DV", fontSize=10, leading=14, textColor=TINTA_2,
                           alignment=TA_CENTER)
h1 = ParagraphStyle("h1", fontName="DV-B", fontSize=12.5, leading=16, textColor=AZUL,
                    spaceBefore=12, spaceAfter=6, keepWithNext=1)
h2 = ParagraphStyle("h2", fontName="DV-B", fontSize=10.5, leading=14, textColor=TINTA,
                    spaceBefore=8, spaceAfter=4, keepWithNext=1)
legenda = ParagraphStyle("leg", fontName="DV", fontSize=8, leading=11, textColor=TINTA_2,
                         spaceAfter=10)
item = ParagraphStyle("item", parent=corpo, leftIndent=12, bulletIndent=2, spaceAfter=3)
celula = ParagraphStyle("cel", fontName="DV", fontSize=8, leading=10, textColor=TINTA)
celula_c = ParagraphStyle("celc", parent=celula, alignment=TA_CENTER)
caixa = ParagraphStyle("caixa", parent=corpo, fontSize=9, leading=13, spaceAfter=0)


def P(t, s=corpo):
    return Paragraph(t, s)


def lista(itens):
    return [Paragraph(i, item, bulletText="•") for i in itens]


def figura(arquivo, largura_cm, texto):
    img = Image(str(FIG / arquivo))
    prop = img.imageHeight / img.imageWidth
    img.drawWidth, img.drawHeight = largura_cm * cm, largura_cm * cm * prop
    return KeepTogether([img, Spacer(1, 3), P(texto, legenda)])


def destaque(texto):
    t = Table([[P(texto, caixa)]], colWidths=[16.4 * cm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), FUNDO),
                           ("LINEBEFORE", (0, 0), (0, -1), 3, AZUL),
                           ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                           ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
    return t


def tabela(linhas, larguras, linhas_ep=(), cabecalho=1):
    dados = [[P(c, celula if j == 0 else celula_c) for j, c in enumerate(l)] for l in linhas]
    t = Table(dados, colWidths=[w * cm for w in larguras], repeatRows=cabecalho)
    estilo = [("LINEABOVE", (0, 0), (-1, 0), 1, TINTA), ("LINEBELOW", (0, cabecalho - 1), (-1, cabecalho - 1), 0.6, TINTA),
              ("LINEBELOW", (0, -1), (-1, -1), 1, TINTA), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
              ("TOPPADDING", (0, 0), (-1, -1), 1.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5)]
    for r in linhas_ep:
        estilo.append(("TEXTCOLOR", (0, r), (-1, r), TINTA_2))
    t.setStyle(TableStyle(estilo))
    return t


def rodape(canvas, doc):
    canvas.saveState()
    canvas.setFont("DV", 7.5)
    canvas.setFillColor(TINTA_2)
    canvas.drawString(2.2 * cm, 1.2 * cm, "Desigualdade de renda e homicídios — dados em painel, 2005–2017")
    canvas.drawRightString(A4[0] - 2.2 * cm, 1.2 * cm, f"{doc.page}")
    canvas.restoreState()


def conteudo():
    s = []
    s += [Spacer(1, 1.2 * cm),
          P("Impacto da desigualdade socioeconômica na criminalidade", titulo),
          P("Uma análise da relação entre o índice de Gini e a taxa de homicídios com dados em painel", subtitulo),
          Spacer(1, 10),
          P("Charliton da Silva Nogueira", subtitulo),
          P("Econometria I — Ciências Econômicas, Universidade Federal de Alagoas (UFAL) · 2025", subtitulo),
          Spacer(1, 16)]

    s.append(destaque(
        "<b>Resumo.</b> Investiga-se se a desigualdade de renda, medida pelo índice de Gini, está associada "
        "a taxas de homicídio mais altas. Com um painel de países (2005–2017), estimam-se cinco regressões "
        "múltiplas com efeitos fixos de país e erros padrão robustos agrupados por país, além de modelos "
        "separados para Ásia-Pacífico, Europa e América Latina. O coeficiente do Gini é positivo em todas as "
        "especificações, mas estatisticamente significativo apenas no Modelo (2), a 10%. Na análise regional, "
        "a desigualdade é significativa somente na América Latina (6,591, p &lt; 0,05). O PIB per capita "
        "apresenta associação negativa e robusta com os homicídios. Os resultados são consistentes com a "
        "literatura que encontra relação positiva entre desigualdade e violência, e com a observação de que "
        "essa relação perde precisão quando se usa apenas a variação dentro de cada país."))

    s += [P("1. Introdução", h1),
          P("A desigualdade de renda é frequentemente apontada como um determinante da criminalidade violenta. "
            "Fajnzylber, Lederman e Loayza (2002a) mostram que aumentos da desigualdade estão associados a "
            "maiores taxas de homicídio e roubo; Krahn, Hartnagel e Gartrell (1986) relacionam a desigualdade à "
            "privação relativa e às tensões sociais que ela gera. Neumayer (2005), por outro lado, ressalta que "
            "fatores culturais e institucionais específicos de cada país podem tornar essa associação espúria, "
            "e Silva e Lozano (2022) destacam a importância de diferenças regionais."),
          P("Este trabalho estima, com regressão múltipla em dados em painel, a influência da desigualdade de "
            "renda sobre a taxa de homicídios (proxy de violência letal). A hipótese central é que a "
            "desigualdade aumenta a criminalidade. As perguntas que orientam a pesquisa são: (i) existe relação "
            "estatisticamente significativa entre Gini e homicídios? (ii) quais variáveis socioeconômicas "
            "influenciam essa relação? (iii) o efeito difere entre regiões?")]

    s += [P("2. Dados", h1),
          P("A variável dependente é o logaritmo da taxa de homicídios por 100 mil habitantes (UNODC, via "
            "<i>Our World in Data</i>). A variável de interesse é o índice de Gini antes de impostos (World "
            "Inequality Database, via <i>Our World in Data</i>), em escala de 0 a 1. Os controles, com o sinal "
            "esperado segundo a literatura, são:"),
          *lista(["<b>ln densidade populacional</b> (+): maior concentração urbana facilitaria crimes "
                  "(Krahn; Hartnagel; Gartrell, 1986; Neumayer, 2005);",
                  "<b>desemprego</b>, % da força de trabalho (+): vulnerabilidade econômica (Riveros Gavilanes, 2023);",
                  "<b>matrícula no ensino primário</b>, % bruta (−): amplia oportunidades legais (Riveros Gavilanes, 2023);",
                  "<b>índice de democracia</b> (−): instituições mais sólidas (Neumayer, 2005);",
                  "<b>ln pobreza</b> (+): condições econômicas precárias (Silva; Lozano, 2022);",
                  "<b>ln PIB per capita</b>, US$ constantes de 2015 (−): desenvolvimento econômico "
                  "(Fajnzylber; Lederman; Loayza, 2002a);",
                  "<b>despesa pública em educação</b> (−) (Riveros Gavilanes, 2023)."]),
          P("Homicídios, Gini, densidade populacional e democracia vêm do <i>Our World in Data</i>; desemprego, "
            "educação, pobreza, PIB e despesa em educação vêm dos <i>World Development Indicators</i> do Banco "
            "Mundial. As bases foram convertidas para o formato longo (país-ano), unidas pelo código do país e "
            "restritas a 2005–2017. Como a base de Gini não traz o código do país, ele foi incorporado pelo "
            "nome a partir de outra base do OWID. Aplicou-se logaritmo às variáveis de alta dispersão e foram "
            "excluídas observações discrepantes (Zâmbia e Bulgária, e um valor extremo de crescimento populacional).")]

    s.append(figura("fig1_gini_homicidios_dispersao.png", 15.5,
                    "<b>Figura 1.</b> Média 2005–2017 do Gini e da taxa de homicídios por país (145 países). Na "
                    "comparação entre países, a associação positiva é visível, puxada principalmente pela "
                    "América Latina. Elaboração própria a partir dos dados brutos."))
    s.append(figura("fig2_tendencia_homicidios_regioes.png", 15.5,
                    "<b>Figura 2.</b> Taxa mediana de homicídios por região do Banco Mundial. A América Latina "
                    "apresenta níveis muito superiores aos das demais regiões ao longo de todo o período. "
                    "Elaboração própria a partir dos dados brutos."))

    s += [P("3. Estratégia empírica", h1),
          P("Estima-se, por mínimos quadrados com efeitos fixos de país, o modelo"),
          P("ln(homicídios)<sub>it</sub> = β·Gini<sub>it</sub> + X<sub>it</sub>′γ + α<sub>i</sub> + "
            "ε<sub>it</sub>", ParagraphStyle("eq", parent=corpo, alignment=TA_CENTER, fontSize=10.5)),
          P("em que α<sub>i</sub> captura características não observadas e constantes de cada país e "
            "X<sub>it</sub> reúne os controles. Os controles são adicionados progressivamente (Modelos 1 a 5) "
            "para avaliar a robustez de β. Os erros padrão são robustos e agrupados (<i>cluster</i>) por país, "
            "o que corrige heterocedasticidade e autocorrelação dentro de cada país. Também foram estimados "
            "modelos separados para Ásia-Pacífico, Europa e América Latina.")]

    linhas = [
        ["Variável", "(1)", "(2)", "(3)", "(4)", "(5)"],
        ["Índice de Gini", "0,864", "1,381*", "1,054", "1,435", "0,574"],
        ["", "(0,869)", "(0,810)", "(0,937)", "(1,170)", "(1,104)"],
        ["ln densidade populacional", "", "−0,789", "−1,560**", "−0,666", "−0,300"],
        ["", "", "(0,658)", "(0,656)", "(0,679)", "(0,703)"],
        ["Desemprego (% força de trabalho)", "", "−0,006", "0,001", "−0,017**", ""],
        ["", "", "(0,005)", "(0,005)", "(0,008)", ""],
        ["Matrícula escolar primária (% bruta)", "", "", "0,066***", "0,058***", "0,076***"],
        ["", "", "", "(0,018)", "(0,018)", "(0,018)"],
        ["Índice de democracia", "", "", "−0,023", "−0,106", "−0,140"],
        ["", "", "", "(0,089)", "(0,090)", "(0,086)"],
        ["ln pobreza", "", "", "", "−0,088", "−0,086"],
        ["", "", "", "", "(0,057)", "(0,061)"],
        ["ln PIB per capita", "", "", "", "−1,274***", "−0,856***"],
        ["", "", "", "", "(0,332)", "(0,295)"],
        ["Despesa pública em educação (% total)", "", "", "", "", "0,004"],
        ["", "", "", "", "", "(0,010)"],
        ["Constante", "0,620", "3,679", "2,685", "12,300***", "5,992"],
        ["", "(0,463)", "(2,855)", "(3,136)", "(4,424)", "(4,637)"],
        ["Observações", "1044", "874", "625", "530", "482"],
    ]
    s.append(KeepTogether([
        P("4. Resultados", h1),
        P("<b>Tabela 1.</b> Regressões com efeitos fixos de país. Variável dependente: ln(homicídios).", legenda),
        tabela(linhas, [6.4, 2, 2, 2, 2, 2], linhas_ep=range(2, 19, 2))]))
    s.append(P("Erros padrão robustos agrupados por país entre parênteses. * p &lt; 0,10; ** p &lt; 0,05; "
               "*** p &lt; 0,01. A amostra diminui à medida que controles com dados faltantes são incluídos.",
               legenda))

    s += [P("4.1 Desigualdade", h2),
          P("O coeficiente do Gini é positivo nos cinco modelos, o que está de acordo com a hipótese, mas só é "
            "significativo no Modelo (2), e apenas a 10%. Os intervalos de confiança são amplos e incluem o "
            "zero nas demais especificações (Figura 3). Como o Gini está em escala de 0 a 1, o coeficiente de "
            "1,381 do Modelo (2) indica que um aumento de 0,01 no Gini está associado a cerca de 1,4% a mais na "
            "taxa de homicídios.")]
    s.append(figura("fig3_coeficiente_gini_modelos.png", 14.5,
                    "<b>Figura 3.</b> Coeficiente do Gini e intervalo de confiança de 95% em cada modelo "
                    "(coeficiente ± 1,96 × erro padrão da Tabela 1)."))

    s += [P("4.2 Controles", h2),
          *lista([
              "<b>PIB per capita:</b> efeito negativo e significativo a 1% nos Modelos (4) e (5), o resultado "
              "mais robusto da tabela: maior desenvolvimento econômico está associado a menos homicídios.",
              "<b>Densidade populacional:</b> negativa em todos os modelos, contrária ao sinal esperado, mas "
              "significativa apenas no Modelo (3), a 5%. Pode refletir maior presença estatal e controle social "
              "em áreas mais densas (Neumayer, 2005).",
              "<b>Desemprego:</b> negativo e significativo apenas no Modelo (4), a 5%, com efeito pequeno "
              "(−0,017); a variável não entra no Modelo (5). O sinal contraria a hipótese tradicional.",
              "<b>Matrícula primária:</b> positiva e significativa a 1% nos Modelos (3) a (5), contrariando o "
              "sinal esperado, o que sugere variáveis omitidas ou endogeneidade.",
              "<b>Democracia:</b> negativa, como esperado, mas não significativa em nenhum modelo. No Modelo (5) "
              "a razão t é de cerca de 1,6, perto do limiar de 10%.",
              "<b>Pobreza e despesa em educação:</b> sem efeito estatisticamente significativo."])]
    s.append(figura("fig4_coeficientes_controles.png", 16.4,
                    "<b>Figura 4.</b> Coeficientes dos controles e intervalos de 95% por modelo (Tabela 1)."))

    s += [P("4.3 Análise regional", h2),
          P("<b>Tabela 2.</b> Coeficientes dos modelos regionais com efeitos fixos. Variável dependente: "
            "ln(homicídios).", legenda),
          tabela([["Variável", "Ásia-Pacífico", "Europa", "América Latina"],
                  ["Índice de Gini", "1,212", "−0,128", "6,591**"],
                  ["Educação (matrícula)", "0,078**", "0,061***", "0,088**"],
                  ["ln PIB per capita", "−0,778***", "−1,251***", "−1,468"],
                  ["ln densidade populacional", "−0,516", "−1,608**", "−2,454"],
                  ["ln pobreza", "0,118*", "−0,071", "−0,771**"],
                  ["R²", "0,801", "0,219", "0,311"]], [6.4, 3.3, 3.3, 3.4]),
          P("* p &lt; 0,10; ** p &lt; 0,05; *** p &lt; 0,01. Os erros padrão e o número de observações dos "
            "modelos regionais não foram registrados no relatório original.", legenda),
          P("A desigualdade só é estatisticamente significativa na América Latina, onde o coeficiente "
            "(6,591) é bem maior que o do painel completo: um aumento de 0,01 no Gini está associado a cerca "
            "de 6,6% a mais de homicídios. Na Ásia-Pacífico o sinal é positivo, mas não significativo; na "
            "Europa é praticamente nulo. O PIB per capita reduz os homicídios na Ásia-Pacífico e na Europa; "
            "na América Latina o sinal é o mesmo, mas sem significância. A densidade populacional é "
            "significativa apenas na Europa. A pobreza tem sinal positivo na Ásia-Pacífico (10%) e negativo na "
            "América Latina (5%). O ajuste é alto na Ásia-Pacífico (R² = 0,801) e modesto na Europa e na "
            "América Latina.")]
    s.append(figura("fig5_coeficientes_regionais.png", 16.4,
                    "<b>Figura 5.</b> Coeficientes dos modelos regionais (Tabela 2)."))

    s += [P("4.4 Diagnósticos", h2),
          P("Foram estimados modelos com efeitos aleatórios para o teste de Hausman, que <b>não rejeitou</b> a "
            "hipótese nula de que os coeficientes de efeitos fixos e aleatórios não diferem sistematicamente. "
            "Formalmente, esse resultado indica que o estimador de efeitos aleatórios seria consistente e mais "
            "eficiente. Optou-se por manter os efeitos fixos por serem consistentes nos dois cenários, uma "
            "escolha conservadora. Também foram feitas matrizes de correlação, testes de multicolinearidade, "
            "gráficos de resíduos, análise de observações influentes, teste RESET e teste de normalidade dos "
            "resíduos.")]

    s += [P("5. Consistência com a literatura", h1),
          P("A Tabela 3 resume, para cada resultado, os autores cujos achados o corroboram. Em seguida, os "
            "pontos são discutidos individualmente."),
          KeepTogether([
              P("<b>Tabela 3.</b> Resultados deste trabalho e literatura que os corrobora.", legenda),
              tabela([["Resultado deste trabalho", "Autores que corroboram"],
                      ["Associação positiva entre Gini e homicídios (sinal em todos os modelos; Figura 1)",
                       "Krahn, Hartnagel e Gartrell (1986); Fajnzylber, Lederman e Loayza (2002a; 2002b); "
                       "Nadanovsky e Cunha-Cruz (2009)"],
                      ["Efeito do Gini perde significância com efeitos fixos de país",
                       "Neumayer (2003; 2005); Brush (2007)"],
                      ["Efeito forte e significativo na América Latina, nulo na Europa",
                       "Silva e Lozano (2022); Enamorado et al. (2016); Nadanovsky e Cunha-Cruz (2009)"],
                      ["PIB per capita reduz homicídios", "Neumayer (2003)"]],
                     [7.6, 8.8])]),
          Spacer(1, 8),
          P("<b>Sinal do efeito.</b> O coeficiente positivo do Gini em todos os modelos concorda com Krahn, "
            "Hartnagel e Gartrell (1986), que encontram efeito positivo da desigualdade sobre homicídios em dados "
            "transnacionais, e com Fajnzylber, Lederman e Loayza (2002a; 2002b). Estes últimos, com um painel de "
            "39 países (1965–1995) e tratamento da endogeneidade da desigualdade, concluem que a desigualdade "
            "eleva as taxas de homicídio e de roubo. Nadanovsky e Cunha-Cruz (2009), comparando países da OCDE, da "
            "América do Sul e da América Central, também associam menor desigualdade a menos homicídios. A "
            "Figura 1 mostra o mesmo padrão nos dados deste trabalho: países mais desiguais têm, em média, mais "
            "homicídios."),
          P("<b>Perda de significância com efeitos fixos.</b> O resultado central deste trabalho (coeficiente "
            "positivo, mas impreciso) é corroborado por Neumayer (2003), que, em um painel de até 117 países "
            "(1980–1997) estimado com efeitos fixos, conclui que a relação positiva entre desigualdade e "
            "homicídios encontrada em muitos estudos pode ser espúria. Neumayer (2005) chega à mesma conclusão "
            "para roubos: a desigualdade só é significativa quando os efeitos específicos de cada país não são "
            "controlados. Brush (2007), com dados de condados dos Estados Unidos, encontra o mesmo contraste: "
            "a desigualdade está positivamente associada ao crime na comparação entre condados (corte "
            "transversal), mas não na variação ao longo do tempo. A explicação estatística aparece nos dados: na "
            "amostra do Modelo (1), apenas <b>3,1% da variância do Gini</b> ocorre dentro dos países ao longo do "
            "tempo (cálculo próprio a partir dos dados brutos). Os efeitos fixos descartam os outros 96,9%, o que "
            "amplia os erros padrão."),
          P("<b>Heterogeneidade regional.</b> O efeito forte e significativo na América Latina, contra a "
            "ausência de efeito na Europa, está de acordo com Silva e Lozano (2022), que comparam países "
            "latino-americanos e europeus. Enamorado et al. (2016) reforçam o resultado para a região: com dados "
            "de mais de 2.000 municípios mexicanos e variável instrumental para o Gini, mostram que o aumento da "
            "desigualdade elevou os homicídios relacionados ao narcotráfico. Nadanovsky e Cunha-Cruz (2009), em "
            "uma amostra que inclui as Américas do Sul e Central, também associam baixa desigualdade a baixas "
            "taxas de homicídio."),
          P("<b>PIB per capita.</b> A associação negativa e robusta entre renda e homicídios é corroborada por "
            "Neumayer (2003), que, com efeitos fixos de país, associa crescimento econômico e renda mais alta a "
            "menores taxas de homicídio."),
          P("<b>Resultados não corroborados.</b> Os sinais positivos da matrícula escolar e negativos da "
            "densidade populacional contrariam o esperado (Riveros Gavilanes, 2023; Krahn et al., 1986). São "
            "resultados que pedem cautela e provavelmente refletem variáveis omitidas, endogeneidade ou mudanças "
            "de amostra entre os modelos.")]

    s += [P("6. Verificação de reprodutibilidade", h1),
          P("O Modelo (1) foi reestimado de forma independente em Python, a partir dos arquivos brutos e com "
            "efeitos fixos de país, erros agrupados por país, países do Banco Mundial e o período 2005–2017. "
            "Resultado: Gini = 0,867 (EP 0,863), constante = 0,617, N = 1048, contra 0,864 (0,869), 0,620 e "
            "N = 1044 no relatório. A diferença de quatro observações é compatível com revisões das bases do "
            "<i>Our World in Data</i> entre os downloads. Os Modelos (2) a (5) não puderam ser reproduzidos "
            "porque os arquivos brutos de matrícula, democracia, pobreza e despesa em educação não foram "
            "preservados.")]

    s += [P("7. Limitações", h1),
          *lista(["O número de observações cai de 1044 para 482 entre os modelos; parte da mudança nos "
                  "coeficientes pode refletir a mudança de amostra, e não a inclusão dos controles. Pelo mesmo "
                  "motivo, critérios como AIC e BIC não são diretamente comparáveis entre os modelos.",
                  "Os efeitos fixos de país não tratam a causalidade reversa nem variáveis omitidas que mudam ao "
                  "longo do tempo. Variáveis instrumentais ou GMM dinâmico seriam extensões naturais.",
                  "A reestimação do Modelo (1) só reproduz o resultado sem efeitos fixos de ano, o que indica "
                  "que choques globais comuns a todos os países não foram controlados (ao menos nesse modelo).",
                  "Os erros padrão dos modelos regionais não foram registrados."])]

    s += [P("8. Conclusão", h1),
          P("A desigualdade de renda está positivamente associada à taxa de homicídios, mas, com efeitos fixos "
            "de país, o efeito é estimado com pouca precisão, porque o Gini varia muito pouco dentro de cada "
            "país ao longo de 13 anos. A América Latina é a exceção: lá o efeito é grande e significativo. O "
            "desenvolvimento econômico aparece como o fator mais robusto contra a violência letal. Políticas de "
            "redução da desigualdade parecem especialmente relevantes em contextos de desigualdade elevada, "
            "como o brasileiro e o latino-americano.")]

    s += [P("Referências", h1)]
    ref = ParagraphStyle("ref", parent=corpo, fontSize=8.5, leading=12, leftIndent=14, firstLineIndent=-14)
    for r in [
        "BRUSH, J. Does income inequality lead to more crime? A comparison of cross-sectional and time-series "
        "analyses of United States counties. <i>Economics Letters</i>, v. 96, n. 2, p. 264–268, 2007.",
        "ENAMORADO, T.; LÓPEZ-CALVA, L. F.; RODRÍGUEZ-CASTELÁN, C.; WINKLER, H. Income inequality and violent "
        "crime: evidence from Mexico's drug war. <i>Journal of Development Economics</i>, v. 120, p. 128–143, 2016.",
        "FAJNZYLBER, P.; LEDERMAN, D.; LOAYZA, N. What causes violent crime? <i>European Economic Review</i>, "
        "v. 46, n. 7, p. 1323–1357, 2002a.",
        "FAJNZYLBER, P.; LEDERMAN, D.; LOAYZA, N. Inequality and violent crime. <i>The Journal of Law and "
        "Economics</i>, v. 45, n. 1, p. 1–40, 2002b.",
        "KRAHN, H.; HARTNAGEL, T. F.; GARTRELL, J. W. Income inequality and homicide rates: cross-national data "
        "and criminological theories. <i>Criminology</i>, v. 24, n. 2, p. 269–295, 1986.",
        "NADANOVSKY, P.; CUNHA-CRUZ, J. The relative contribution of income inequality and imprisonment to the "
        "variation in homicide rates among Developed (OECD), South and Central American countries. <i>Social "
        "Science &amp; Medicine</i>, v. 69, n. 9, p. 1343–1350, 2009.",
        "NEUMAYER, E. Good policy can lower violent crime: evidence from a cross-national panel of homicide "
        "rates, 1980–97. <i>Journal of Peace Research</i>, v. 40, n. 6, p. 619–640, 2003.",
        "NEUMAYER, E. Inequality and violent crime: evidence from data on robbery and violent theft. "
        "<i>Journal of Peace Research</i>, v. 42, n. 1, p. 101–112, 2005.",
        "RIVEROS GAVILANES, J. M. On the empirics of violence, inequality, and income. <i>Journal of "
        "Economics &amp; Management</i>, v. 45, p. 102–136, 2023.",
        "SILVA, J.; LOZANO, E. Análisis de las tasas de homicidio, un estudio para países latinoamericanos y "
        "europeos. <i>Revista Venezolana de Economía y Ciencias Sociales</i>, v. 10, n. 1, p. 77–93, 2022.",
        "Dados: Our World in Data (ourworldindata.org); World Bank, World Development Indicators "
        "(databank.worldbank.org).",
    ]:
        s.append(P(r, ref))
    return s


def main():
    SAIDA.parent.mkdir(exist_ok=True)
    doc = SimpleDocTemplate(str(SAIDA), pagesize=A4, leftMargin=2.3 * cm, rightMargin=2.3 * cm,
                            topMargin=2 * cm, bottomMargin=2 * cm,
                            title="Impacto da desigualdade socioeconômica na criminalidade",
                            author="Charliton da Silva Nogueira")
    doc.build(conteudo(), onFirstPage=rodape, onLaterPages=rodape)
    print(f"PDF salvo em {SAIDA}")


if __name__ == "__main__":
    main()

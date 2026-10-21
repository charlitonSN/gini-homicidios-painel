# Dados

Os arquivos de dados **não estão no repositório**. Baixe-os das fontes abaixo e salve-os em `dados/brutos/` com o nome indicado, que é o nome usado pelos scripts. Os dados foram obtidos em maio de 2025; as bases podem ter sido revisadas desde então.

## Bases usadas pelos scripts

| Arquivo esperado | Variável | Fonte |
|---|---|---|
| `homicidios.csv` | Taxa de homicídios por 100 mil hab. (UNODC) | [Our World in Data](https://ourworldindata.org/grapher/homicide-rate-unodc) |
| `gini.csv` | Índice de Gini antes de impostos (World Inequality Database) | [Our World in Data — Economic Inequality](https://ourworldindata.org/economic-inequality) |
| `exp_vida.csv` | Expectativa de vida (usada também para obter o código dos países da base de Gini) | [Our World in Data](https://ourworldindata.org/life-expectancy) |
| `densidade_populacional_2025.csv` | Densidade populacional | [Our World in Data](https://ourworldindata.org/grapher/population-density) |
| `populacao_idade.csv` | População por faixa etária | [Our World in Data](https://ourworldindata.org/grapher/population-by-age-group) |
| `taxa_cresc_populacional.csv` | Taxa de crescimento populacional | [Our World in Data](https://ourworldindata.org/grapher/population-growth-rates) |
| `taxa_mortalidade_infantil.csv` | Mortalidade infantil | [Our World in Data](https://ourworldindata.org/grapher/child-mortality) |
| `urb_rural.csv` | População urbana e rural | [Our World in Data](https://ourworldindata.org/grapher/urban-and-rural-population-stacked) |
| `crescimento_pib_percapta.xls` | Crescimento do PIB per capita, % anual (NY.GDP.PCAP.KD.ZG), com a aba *Metadata - Countries* | [World Bank](https://data.worldbank.org/indicator/NY.GDP.PCAP.KD.ZG) (download em Excel) |
| `pop_prisional.xls` | Desemprego, % da força de trabalho (SL.UEM.TOTL.NE.ZS)¹ | [World Bank](https://data.worldbank.org/indicator/SL.UEM.TOTL.NE.ZS) (download em Excel) |
| `desemprego_total.xlsx` | Desemprego, % da força de trabalho (SL.UEM.TOTL.NE.ZS), 2005–2023 | [World Bank DataBank — WDI](https://databank.worldbank.org/source/world-development-indicators) |
| `pib_perc_2015.xlsx` | PIB per capita, US$ constantes de 2015 (NY.GDP.PCAP.KD), 2005–2023 | [World Bank DataBank — WDI](https://databank.worldbank.org/source/world-development-indicators) |
| `populacao_urbana.xlsx` | População urbana, % do total (SP.URB.TOTL.IN.ZS), 2005–2023 | [World Bank DataBank — WDI](https://databank.worldbank.org/source/world-development-indicators) |
| `cresc_pop_urbana.xlsx` | Crescimento da população urbana, % anual (SP.URB.GROW), 2005–2023 | [World Bank DataBank — WDI](https://databank.worldbank.org/source/world-development-indicators) |

¹ Apesar do nome, o arquivo usado no trabalho contém o indicador de desemprego.

Nos arquivos do DataBank, exporte em Excel com os países nas linhas e os anos nas colunas (formato `2005 [YR2005]`).

## Outras variáveis dos modelos 2 a 5

Também foram usadas as variáveis abaixo, mas os arquivos brutos não foram preservados:

- **Matrícula no ensino primário, % bruta**: World Bank WDI, *School enrollment, primary (% gross)*;
- **Despesa pública em educação, % do gasto total do governo**: World Bank WDI;
- **Pobreza**: World Bank WDI;
- **Índice de democracia**: [Our World in Data — Democracy](https://ourworldindata.org/democracy).

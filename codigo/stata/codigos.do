clear all

cd "C:\trabalho_econometria\dados_originais"

* ---------  LISTA DE PAISES ---------------*
import excel "crescimento_pib_percapta.xls", sheet(Metadata - Countries) firstrow clear
keep CountryCode Region
rename CountryCode codigo
keep codigo
save "C:\trabalho_econometria/paises.dta", replace


*------- PREPARANDO OS DADOS --------------*
/* Este arquivo formata os dados do WORLD BANK para o formato long, edita e renomeia as variavéis de forma a orgnizar os dados, cria outras bases de dados no fomrato dta e por fim, itera todas as bases de dados utilizadas. */




*========== Crescimento PIB Percapta =================*
import excel "crescimento_pib_percapta.xls", firstrow clear
	    	
* Manter somente as variáveis necessárias
keep DataSource WorldDevelopmentIndicators AX AY AZ BA BB BC BD BE BF BG BH BI BJ BK BL BM BN BO BP

* Renomear colunas de AX a BP para _2005 até _2023
local letras AX AY AZ BA BB BC BD BE BF BG BH BI BJ BK BL BM BN BO BP

local anos 2005 2006 2007 2008 2009 2010 2011 2012 2013 2014 2015 2016 2017 2018 2019 2020 2021 2022 2023

local i = 1
foreach letra of local letras {
    local ano : word `i' of `anos'
    rename `letra' _`ano'
    local ++i
}

* Renomear variáveis fixas
rename WorldDevelopmentIndicators codigo
rename DataSource pais

* Reestruturar para formato longo
reshape long _, i(codigo) j(ano)
rename _ pib_cresc
label variable pib_cresc "Crescimento do PIB per capita anual %"
    save "C:\trabalho_econometria/crescimento_pib_percapt.dta", replace
	
*============= POPULAÇÃO PRISIONAL ===================
clear all
import excel "C:\trabalho_econometria\dados_originais\pop_prisional.xls", firstrow sheet(Data)	

* Manter somente as variáveis necessárias
keep DataSource WorldDevelopmentIndicators AX AY AZ BA BB BC BD BE BF BG BH BI BJ BK BL BM BN BO BP

* Renomear colunas de AX a BP para _2005 até _2023
local letras AX AY AZ BA BB BC BD BE BF BG BH BI BJ BK BL BM BN BO BP

local anos 2005 2006 2007 2008 2009 2010 2011 2012 2013 2014 2015 2016 2017 2018 2019 2020 2021 2022 2023

local i = 1
foreach letra of local letras {
    local ano : word `i' of `anos'
    rename `letra' _`ano'
    local ++i
}

* Renomear variáveis fixas
rename WorldDevelopmentIndicators codigo
rename DataSource pais

* Reestruturar para formato longo
reshape long _, i(codigo) j(ano)
rename _ pop_prisional
label variable pop_prisional "População prisional"
    save "C:\trabalho_econometria/pop_prisional.dta", replace   
*============== PIB PERCAPTA CONSTANTE 2015 ==============
	import excel "pib_perc_2015.xlsx", firstrow clear
        rename 	CountryCode codigo
        rename CountryName nome_pais
        drop if codigo == ""
        drop SeriesName SeriesCode
		reshape long YR, i(codigo) j(ano)
		rename YR pib_2015
		label variable pib_2015 "PIB per capita US$ constante de 2015"
		save "C:\trabalho_econometria/pib_2015.dta", replace
*================= POPULAÇÃO URBANA ====================
import excel "populacao_urbana.xlsx", firstrow clear	
        rename 	CountryCode codigo
        rename CountryName nome_pais
        drop if codigo == ""
        drop SeriesName SeriesCode
		reshape long YR, i(codigo) j(ano)
		rename YR pop_urb
		label variable pop_urb "População urbana % da população total"
        save "C:\trabalho_econometria/populacao_urbana.dta", replace

	
*============== CRESCIMENTO POPULAÇÃO URBANA =================
import excel "cresc_pop_urbana.xlsx", firstrow clear
        rename 	CountryCode codigo
        rename CountryName nome_pais
        drop if codigo == ""
        drop SeriesName SeriesCode
		reshape long YR, i(codigo) j(ano)
		rename YR pop_cresc
		label variable pop_cresc "Crescimento da população urbana anual %"
       save "C:\trabalho_econometria/cresc_pop_urbana.dta", replace

*========== DENSIDADE POPULACIONAL =================*  
clear all
import delimited "C:\trabalho_econometria\dados_originais\densidade_populacional_2025.csv"
rename entity pais
rename code codigo
rename year ano
rename populationdensity Pop_dens
label variable Pop_dens "Densidade Populacional"
save "C:\trabalho_econometria/pop_dens.dta", replace

*========== EXPECTATIVA DE VIDA =================*
clear all
import delimited "C:\trabalho_econometria\dados_originais\exp_vida.csv"
rename entity pais
rename code codigo
rename year ano
rename periodlifeexpectancyatbirthsexto exp_vida
label variable exp_vida "Expectativa de vida"
save "C:\trabalho_econometria/exp_vida.dta", replace

*========== INDICE DE GINI =================*
clear all
import delimited "C:\trabalho_econometria\dados_originais\gini.csv"
rename country pais
rename year ano
rename ginicoefficientbeforetaxworldine exp_vida
label variable gini "Indice de Gini"
save "C:\trabalho_econometria/gini.dta", replace

*========== TAXA DE HOMICIOS =================*
clear all
import delimited "C:\trabalho_econometria\dados_originais\homicidios.csv"
rename entity pais
rename code codigo
rename year ano
rename homiciderateper100000populations homicidios
label variable homicidios "taxa de Homicidios"
save "C:\trabalho_econometria/homicidios.dta", replace


*========== POPULAÇÃO POR IDADE =================*
clear all
import delimited "C:\trabalho_econometria\dados_originais\populacao_idade.csv"

rename entity pais
rename code codigo
rename year ano
rename populationsexallage65variantesti pop_mais65
rename populationsexallage2564variantes pop_25a64
rename populationsexallage1524variantes pop_15a24
rename populationsexallage514variantest pop_5a14
rename populationsexallage04variantesti pop_0a4

label variable pop_mais65 "populacao com mais de 65 anos"
label variable pop_25a64 "populacao de 25 a 64 anos"
label variable pop_15a24 "populacao de 15 a 24 anos"
label variable pop_5a14 "populacao de 5 a14 anos"
label variable pop_0a4 "populacao de 0 a 14 anos"

save "C:\trabalho_econometria/pop_idade.dta", replace

*========== TAXA DE MORTALIDADE =================*
clear all
import delimited "C:\trabalho_econometria\dados_originais\taxa_mortalidade_infantil.csv"
rename entity pais
rename code codigo
rename year ano
rename childmortalityrate mort_inf
label variable mort_inf "mortalidade infantil"
save "C:\trabalho_econometria/mort_inf.dta", replace










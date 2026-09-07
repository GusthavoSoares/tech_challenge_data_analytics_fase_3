"""
Contrato da camada Silver. TC3.

Este módulo NÃO executa nada. Ele declara, em um só lugar:

  1. quais edições entram e como cada uma se chama;
  2. o de-para de COLUNAS (nome na Bronze -> nome canônico na Silver);
  3. o de-para de CATEGORIAS (valores que mudaram de rótulo entre edições);
  4. as correções de origem já provadas na validação da Bronze.

Quem consome (job_silver.py, testes, notebook) importa daqui. Trocar uma regra
significa mexer neste arquivo e em nenhum outro.

Referência dos achados: docs/VALIDACAO_BRONZE.md
"""

# --------------------------------------------------------------------------- #
# 1. EDIÇÕES
# --------------------------------------------------------------------------- #
# A convenção da fonte é `ano_da_coleta` + `ano_seguinte`, e a coleta acontece
# sempre no último trimestre. `ano_pesquisa` é o ano da COLETA: é ele que
# entra no fato e é ele que particiona a Silver.

EDICOES = {
    2023: {
        "edicao": "2023-2024",
        "tabela_bronze": "bronze_dw_state_data_2023_2024",
        "col_chave": "id",
        "col_data_envio": None,          # a edição 2023-2024 não tem data de envio
        "col_uf_moradia": None,          # derivada de `estado`
        "col_layoff": "empresa_trabalha_passou_layoff_2023",
        "linhas_esperadas": 5293,
        "colunas_esperadas": 399,
    },
    2024: {
        "edicao": "2024-2025",
        "tabela_bronze": "bronze_dw_state_data_2024_2025",
        "col_chave": "token_user",
        "col_data_envio": "data_hora_envio",
        "col_uf_moradia": "uf",          # em 2024 `uf` é onde MORA
        "col_layoff": "layoff_2024",
        "linhas_esperadas": 5217,
        "colunas_esperadas": 403,
    },
    2025: {
        "edicao": "2025-2026",
        "tabela_bronze": "bronze_dw_state_data_2025_2026",
        "col_chave": "token_user",
        "col_data_envio": "data_hora_envio",
        "col_uf_moradia": "uf_moradia",  # ATENÇÃO: em 2025 `uf` é onde NASCEU
        "col_layoff": "layoff_2025",
        "linhas_esperadas": 3495,
        "colunas_esperadas": 388,
    },
}

FORMATO_DATA_ENVIO = "dd/MM/yyyy_HH:mm:ss"   # ex.: 16/10/2024_11:19:17

# --------------------------------------------------------------------------- #
# 2. DE-PARA DE COLUNAS  (canônico -> nome na Bronze, por edição)
# --------------------------------------------------------------------------- #
# None = a coluna não existe naquela edição. O job materializa NULL e a marca
# como "não comparável" no dicionário de cobertura: nunca como 0 ou vazio.
#
# ⚠️ `uf` NÃO aparece aqui de propósito: ele muda de significado entre edições
#    (ver docs/VALIDACAO_BRONZE.md, achado #3). A sigla é sempre derivada de
#    `estado` / `estado_origem`, que são estáveis nas três.

DE_PARA_COLUNAS = {
    # --- identificação -----------------------------------------------------
    "id_origem":            {2023: "id",           2024: "token_user", 2025: "token_user"},
    "data_envio":           {2023: None,           2024: "data_hora_envio", 2025: "data_hora_envio"},

    # --- demografia --------------------------------------------------------
    "idade":                {2023: "idade",        2024: "idade",        2025: "idade"},
    "faixa_etaria":         {2023: "faixa_etaria", 2024: "faixa_etaria", 2025: "faixa_etaria"},
    "genero":               {2023: "genero",       2024: "genero",       2025: "genero"},
    "cor_raca_etnia":       {2023: "cor_raca_etnia", 2024: "cor_raca_etnia", 2025: "cor_raca_etnia"},
    "pcd":                  {2023: "pcd",          2024: "pcd",          2025: "pcd"},
    "vive_brasil":          {2023: "vive_brasil",  2024: "vive_brasil",  2025: "vive_brasil"},

    # --- localização -------------------------------------------------------
    "estado_moradia":       {2023: "estado",        2024: "estado",        2025: "estado"},
    "regiao_moradia":       {2023: "regiao",        2024: "regiao",        2025: "regiao"},
    "estado_origem":        {2023: None,            2024: "estado_origem", 2025: "estado_origem"},
    "regiao_origem":        {2023: "regiao_origem", 2024: "regiao_origem", 2025: "regiao_origem"},

    # --- formação ----------------------------------------------------------
    "nivel_ensino":         {2023: "nvl_ensino",   2024: "nvl_ensino",   2025: "nvl_ensino"},
    "area_formacao":        {2023: "area_formacao", 2024: "area_formacao", 2025: "area_formacao"},

    # --- carreira ----------------------------------------------------------
    "cargo_atual":          {2023: "cargo_atual",  2024: "cargo_atual",  2025: "cargo_atual"},
    "nivel_senioridade":    {2023: "nvl",          2024: "nvl",          2025: "nvl"},
    "eh_gestor":            {2023: "gestor",       2024: "gestor",       2025: "gestor"},
    "tempo_exp_dados":      {2023: "tempo_exp_dados", 2024: "tempo_exp_dados", 2025: "tempo_exp_dados"},
    "tempo_exp_ti":         {2023: "tempo_exp_ti", 2024: "tempo_exp_ti", 2025: "tempo_exp_ti"},
    "setor_empresa":        {2023: "setor",        2024: "setor",        2025: "setor"},
    "forma_trabalho":       {2023: "forma_trabalho", 2024: "forma_trabalho", 2025: "forma_trabalho"},
    "faixa_salarial":       {2023: "faixa_salarial", 2024: "faixa_salarial", 2025: "faixa_salarial"},

    # --- maturidade de dados e IA -----------------------------------------
    "empresa_possui_datalake": {2023: "empresa_possui_datalake", 2024: "empresa_possui_datalake", 2025: "empresa_possui_datalake"},
    "empresa_possui_dw":       {2023: "empresa_possui_dw",       2024: "empresa_possui_dw",       2025: "empresa_possui_dw"},
    "ia_gen_prioridade":       {2023: "ia_gen_eh_prioridade_empresa", 2024: "ia_gen_eh_prioridade_empresa", 2025: "ia_gen_eh_prioridade_empresa"},
    "empresa_passou_layoff":   {2023: "empresa_trabalha_passou_layoff_2023", 2024: "layoff_2024", 2025: "layoff_2025"},
    "llms_bom_resultado":      {2023: None,        2024: None,           2025: "llms_bom_resultado"},

    # --- preferências de tecnologia (resposta única) -----------------------
    "linguagem_preferida":  {2023: "linguagem_preferida", 2024: "linguagem_preferida", 2025: "linguagem_preferida"},
    "cloud_preferida":      {2023: "cloud_preferida",     2024: "cloud_preferida",     2025: "cloud_preferida"},
    "ferramenta_bi_diaria": {2023: "ferramenta_bi_diaria", 2024: "ferramenta_bi_diaria", 2025: "ferramenta_bi_diaria"},

    # --- booleanas soltas (não são múltipla escolha) -----------------------
    "mudou_estado":         {2023: "mudou_estado", 2024: None, 2025: None},
    "satisfeito_empresa":   {2023: "satisfacao_empresa_atual", 2024: "satisfacao_empresa_atual", 2025: "satisfacao_empresa_atual"},
}

# Colunas booleanas: viram BooleanType na Silver.
COLUNAS_BOOLEANAS = [
    "vive_brasil",
    "eh_gestor",
    "empresa_possui_datalake",
    "empresa_possui_dw",
    "mudou_estado",
    "satisfeito_empresa",
]

# ⚠️ `empresa_passou_layoff` NÃO é booleana, apesar do nome sugerir. São três
# respostas: não houve / houve mas não me afetou / houve e fui afetado. Os
# rótulos são idênticos nas três edições, então harmoniza sem de-para. O job
# deriva dois flags a partir dela (ver LAYOFF_HOUVE / LAYOFF_AFETADO).
LAYOFF_HOUVE = {
    "Nao_ocorreram_layoffs/demissoes_em_massa_na_empresa_em_que_trabalho": False,
    "Sim,_ocorreram_layoffs/demissoes_em_massa_na_empresa_em_que_trabalho_mas_nao_fui_afetado": True,
    "Sim,_ocorreram_layoffs/demissoes_em_massa_na_empresa_em_que_trabalhava_e_eu_fui_afetado": True,
}
LAYOFF_AFETADO = {
    "Nao_ocorreram_layoffs/demissoes_em_massa_na_empresa_em_que_trabalho": False,
    "Sim,_ocorreram_layoffs/demissoes_em_massa_na_empresa_em_que_trabalho_mas_nao_fui_afetado": False,
    "Sim,_ocorreram_layoffs/demissoes_em_massa_na_empresa_em_que_trabalhava_e_eu_fui_afetado": True,
}

# ⚠️ Achado #2 da validação: em 2024 seis colunas vêm como "TRUE"/"FALSE"
# enquanto em 2023 e 2025 as mesmas colunas vêm como "0"/"1". Um union ingênuo
# mantém as duas grafias e qualquer filtro `= '1'` descarta a edição inteira.
MAPA_BOOLEANO = {
    "1": True,  "0": False,
    "TRUE": True, "FALSE": False,
    "true": True, "false": False,
    "True": True, "False": False,
    "Sim": True, "Nao": False, "Não": False,
}

# --------------------------------------------------------------------------- #
# 2b. MÚLTIPLA ESCOLHA: as ~320 colunas binárias
# --------------------------------------------------------------------------- #
# Cada pergunta de múltipla escolha vira uma coluna por opção na origem. A
# Silver consolida cada grupo em DUAS colunas:
#
#     <grupo>       string, opções marcadas separadas por ", "
#     qtd_<grupo>   inteiro, quantas foram marcadas
#
# Assim as ~400 colunas da Bronze viram ~30 de resposta única + 17 grupos, que
# é o "consolidar para ~20" que o grupo combinou, sem perder informação:
# `WHERE linguagens LIKE '%python%'` responde tão bem quanto a coluna binária,
# e a Gold explode em bridge quando alguma pergunta precisar do grão de opção.
#
# A lista de colunas por grupo vive em grupos_multipla_escolha.py: ali está
# documentado como cada grupo foi derivado e o que falta confirmar com o
# de-para do Alexandre.
from grupos_multipla_escolha import GRUPOS_MULTIPLA_ESCOLHA  # noqa: E402,F401

SEPARADOR_MULTIPLA_ESCOLHA = ", "

# Grupos que não existem nas três edições: não podem virar série temporal.
GRUPOS_NAO_COMPARAVEIS = {
    "motivos_insatisfacao_2023": [2023],
    "fatores_emprego_atual": [2024, 2025],
}

# --------------------------------------------------------------------------- #
# 3. DE-PARA DE CATEGORIAS
# --------------------------------------------------------------------------- #
# Correções de digitação na origem, provadas célula a célula na validação.
CORRECOES_ORIGEM = {
    "faixa_salarial": {
        # 2023, 1 registro: falta o "1." dos milhares
        "de_R$_101/mes_a_R$_2.000/mes": "de_R$_1.001/mes_a_R$_2.000/mes",
        # 2025, 1 registro: "3000" onde as demais linhas dizem "30.000"
        "de_R$_25.001/mes_a_R$_3000/mes": "de_R$_25.001/mes_a_R$_30.000/mes",
    },
}

# Rótulos que mudaram entre edições e descrevem o MESMO conceito.
# Só entra aqui o que foi conferido contra as duas edições.
DE_PARA_CATEGORIAS = {
    # A pesquisa reescreveu o parêntese desta opção entre 2023-2024 e as
    # seguintes: mesma resposta, texto diferente. Sem o de-para vira duas
    # categorias e a série de prioridade de IA quebra no meio.
    "ia_gen_prioridade": {
        "Mais_ou_menos..._E_uma_das_varias_iniciativas_que_estamos_impulsionando,"
        "_mas_nao_e_uma_prioridade_(iniciativas_isoladas_e_pouco_foco).":
            "Mais_ou_menos..._E_uma_das_varias_iniciativas_que_estamos_impulsionando,"
            "_mas_nao_e_uma_prioridade_(tratam-se_de_iniciativas_isoladas_e_com_pouco_foco).",
    },
    # `area_formacao` reescreveu duas opções entre 2023-2024 e as seguintes.
    # Conferido pelo volume, que é compatível:
    #   Outras_Engenharias .............. 1.078 (2023) x 1.062 / 678 (2024/25)
    #   Marketing + Ciencias_Sociais .....  214 (2023) x   181 / 126 (2024/25)
    # No segundo caso a pesquisa FUNDIU duas categorias de 2023 numa só, então
    # as duas de 2023 apontam para a fundida. Sem isso a série de formação
    # quebra em 2024 e "Ciências Sociais" some do nada.
    "area_formacao": {
        "Outras_Engenharias":
            "Outras_Engenharias_(nao_incluir_engenharia_de_software_ou_TI)",
        "Marketing_/_Publicidade_/_Comunicacao_/_Jornalismo":
            "Marketing_/_Publicidade_/_Comunicacao_/_Jornalismo_/_Ciencias_Sociais",
        "Ciencias_Sociais":
            "Marketing_/_Publicidade_/_Comunicacao_/_Jornalismo_/_Ciencias_Sociais",
    },
    "cargo_atual": {
        # Em 2023 engenheiro e arquiteto eram uma opção só; a partir de 2024 a
        # pesquisa separou as duas. Mantemos os rótulos de 2024/2025 como
        # canônicos e sinalizamos que 2023 não é comparável no nível "arquiteto".
        "Engenheiro_de_Dados/Arquiteto_de_Dados/Data_Engineer/Data_Architect":
            "Engenheiro_de_Dados/Data_Engineer/Data_Architect",
    },
}

# Categorias que existem em uma edição e não nas outras. Vão para o dicionário
# de cobertura e NÃO podem virar série temporal sem ressalva na apresentação.
CATEGORIAS_NAO_COMPARAVEIS = {
    "nivel_senioridade": {"Especialista/Staff+": [2025]},
    "cargo_atual": {
        "Arquiteto_de_Dados/Data_Architect": [2024, 2025],
        "Analista_de_Inteligencia_de_Mercado/Market_Intelligence": [2023],
        "DBA/Administrador_de_Banco_de_Dados": [2023],
        "Economista": [2023],
    },
    "area_formacao": {
        "Ciencia_de_Dados_/_Inteligencia_Artificial": [2025],
    },
    # 2023 oferecia "de_4_a_6_anos" E "de_5_a_6_anos"; 2024/2025 só a segunda.
    # Somar as duas em 2023 para comparar com as outras edições distorce.
    "tempo_exp_dados": {"de_4_a_6_anos": [2023]},
}

# --------------------------------------------------------------------------- #
# 4. FAIXA SALARIAL -> VALOR NUMÉRICO
# --------------------------------------------------------------------------- #
# O ponto médio da faixa, para permitir média/mediana na Gold. A faixa aberta
# do topo usa o limite inferior (40.001): subestima, e é o viés conservador.
# Reportar sempre junto da faixa original, nunca sozinho.
PONTO_MEDIO_SALARIAL = {
    "Menos_de_R$_1.000/mes":              500.0,
    "de_R$_1.001/mes_a_R$_2.000/mes":    1500.5,
    "de_R$_2.001/mes_a_R$_3.000/mes":    2500.5,
    "de_R$_3.001/mes_a_R$_4.000/mes":    3500.5,
    "de_R$_4.001/mes_a_R$_6.000/mes":    5000.5,
    "de_R$_6.001/mes_a_R$_8.000/mes":    7000.5,
    "de_R$_8.001/mes_a_R$_12.000/mes":  10000.5,
    "de_R$_12.001/mes_a_R$_16.000/mes": 14000.5,
    "de_R$_16.001/mes_a_R$_20.000/mes": 18000.5,
    "de_R$_20.001/mes_a_R$_25.000/mes": 22500.5,
    "de_R$_25.001/mes_a_R$_30.000/mes": 27500.5,
    "de_R$_30.001/mes_a_R$_40.000/mes": 35000.5,
    "Acima_de_R$_40.001/mes":           40001.0,
}

# Ordem das faixas, para eixo de gráfico e ordenação na Gold.
ORDEM_FAIXA_SALARIAL = list(PONTO_MEDIO_SALARIAL.keys())

ORDEM_SENIORIDADE = ["Junior", "Pleno", "Senior", "Especialista/Staff+"]

ORDEM_TEMPO_EXP_DADOS = [
    "Nao_tenho_experiencia_na_area_de_dados",
    "Menos_de_1_ano",
    "de_1_a_2_anos",
    "de_3_a_4_anos",
    "de_4_a_6_anos",     # só 2023, ver CATEGORIAS_NAO_COMPARAVEIS
    "de_5_a_6_anos",
    "de_7_a_10_anos",
    "Mais_de_10_anos",
]

# --------------------------------------------------------------------------- #
# 5. UF -> REGIÃO  (para derivar e conferir, não para substituir a origem)
# --------------------------------------------------------------------------- #
UF_PARA_REGIAO = {
    "AC": "Norte", "AP": "Norte", "AM": "Norte", "PA": "Norte",
    "RO": "Norte", "RR": "Norte", "TO": "Norte",
    "AL": "Nordeste", "BA": "Nordeste", "CE": "Nordeste", "MA": "Nordeste",
    "PB": "Nordeste", "PE": "Nordeste", "PI": "Nordeste", "RN": "Nordeste",
    "SE": "Nordeste",
    "DF": "Centro-oeste", "GO": "Centro-oeste", "MT": "Centro-oeste",
    "MS": "Centro-oeste",
    "ES": "Sudeste", "MG": "Sudeste", "RJ": "Sudeste", "SP": "Sudeste",
    "PR": "Sul", "RS": "Sul", "SC": "Sul",
}

# --------------------------------------------------------------------------- #
# 6. CAMINHOS
# --------------------------------------------------------------------------- #
import os
import sys


def parametro(nome: str, padrao: str) -> str:
    """
    Lê uma configuração, nesta ordem de precedência:

      1. argumento de linha de comando `--NOME valor` (ou `--NOME=valor`);
      2. variável de ambiente `NOME`;
      3. o padrão.

    O passo 1 existe porque o Glue **não** transforma "Job parameter" em
    variável de ambiente: ele entrega em `sys.argv`. Sem ler o argv, um job
    configurado com `--TC3_BUCKET` cairia no padrão e escreveria no bucket
    errado, sem erro nenhum aparente.

    Não usa `awsglue.utils.getResolvedOptions` de propósito: aquele módulo só
    existe dentro do Glue, e importar quebraria a execução local. Ler as duas
    fontes aqui é o que mantém a promessa de um arquivo só, sem `if nuvem`.
    """
    chave = f"--{nome}"
    for i, arg in enumerate(sys.argv):
        if arg == chave and i + 1 < len(sys.argv):
            return sys.argv[i + 1]
        if arg.startswith(chave + "="):
            return arg.split("=", 1)[1]
    return os.getenv(nome, padrao)


BUCKET = parametro("TC3_BUCKET", "s3://tc3-datalake")

# Job parameter no Glue, variável de ambiente na máquina: o mesmo job roda nos
# dois lugares sem branch no código.
PATH_BRONZE = parametro("TC3_PATH_BRONZE", f"{BUCKET}/bronze/state_data")
PATH_SILVER = parametro("TC3_PATH_SILVER", f"{BUCKET}/silver/state_data")
DATABASE_GLUE = "state_of_data"
TABELA_SILVER = "silver_dw_fat_respondente"
PARTICAO_SILVER = "ano_pesquisa"


# --------------------------------------------------------------------------- #
# 2c. RÓTULO CANÔNICO DAS OPÇÕES DE MÚLTIPLA ESCOLHA
# --------------------------------------------------------------------------- #
# A consolidação usa o NOME DA COLUNA de origem como rótulo da opção: e esse
# nome muda entre edições para o mesmo conceito:
#
#     2023: remuneracao_salario      2024/25: remuneracao_salario_1
#     2023: img_1                    2024/25: img_fonte
#     2023: alteryx                  2024/25: alteryx_analista
#
# Sem canonizar, `linguagens LIKE '%remuneracao_salario%'` acha 2023 e devolve
# ZERO em 2025: sem erro, sem nulo. Foi assim que a tabela de fatores de
# retenção saiu 81% em 2023 e 0% em 2025.
#
# ⚠️ MAS a normalização não pode ser cega: dentro da MESMA edição, `img` e
# `img_1` são DUAS perguntas distintas (conferido: batem em 90%, não 100%).
# Colapsar as duas para ganhar comparabilidade entre anos estraga o dado
# dentro do ano: troca um erro por outro pior.
#
# Por isso o canônico é aplicado por grupo, e SÓ quando não gera colisão
# naquela edição. Onde colide, os rótulos ficam como estão e o grupo é marcado
# em GRUPOS_ROTULO_NAO_HARMONIZADO: comparação temporal dele precisa do
# de-para do Alexandre.

SUFIXOS_CANONICOS = [
    "_tmp_gasto_cientista", "_analista_dados", "_fonte",
    "_analista", "_cientista", "_1", "_2", "_3",
]
PREFIXOS_CANONICOS = ["engenheiro_dados_", "construcao_"]

# Renomeações semânticas da própria pesquisa: a regra de sufixo não pega.
ROTULO_MANUAL = {
    "colaboradores_uso_ia_descentra_independ": "ia_llm_empresa_descentralizada_independente",
    "direcionamento_centralizado_ia_generativa": "ia_llm_empresa_uso_centralizado",
    "dev_usando_copilot": "ia_llm_empresa_uso_copilot",
    "ia_gen_llm_melhorar_prod_int_colaboradores": "ia_llm_empresa_prod_interno",
    "ia_gen_llm_principal_frente_neg": "ia_llm_empresa_frente_negoc",
    "ia_llm_nao_prioridade": "ia_llm_empresa_nao_prioridade",
    "sem_opiniao_llm_ia_generativa": "ia_llm_empresa_sem_opiniao",
    "talent": "talend",
    "script_python": "python",
    "sql_stored_procedures": "stored_procedures",
    "relatorios_sql_exportados": "extracao_rel_sql",
    "exportacao_rel_para_area_neg": "exportacao_rel_area_neg",
    "nenhuma_opcao_engenheiro_dados": "nenhuma_das_opcoes",
    "nenhuma_das_opcoes_tmp_gasto": "nenhuma_das_opcoes",
    "nenhuma_opcao_listada_atv": "nenhuma_das_opcoes",
    "nao_utilizo_ferramentas_etl": "sem_ferramenta_etl",
    "engenheiro_dados_sem_ferramenta_etl": "sem_ferramenta_etl",
    "ad_hoc_hipoteses": "uso_adhoc_modelo_preditivo",
    "dashboards_ferramenta_bi": "dashboard_ferramentas_bi",
    "dashboard_ferramenta_bi": "dashboard_ferramentas_bi",
    "ferramenta_avancadas_estatistica": "ferramentas_avanc_estatistica",
}


def _canonizar(nome):
    x = nome.lower().replace("georefenciados", "georeferenciados")
    mudou = True
    while mudou:
        mudou = False
        for p in PREFIXOS_CANONICOS:
            if x.startswith(p) and len(x) > len(p):
                x, mudou = x[len(p):], True
        for s in SUFIXOS_CANONICOS:
            if x.endswith(s) and len(x) > len(s):
                x, mudou = x[:-len(s)], True
    return ROTULO_MANUAL.get(x, x)


def _construir_rotulos():
    """
    {grupo: {ano: {coluna_origem: rótulo}}}. Só onde o canônico é injetivo
    dentro da edição. Devolve também os grupos que ficaram sem harmonizar.
    """
    rotulos, nao_harmonizados = {}, []
    for grupo, por_ano in GRUPOS_MULTIPLA_ESCOLHA.items():
        colide = False
        candidato = {}
        for ano, colunas in por_ano.items():
            mapa = {c: _canonizar(c) for c in colunas}
            if len(set(mapa.values())) != len(mapa):   # dois nomes -> um rótulo
                colide = True
                break
            candidato[ano] = mapa
        if colide:
            nao_harmonizados.append(grupo)
            rotulos[grupo] = {a: {c: c for c in cs} for a, cs in por_ano.items()}
        else:
            rotulos[grupo] = candidato
    return rotulos, sorted(nao_harmonizados)


ROTULOS_MULTIPLA_ESCOLHA, GRUPOS_ROTULO_NAO_HARMONIZADO = _construir_rotulos()


# --------------------------------------------------------------------------- #
# 2d. CAMPOS MULTIVALORADOS EM TEXTO
# --------------------------------------------------------------------------- #
# Três colunas parecem resposta única pelo nome e NÃO são: a pessoa marca mais
# de uma opção e a origem concatena numa string só.
#
#     linguagem_preferida  ->  "Python,_SQL"   e também  "SQL,_Python"
#     ferramenta_bi_diaria ->  1.422 strings distintas, 1.031 aparecendo 1x
#
# Duas armadilhas juntas:
#   1. a ORDEM varia, então "Python,_SQL" e "SQL,_Python" viram categorias
#      diferentes num GROUP BY: a mesma resposta contada duas vezes;
#   2. o separador real é `,_` (vírgula + underscore, porque o ETL trocou
#      espaço por underscore), então um split ingênuo por vírgula produz
#      `_SQL` e `SQL` como opções distintas.
#
# A Silver normaliza para o mesmo formato dos 17 grupos: opções separadas por
# ", ", ordenadas: e cria a coluna `qtd_`. Assim `marcou()` funciona igual.
COLUNAS_MULTIVALORADAS_TEXTO = [
    "linguagem_preferida",
    "cloud_preferida",
    "ferramenta_bi_diaria",
]

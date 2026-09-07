"""
Rótulos de exibição e ordenação das dimensões da Gold.

A Silver guarda os valores como vieram da origem: `pbi`, `postgre_sql`,
`Modelo_100%_remoto`, `Engenheiro_de_Dados/Data_Engineer/Data_Architect`.
Isso é correto para a Silver, ela é fiel ao dado. Mas é ilegível num eixo de
gráfico.

A Gold é a camada de apresentação. Aqui os valores ganham rótulo humano e,
onde a ordem importa (senioridade, faixa salarial, tempo de experiência), uma
coluna `ordem`, sem ela o Power BI ordena alfabeticamente e "Júnior" aparece
depois de "Especialista".

Regra: o rótulo NUNCA substitui o valor original no fato. As dimensões carregam
os dois: `valor` (chave de junção, igual à Silver) e `rotulo` (o que aparece).
Assim dá para conferir contra a Silver a qualquer momento.
"""

# --------------------------------------------------------------------------- #
# ordenações: o que o Power BI usa em SortByColumn
# --------------------------------------------------------------------------- #

ORDEM_SENIORIDADE = ["Junior", "Pleno", "Senior", "Especialista/Staff+"]

ORDEM_TEMPO_EXPERIENCIA = [
    "Nao_tenho_experiencia_na_area_de_dados", "Menos_de_1_ano", "de_1_a_2_anos",
    "de_3_a_4_anos", "de_4_a_6_anos", "de_5_a_6_anos", "de_7_a_10_anos",
    "Mais_de_10_anos",
]

ORDEM_ENSINO = [
    "Nao_tenho_graduacao_formal", "Estudante_de_Graduacao", "Graduacao/Bacharelado",
    "Pos-graduacao", "Mestrado", "Doutorado_ou_Phd", "Prefiro_nao_informar",
]

ORDEM_FAIXA_ETARIA = ["17-21", "22-24", "25-29", "30-34", "35-39", "40-44",
                      "45-49", "50-54", "55+"]

# --------------------------------------------------------------------------- #
# rótulos
# --------------------------------------------------------------------------- #

ROTULO_SENIORIDADE = {
    "Junior": "Júnior", "Pleno": "Pleno", "Senior": "Sênior",
    "Especialista/Staff+": "Especialista / Staff+",
}

ROTULO_MODELO_TRABALHO = {
    "Modelo_100%_remoto": "100% remoto",
    "Modelo_100%_presencial": "100% presencial",
    "Modelo_hibrido_com_dias_fixos_de_trabalho_presencial": "Híbrido com dias fixos",
    "Modelo_hibrido_flexivel_(o_funcionario_tem_liberdade_para_escolher_quando"
    "_estar_no_escritorio_presencialmente)": "Híbrido flexível",
}

ROTULO_CARGO = {
    "Analista_de_Dados/Data_Analyst": "Analista de Dados",
    "Cientista_de_Dados/Data_Scientist": "Cientista de Dados",
    "Engenheiro_de_Dados/Data_Engineer/Data_Architect": "Engenheiro de Dados",
    "Engenheiro_de_Dados/Arquiteto_de_Dados/Data_Engineer/Data_Architect": "Engenheiro de Dados",
    "Arquiteto_de_Dados/Data_Architect": "Arquiteto de Dados",
    "Analista_de_BI/BI_Analyst": "Analista de BI",
    "Analytics_Engineer": "Analytics Engineer",
    "Analista_de_Negocios/Business_Analyst": "Analista de Negócios",
    "Engenheiro_de_Machine_Learning/ML_Engineer/AI_Engineer": "Engenheiro de ML / IA",
    "Data_Product_Manager/_Product_Manager_(PM/APM/DPM/GPM/PO)": "Product Manager de Dados",
    "Desenvolvedor/_Engenheiro_de_Software/_Analista_de_Sistemas": "Desenvolvedor / Eng. de Software",
    "Analista_de_Suporte/Analista_Tecnico": "Analista de Suporte",
    "Analista_de_Inteligencia_de_Mercado/Market_Intelligence": "Analista de Market Intelligence",
    "DBA/Administrador_de_Banco_de_Dados": "DBA",
    "Outras_Engenharias_(nao_inclui_dev)": "Outras Engenharias",
    "Professor/Pesquisador": "Professor / Pesquisador",
    "Estatistico": "Estatístico",
    "Economista": "Economista",
    "Outra_Opcao": "Outros",
}

# Agrupamento de cargo: para o gráfico que não cabe 18 categorias.
FAMILIA_CARGO = {
    "Analista de Dados": "Análise", "Analista de BI": "Análise",
    "Analista de Negócios": "Análise", "Analista de Market Intelligence": "Análise",
    "Analista de Suporte": "Análise",
    "Cientista de Dados": "Ciência de Dados", "Estatístico": "Ciência de Dados",
    "Engenheiro de Dados": "Engenharia", "Arquiteto de Dados": "Engenharia",
    "Analytics Engineer": "Engenharia", "DBA": "Engenharia",
    "Engenheiro de ML / IA": "Machine Learning / IA",
    "Product Manager de Dados": "Produto e Gestão",
    "Desenvolvedor / Eng. de Software": "Engenharia de Software",
    "Outras Engenharias": "Engenharia de Software",
    "Professor / Pesquisador": "Academia", "Economista": "Outros", "Outros": "Outros",
}

ROTULO_ENSINO = {
    "Nao_tenho_graduacao_formal": "Sem graduação formal",
    "Estudante_de_Graduacao": "Estudante de graduação",
    "Graduacao/Bacharelado": "Graduação",
    "Pos-graduacao": "Pós-graduação",
    "Mestrado": "Mestrado",
    "Doutorado_ou_Phd": "Doutorado / PhD",
    "Prefiro_nao_informar": "Prefere não informar",
}

ROTULO_TEMPO_EXPERIENCIA = {
    "Nao_tenho_experiencia_na_area_de_dados": "Sem experiência na área",
    "Menos_de_1_ano": "Menos de 1 ano", "de_1_a_2_anos": "1 a 2 anos",
    "de_3_a_4_anos": "3 a 4 anos", "de_4_a_6_anos": "4 a 6 anos",
    "de_5_a_6_anos": "5 a 6 anos", "de_7_a_10_anos": "7 a 10 anos",
    "Mais_de_10_anos": "Mais de 10 anos",
}

ROTULO_GENERO = {
    "Masculino": "Masculino", "Feminino": "Feminino",
    "Outro": "Outro", "Prefiro_nao_informar": "Prefere não informar",
}

# Faixa salarial: rótulo curto para caber no eixo, mais os limites numéricos.
FAIXA_SALARIAL = {
    "Menos_de_R$_1.000/mes":              ("até R$ 1.000",      0,      1000,   500.0),
    "de_R$_1.001/mes_a_R$_2.000/mes":     ("R$ 1–2 mil",     1001,      2000,  1500.5),
    "de_R$_2.001/mes_a_R$_3.000/mes":     ("R$ 2–3 mil",     2001,      3000,  2500.5),
    "de_R$_3.001/mes_a_R$_4.000/mes":     ("R$ 3–4 mil",     3001,      4000,  3500.5),
    "de_R$_4.001/mes_a_R$_6.000/mes":     ("R$ 4–6 mil",     4001,      6000,  5000.5),
    "de_R$_6.001/mes_a_R$_8.000/mes":     ("R$ 6–8 mil",     6001,      8000,  7000.5),
    "de_R$_8.001/mes_a_R$_12.000/mes":    ("R$ 8–12 mil",    8001,     12000, 10000.5),
    "de_R$_12.001/mes_a_R$_16.000/mes":   ("R$ 12–16 mil",  12001,     16000, 14000.5),
    "de_R$_16.001/mes_a_R$_20.000/mes":   ("R$ 16–20 mil",  16001,     20000, 18000.5),
    "de_R$_20.001/mes_a_R$_25.000/mes":   ("R$ 20–25 mil",  20001,     25000, 22500.5),
    "de_R$_25.001/mes_a_R$_30.000/mes":   ("R$ 25–30 mil",  25001,     30000, 27500.5),
    "de_R$_30.001/mes_a_R$_40.000/mes":   ("R$ 30–40 mil",  30001,     40000, 35000.5),
    "Acima_de_R$_40.001/mes":             ("acima de R$ 40 mil", 40001, None, 40001.0),
}

ROTULO_AREA_FORMACAO = {
    "Computacao_/_Engenharia_de_Software_/_Sistemas_de_Informacao/_TI":
        "Computação / Eng. de Software / TI",
    "Economia/_Administracao_/_Contabilidade_/_Financas/_Negocios":
        "Economia / Administração / Negócios",
    "Estatistica/_Matematica_/_Matematica_Computacional/_Ciencias_Atuariais":
        "Estatística / Matemática",
    "Outras_Engenharias_(nao_incluir_engenharia_de_software_ou_TI)": "Outras Engenharias",
    "Marketing_/_Publicidade_/_Comunicacao_/_Jornalismo_/_Ciencias_Sociais":
        "Marketing / Comunicação / Ciências Sociais",
    "Ciencias_Biologicas/_Farmacia/_Medicina/_Area_da_Saude": "Ciências Biológicas / Saúde",
    "Ciencia_de_Dados_/_Inteligencia_Artificial": "Ciência de Dados / IA",
    "Quimica_/_Fisica": "Química / Física",
    "Outra_opcao": "Outras áreas",
}

ROTULO_SETOR = {
    "Financas_ou_Bancos": "Finanças e Bancos",
    "Tecnologia/Fabrica_de_Software": "Tecnologia / Software",
    "Area_de_Consultoria": "Consultoria",
    "Area_da_Saude": "Saúde",
    "Entretenimento_ou_Esportes": "Entretenimento e Esportes",
    "Filantropia/ONG's": "Filantropia / ONG",
    "Setor_Publico": "Setor Público",
    "Setor_de_Educacao": "Educação",
    "Educacao": "Educação",
    "Agronegocios": "Agronegócio",
    "Industria": "Indústria",
    "Varejo": "Varejo",
    "Internet/Ecommerce": "Internet / E-commerce",
    "Telecomunicacao": "Telecomunicações",
    "Marketing": "Marketing",
    "Seguros_ou_Previdencia": "Seguros e Previdência",
    "Setor_Alimenticio": "Alimentício",
    "Setor_Automotivo": "Automotivo",
    "Setor_Farmaceutico": "Farmacêutico",
    "Setor_Imobiliario/_Construcao_Civil": "Imobiliário e Construção",
    "Setor_de_Energia": "Energia",
    "Outra_Opcao": "Outros",
}

# Rótulo das opções de tecnologia: as que aparecem em gráfico.
ROTULO_TECNOLOGIA = {
    "pbi": "Power BI", "looker": "Looker", "looker_studio": "Looker Studio",
    "tableau": "Tableau", "qlik_view_sense": "Qlik", "metabase": "Metabase",
    "superset": "Superset", "grafana": "Grafana", "redash": "Redash",
    "excel_planilha_apenas": "Apenas Excel / Planilhas",
    "nenhuma_ferramenta_bi": "Nenhuma ferramenta de BI",
    "amazon_quicksight": "Amazon QuickSight", "oracle_bi": "Oracle BI",
    "sap_business_objects": "SAP BusinessObjects", "sas_visual_analytics": "SAS Visual Analytics",
    "alteryx": "Alteryx", "pentaho": "Pentaho",
    "python": "Python", "sql": "SQL", "r": "R", "scala": "Scala", "julia": "Julia",
    "ccc": "C / C++ / C#", "rust": "Rust", "vba": "VBA", "dax": "DAX",
    "java": "Java", "js": "JavaScript", "php": "PHP", "net": ".NET",
    "matlab": "MATLAB", "sas_stat": "SAS/STAT",
    "aws": "AWS", "azure": "Azure", "gcp": "Google Cloud", "ibm": "IBM Cloud",
    "on_premise": "On-premise", "cloud_proprietaria": "Cloud proprietária",
    "postgre_sql": "PostgreSQL", "my_sql": "MySQL", "sql_server": "SQL Server",
    "mongo_db": "MongoDB", "oracle": "Oracle", "s3": "Amazon S3",
    "google_big_query": "BigQuery", "databricks": "Databricks", "snowflake": "Snowflake",
    "amazon_redshift": "Redshift", "amazon_athena": "Athena", "amazon_aurora_rds": "Aurora / RDS",
    "elastic_search": "Elasticsearch", "redis": "Redis", "cassandra": "Cassandra",
    "dynamo_db": "DynamoDB", "hive": "Hive", "hbase": "HBase", "presto": "Presto",
    "maria_db": "MariaDB", "sqlite": "SQLite", "firebase": "Firebase",
    "sap_hana": "SAP HANA", "db2": "DB2", "neo4j": "Neo4j", "splunk": "Splunk",
    "microsoft_acess": "Microsoft Access", "google_firestore": "Firestore",
    "nao_utilizo_nenhuma": "Não utilizo nenhum",
}

# Nome de exibição de cada grupo de múltipla escolha, para a bridge.
ROTULO_GRUPO = {
    "linguagens": "Linguagens utilizadas",
    "bancos_dados": "Bancos e plataformas de dados",
    "clouds": "Clouds utilizadas",
    "ferramentas_bi": "Ferramentas de BI",
    "fontes_dados": "Fontes de dados manipuladas",
    # As três perguntas que a Silver junta num grupo só. Ver SUBGRUPO em
    # job_gold.py: públicos diferentes, denominadores diferentes.
    "uso_ia_pessoal": "Uso de IA: a pessoa",
    "uso_ia_empresa": "Uso de IA: a empresa",
    "uso_ia_gestor": "Uso de IA: bloco do gestor",
    "uso_ia_generativa": "Uso de IA generativa",
    "barreiras_ia_generativa": "Barreiras à adoção de IA",
    "atividades_analista_dados": "Atividades: Analista de Dados",
    "atividades_cientista_dados": "Atividades: Cientista de Dados",
    "atividades_engenheiro_dados": "Atividades: Engenheiro de Dados",
    "desafios_gestor": "Desafios do gestor",
    "cargos_no_time": "Cargos presentes no time",
    "percepcao_carreira": "Percepção de carreira",
    "exp_prof_prejudicada": "Experiência profissional prejudicada",
    "fatores_avaliacao_emprego": "Fatores ao avaliar um emprego",
    "fatores_troca_emprego": "Fatores para trocar de emprego",
    "motivos_insatisfacao_2023": "Motivos de insatisfação (só 2023-2024)",
    "linguagem_preferida": "Linguagem preferida",
    "cloud_preferida": "Cloud preferida",
    "ferramenta_bi_diaria": "Ferramenta de BI do dia a dia",
}


# --------------------------------------------------------------------------- #
# atributos degenerados: ficam no fato, mas ainda assim precisam de rótulo
# --------------------------------------------------------------------------- #
# Estes não viraram dimensão (cardinalidade baixa demais), e mesmo assim vão
# parar em eixo de gráfico. Sem rótulo, o eixo mostra a frase inteira da
# pesquisa, com underline no lugar do espaço.

ROTULO_COR_RACA = {
    "Prefiro_nao_informar": "Prefiro não informar",
    "Indigena": "Indígena",
    "nao_declarado": "Não declarado",
}

# A pergunta de prioridade de IA tem 4 respostas, e as duas que começam com
# "Sim" são o que a análise chama de prioridade alta. Ver `ia_prioridade_alta`
# no fato: a regra fica no código, não espalhada em medida DAX.
ROTULO_IA_PRIORIDADE = {
    "Sim,_e_nossa_principal_prioridade_como_empresa_(com_foco_executivo_"
    "significativo_e_alocacao_de_orcamento_relevante).":
        "Principal prioridade da empresa",
    "Sim,_esta_entre_nossas_principais_prioridades_para_os_proximos_2-4_anos_"
    "(com_discussoes_de_iniciativas_e_orcamentos_de_curto_a_medio_prazo).":
        "Entre as principais prioridades",
    "Mais_ou_menos..._E_uma_das_varias_iniciativas_que_estamos_impulsionando,_"
    "mas_nao_e_uma_prioridade_(tratam-se_de_iniciativas_isoladas_e_com_pouco_"
    "foco).":
        "Iniciativa isolada, sem foco",
    "Nao_e_uma_iniciativa_que_estamos_focando_e_nao_tem_sido_uma_prioridade.":
        "Não é prioridade",
    "Nao_sei_opinar_sobre_esse_assunto.": "Não sei opinar",
}

ORDEM_IA_PRIORIDADE = [
    "Não sei opinar", "Não é prioridade", "Iniciativa isolada, sem foco",
    "Entre as principais prioridades", "Principal prioridade da empresa",
]

ROTULO_LLMS_RESULTADO = {
    "Sim._Temos_projetos_envolvendo_AI_Generativa_e_Modelos_LLM_em_producao,_"
    "gerando_resultados_e_impacto_no_negocio.":
        "Sim, em produção com resultado",
    'Em_partes._Temos_alguns_projetos_"piloto",_envolvendo_AI_Generativa_e_'
    "Modelos_LLM,_rodando_mas_sem_muitos_resultados_e_impacto_no_negocio.":
        "Em partes, projetos piloto",
    "Nao,_ainda_nao_comecamos_nenhum_projeto_envolvendo_AI_Generativa_e_"
    "Modelos_LLM.":
        "Não começamos",
    "Nao._Os_projetos_envolvendo_AI_Generativa_e_Modelos_LLM,_ainda_estao_em_"
    "fase_de_investigacao_e_planejamento.":
        "Ainda em investigação",
    "Nao_sei_opinar_sobre_isso.": "Não sei opinar",
}

ROTULO_LAYOFF_EMPRESA = {
    "Nao_ocorreram_layoffs/demissoes_em_massa_na_empresa_em_que_trabalho":
        "Não houve layoff",
    "Sim,_ocorreram_layoffs/demissoes_em_massa_na_empresa_em_que_trabalho_"
    "mas_nao_fui_afetado":
        "Houve layoff, não fui afetado",
    "Sim,_ocorreram_layoffs/demissoes_em_massa_na_empresa_em_que_trabalhava_"
    "e_eu_fui_afetado":
        "Houve layoff, fui afetado",
}

# O texto que marca prioridade alta. Uma resposta que comece com isto conta.
PREFIXO_IA_PRIORIDADE_ALTA = "Sim,"


# --------------------------------------------------------------------------- #
# rótulos das opções de múltipla escolha que ainda saíam cruas no eixo
# --------------------------------------------------------------------------- #
# Cinco grupos chegavam ao gráfico com o nome técnico da coluna da origem
# ("falta_expertise_ou_recurso"). Num eixo de gráfico isso é ilegível, e é o
# tipo de detalhe que a banca lê como falta de acabamento.

ROTULO_OPCAO_EXTRA = {
    # barreiras para adotar IA generativa (bloco de gestores)
    "falta_expertise_ou_recurso": "Falta de expertise ou recurso",
    "falta_compreensao_caso_uso": "Falta de compreensão do caso de uso",
    "seguranca_privacidade_dados": "Segurança e privacidade dos dados",
    "falta_confiab_saida_alucinacao_modelo": "Falta de confiabilidade da saída",
    "incerteza_rel_regulamentacao": "Incerteza regulatória",
    "preocupacao_prop_intelectual": "Propriedade intelectual",
    "alta_direcao_nao_ve_valor_prioridade": "Alta direção não vê valor",

    # percepção de carreira
    "aprov_processos_seletivos_entrevistas": "Aprovação em processos seletivos",
    "atencao_opiniao_ideias": "Atenção às minhas ideias",
    "nvl_cobranca_e_stress_trab": "Nível de cobrança e estresse",
    "oportunidades_progresso_carreira": "Oportunidades de progresso",
    "qtd_oportunidades_vagas_emprego_receb": "Quantidade de vagas recebidas",
    "rel_outros_membros_empresa_em_trabalho": "Relação com o time no trabalho",
    "rel_outros_membros_empresa_integracao_fora_trab": "Integração fora do trabalho",
    "senioridade_vagas_recebidas_rel_experiencia": "Senioridade das vagas recebidas",
    "vel_progressao_carreira": "Velocidade de progressão",

    # experiência profissional prejudicada
    "exp_prof_nao_prejud": "Não foi prejudicada",
    "exp_prof_prejud_cor_raca_etnia": "Prejudicada por cor ou raça",
    "exp_prof_prejud_ident_gen": "Prejudicada por identidade de gênero",
    "exp_prof_prejud_pcd": "Prejudicada por deficiência",

    # cargos que existem no time (respondido por gestores)
    "analista_bi": "Analista de BI",
    "analista_business": "Analista de Negócios",
    "analista_dados": "Analista de Dados",
    "arquiteto_dados": "Arquiteto de Dados",
    "cientista_dados": "Cientista de Dados",
    "data_product_manager": "Product Manager de Dados",
    "dba": "DBA",
    "engenheiro_analytics": "Analytics Engineer",
    "engenheiro_dados": "Engenheiro de Dados",
    "engenheiro_ml_ia": "Engenheiro de ML e IA",

    # --- uso de IA generativa, bloco 1: como a PESSOA usa (não gestores)
    "uso_ia_gen_gratuita_produtividade": "Uso versão gratuita",
    "uso_pago_ia_gen_empresa_paga": "A empresa paga a ferramenta",
    "uso_pago_ia_gen_produtividade": "Pago do próprio bolso",
    "uso_copilot": "Uso Copilot",
    "nao_uso_ia_gen_produtividade": "Não uso",

    # --- uso de IA generativa, bloco 2: como a EMPRESA usa (não gestores)
    # ⚠️ O SUFIXO `_1` É A EDIÇÃO 2023-2024 DA MESMA PERGUNTA.
    # Ela mudou de nome de coluna em 2024-2025: `colaboradores_uso_ia_*` virou
    # `ia_llm_empresa_*`. Os pares abaixo levam o MESMO rótulo de propósito,
    # para as três edições caírem na mesma barra do gráfico. Rótulo diferente
    # aqui não é detalhe de texto: parte a série em duas.
    "ia_llm_empresa_descentralizada_independente": "Uso descentralizado na empresa",
    "colaboradores_uso_ia_descentra_independ_1": "Uso descentralizado na empresa",
    "ia_llm_empresa_uso_centralizado": "Uso centralizado na empresa",
    "direcionamento_centralizado_ia_generativa_1": "Uso centralizado na empresa",
    "ia_llm_empresa_uso_copilot": "Empresa usa Copilot",
    "dev_usando_copilot_1": "Empresa usa Copilot",
    "ia_llm_empresa_prod_interno": "Produto interno com LLM",
    "ia_gen_llm_melhorar_prod_int_colaboradores_1": "Produto interno com LLM",
    "ia_llm_empresa_prod_externo": "Produto externo com LLM",
    "ia_llm_empresa_frente_negoc": "Frente de negócio com LLM",
    "ia_gen_llm_principal_frente_neg_1": "Frente de negócio com LLM",
    "ia_llm_empresa_nao_prioridade": "Não é prioridade na empresa",
    "ia_llm_nao_prioridade_1": "Não é prioridade na empresa",
    "ia_llm_empresa_sem_opiniao": "Sem opinião",
    "sem_opiniao_llm_ia_generativa_1": "Sem opinião",

    # --- uso de IA generativa, bloco 3: o bloco do GESTOR
    # Mesmos nomes de coluna sem sufixo, e público inteiramente diferente:
    # 2.505 gestores, nenhum deles presente nos dois blocos acima.
    "colaboradores_uso_ia_descentra_independ": "Uso descentralizado e independente",
    "direcionamento_centralizado_ia_generativa": "Direcionamento centralizado",
    "dev_usando_copilot": "Desenvolvedores usando Copilot",
    "ia_gen_llm_melhorar_prod_int_colaboradores": "Melhorar produto interno",
    "ia_gen_llm_melhorar_prod_ext": "Melhorar produto externo",
    "ia_gen_llm_principal_frente_neg": "Principal frente de negócio",
    "ia_llm_nao_prioridade": "Não é prioridade",
    "sem_opiniao_llm_ia_generativa": "Sem opinião",
    "dados_empresa_nao_prep_ia_gen": "Dados não estão preparados",
    "retorno_roi_nao_comprovado_ia_gen": "ROI não comprovado",
}


def rotular(valor, mapa, capitalizar=True):
    """Aplica o mapa; sem entrada, limpa o snake_case para ficar legível."""
    if valor is None:
        return None
    if valor in mapa:
        return mapa[valor]
    limpo = valor.replace("_", " ").strip()
    return limpo[:1].upper() + limpo[1:] if capitalizar else limpo

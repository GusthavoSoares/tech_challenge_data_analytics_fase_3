"""
Grupos de múltipla escolha do State of Data Brasil. TC3.

ARQUIVO GERADO. Não editar à mão sem registrar o motivo aqui.

Cada pergunta de múltipla escolha da pesquisa vira ~N colunas binárias na base
(uma por opção). São ~320 das ~400 colunas. Este módulo diz quais colunas
pertencem a qual pergunta, por edição, para a Silver consolidar cada grupo em
UMA coluna de lista.

Como os grupos foram derivados (ver docs/VALIDACAO_BRONZE.md §8):

  1. Classificação semântica, por lista explícita de nomes. Resolve
     `linguagens`, `bancos_dados`, `clouds`, `ferramentas_bi`, `fontes_dados`
     e `uso_ia_generativa`, que se misturam quando agrupados só por máscara.

  2. Máscara de resposta, para o restante, colunas da mesma pergunta têm
     exatamente o mesmo conjunto de respondentes preenchido (quem responde uma
     opção responde todas). Resolve os grupos de atividade e percepção.

Cobertura: 323/329 (2023-2024) · 323/323 (2024-2025) · 310/316 (2025-2026).
O que fica de fora são as colunas booleanas canônicas (`gestor`, `vive_brasil`,
`empresa_possui_datalake`, `empresa_possui_dw`, `satisfacao_empresa_atual`,
`vive_estado_formacao`, `mudou_estado`), que não são múltipla escolha e viram
coluna própria na Silver.

⚠️ O SUFIXO `_1` INVERTE ENTRE AS EDIÇÕES

Duas perguntas usam o MESMO conjunto de opções e na origem só se distinguem
pelo sufixo `_1`. O problema: **qual delas leva o sufixo muda de uma edição
para a outra**. Medido pelo tamanho da base:

    pergunta AMPLA    2023: sem sufixo (4.727)  |  2024/25: com `_1` (4.861 / 3.227)
    pergunta ESTREITA 2023: opções próprias     |  2024/25: sem sufixo (1.527 / 1.001)

Agrupar pelo nome, como esta lista fazia até 30/08, junta a pergunta ampla de
2023 com a estreita de 2024, e a série cai de 4.727 para 1.527 sem nenhum
motivo real. Por isso o agrupamento aqui é **pela base**, não pelo nome:

  - `fatores_avaliacao_emprego`: base ampla, nas 3 edições, ~90% dos empregados
  - `fatores_troca_emprego`: base estreita, só 2024/25, ~30%
  - `motivos_insatisfacao_2023`: só 2023, com opções próprias e descritivas
    (`salario_atual_n_corresponde_mercado`, `clima_trabalho_ruim`). É provável
    que seja a antecessora de `fatores_troca_emprego`, mas as OPÇÕES são outras,
    então não vira série temporal sem o enunciado.

Os nomes seguem provisórios: descrevem o comportamento observado, não o
enunciado da pesquisa. Falta o de-para do Alexandre para fechar.

  - `motivos_insatisfacao_2023`: existe só em 2023-2024, com nomes descritivos
    (`salario_atual_n_corresponde_mercado`, `clima_trabalho_ruim`, ...). Pode
    ser a mesma pergunta que virou `fatores_emprego_atual` nas edições
    seguintes. Enquanto não confirmado, fica como grupo próprio e NÃO entra em
    comparação temporal.
"""

GRUPOS_MULTIPLA_ESCOLHA = {
    "atividades_analista_dados": {
        2023: [
            "SSIS_1", "alteryx_2", "analise_processamento_linguagem_prog",
            "apache_airflow_1", "apache_nifi_1", "aws_glue_1",
            "criacao_manutencao_etl_analista", "dashboard_ferramentas_bi",
            "dashboards_ferramenta_bi_analista", "dashboards_script_analista",
            "databricks_2", "empresa_nao_utiliza_ferramenta_autonomia",
            "engenheiro_dados_sem_ferramenta_etl_1", "estudo_experimentos_util_estatistica",
            "estudo_uso_estatistica_analista", "exportacao_rel_para_area_neg_1",
            "extracao_api_analista", "extracao_dados_api",
            "ferramentas_analise_dados_dentro_crm", "ferramentas_auto_ml",
            "ferramentas_avanc_estatistica_analista", "fivetran_1", "google_dataflow_1",
            "ibm_data_stage_1", "knime_1", "luigi_1",
            "manutencao_etl_utilizando_ferramenta_etl_analista",
            "manutencao_planilha_area_negocio", "manutencao_planilhas_analista",
            "modelagem_dados_dw_data_mart_analista", "modelagem_dw_data_mart_analista",
            "nao_sei_informar_ferramenta_autonomia_area_neg",
            "nenhuma_opcao_engenheiro_dados_2", "nenhuma_opcao_engenheiro_dados_3",
            "oracle_data_integrator_1", "pentaho_2", "point_click",
            "product_metrics_insight", "qlik_sense_1", "relatorios_sql_exportados_1",
            "sap_bw_etl_1", "sas_data_integration_1", "script_python_1",
            "sql_stored_procedures_1", "stitch_1", "talend_1",
            "utilizacao_ferramenta_avancada_estatistica"
        ],
        2024: [
            "alteryx_analista", "analise_processamento_linguagem_prog",
            "apache_airflow_analista", "apache_nifi_analista", "aws_glue_analista",
            "criacao_manutencao_etl_analista", "dashboard_ferramentas_bi",
            "dashboards_ferramenta_bi_analista", "dashboards_script_analista",
            "databricks_analista", "empresa_nao_utiliza_ferramenta_autonomia",
            "estudo_experimentos_util_estatistica", "estudo_uso_estatistica_analista",
            "exportacao_rel_area_neg_analista_dados", "extracao_api_analista",
            "extracao_dados_api", "extracao_rel_sql_analista",
            "ferramentas_analise_dados_dentro_crm", "ferramentas_auto_ml",
            "ferramentas_avanc_estatistica_analista", "fivetran_analista",
            "google_dataflow_analista", "ibm_data_stage_analista", "knime_analista",
            "luigi_analista", "manutencao_etl_utilizando_ferramenta_etl_analista",
            "manutencao_planilha_area_negocio", "manutencao_planilhas_analista",
            "modelagem_dados_dw_data_mart_analista", "modelagem_dw_data_mart_analista",
            "nao_sei_informar_ferramenta_autonomia_area_neg",
            "nao_utilizo_ferramentas_etl_analista", "nenhuma_das_opcoes_analista",
            "nenhuma_opcao_listada_atv_analista", "oracle_data_integrator_analista",
            "pentaho_analista", "point_click", "product_metrics_insight", "python_analista",
            "qlik_sense_analista", "sap_bw_etl_analista", "sas_data_integration_analista",
            "ssis_analista", "stitch_analista", "stored_procedures_analista",
            "talent_analista", "utilizacao_ferramenta_avancada_estatistica"
        ],
        2025: [
            "alteryx_analista", "analise_processamento_linguagem_prog",
            "apache_airflow_analista", "apache_nifi_analista", "aws_glue_analista",
            "criacao_manutencao_etl_analista", "dashboard_ferramentas_bi",
            "dashboards_ferramenta_bi_analista", "dashboards_script_analista",
            "databricks_analista", "empresa_nao_utiliza_ferramenta_autonomia",
            "estudo_experimentos_util_estatistica", "estudo_uso_estatistica_analista",
            "exportacao_rel_area_neg_analista_dados", "extracao_api_analista",
            "extracao_dados_api", "extracao_rel_sql_analista",
            "ferramentas_analise_dados_dentro_crm", "ferramentas_auto_ml",
            "ferramentas_avanc_estatistica_analista", "fivetran_analista",
            "google_dataflow_analista", "ibm_data_stage_analista", "knime_analista",
            "luigi_analista", "manutencao_etl_utilizando_ferramenta_etl_analista",
            "manutencao_planilha_area_negocio", "manutencao_planilhas_analista",
            "modelagem_dados_dw_data_mart_analista", "modelagem_dw_data_mart_analista",
            "nao_sei_informar_ferramenta_autonomia_area_neg",
            "nao_utilizo_ferramentas_etl_analista", "nenhuma_das_opcoes_analista",
            "nenhuma_opcao_listada_atv_analista", "oracle_data_integrator_analista",
            "pentaho_analista", "point_click", "product_metrics_insight", "python_analista",
            "qlik_sense_analista", "sap_bw_etl_analista", "sas_data_integration_analista",
            "ssis_analista", "stitch_analista", "stored_procedures_analista",
            "talent_analista", "utilizacao_ferramenta_avancada_estatistica"
        ],
    },
    "atividades_cientista_dados": {
        2023: [
            "LLM_tmp_gasto_cientista", "NLP_dados_nao_estruturados",
            "ambiente_local_jupyter_anaconda", "analise_requisitos_area_negocio",
            "analise_requisitos_tmp_gasto_cientista", "aprendizado_reforco",
            "auto_ml_cientista", "cadeias_markov_hmm_analise_dados",
            "coleta_limpeza_cientista", "coleta_limpeza_modelagem_analise",
            "controle_de_versao_cientista", "criacao_gerencia_feature_store_mlops",
            "criacao_manun_etl_dags_automacoes", "criacao_treinamento_llm",
            "dashboard_ferramentas_bi_1", "dashboards_ferramenta_bi_analista_1",
            "data_apps_cientista", "deploy_modelo_prod_criacao_api_monitoramento",
            "dev_ml_prod_tmp_gasto_cientista", "dev_modelo_ml", "dev_nuvem",
            "feature_store_cientista", "feature_store_ml_ops_tmp_gasto_cientista",
            "ferramenta_avanc_estatistica_analise_ajust_modelo", "ferramenta_bi_cientista",
            "ferramenta_estatistica_avanc_cientista", "ferramenta_etl_cientista",
            "ferramentas_avanc_estatistica_analista_1",
            "infra_modelo_clusters_servidores_tmp_gasto_cientista",
            "infra_modelos_rodam_em_clusters_api_etc", "llm_cientista_dados_uso",
            "manutencao_etl_dag_tmp_gasto_cientista",
            "manutencao_ml_em_prod_monitoramento_ajuste_tmp_gasto_cientista",
            "manutencao_ml_prod_tmp_gasto_cientista",
            "manutencao_modelo_ml_producao_melhorias",
            "metodo_estatistico_bayesiano_analise", "metodos_estatisticos_classicos",
            "ml_deteccao_fraude", "modelo_deteccao_churn", "modelos_preditivos",
            "planilha_excel_cientista", "plataforma_ml_cientista",
            "redes_neurais_odelo_arvore", "regressao_logistica_glm", "sistema_recomendacao",
            "tecnicas_clusterizacao", "uso_adhoc_modelo_preditivo",
            "uso_adhoc_modelo_preditivo_1", "visao_computacional"
        ],
        2024: [
            "LLM_tmp_gasto_cientista", "NLP_dados_nao_estruturados",
            "ad_hoc_hipoteses_tmp_gasto_cientista", "ambiente_local_jupyter_anaconda",
            "analise_requisitos_area_negocio", "analise_requisitos_tmp_gasto_cientista",
            "aprendizado_reforco", "auto_ml_cientista", "cadeias_markov_hmm_analise_dados",
            "coleta_limpeza_cientista", "coleta_limpeza_modelagem_analise",
            "construcao_dashboard_ferramenta_bi_analista", "controle_de_versao_cientista",
            "criacao_gerencia_feature_store_mlops", "criacao_manun_etl_dags_automacoes",
            "criacao_treinamento_llm", "dashboards_ferramenta_bi_tmp_gasto_cientista",
            "data_apps_cientista", "deploy_modelo_prod_criacao_api_monitoramento",
            "dev_ml_prod_tmp_gasto_cientista", "dev_modelo_ml", "dev_nuvem",
            "feature_store_cientista", "feature_store_ml_ops_tmp_gasto_cientista",
            "ferramenta_avanc_estatistica_analise_ajust_modelo",
            "ferramenta_avancadas_estatistica_analista_tmp_gasto_cientista",
            "ferramenta_bi_cientista", "ferramenta_estatistica_avanc_cientista",
            "ferramenta_etl_cientista",
            "infra_modelo_clusters_servidores_tmp_gasto_cientista",
            "infra_modelos_rodam_em_clusters_api_etc", "llm_cientista_dados_uso",
            "manutencao_etl_dag_tmp_gasto_cientista",
            "manutencao_ml_em_prod_monitoramento_ajuste_tmp_gasto_cientista",
            "manutencao_ml_prod_tmp_gasto_cientista",
            "manutencao_modelo_ml_producao_melhorias",
            "metodo_estatistico_bayesiano_analise", "metodos_estatisticos_classicos",
            "ml_deteccao_fraude", "modelo_deteccao_churn", "modelos_preditivos",
            "planilha_excel_cientista", "plataforma_ml_cientista",
            "redes_neurais_odelo_arvore", "regressao_logistica_glm", "sistema_recomendacao",
            "tecnicas_clusterizacao", "uso_adhoc_modelo_preditivo", "visao_computacional"
        ],
        2025: [
            "LLM_tmp_gasto_cientista", "NLP_dados_nao_estruturados",
            "ad_hoc_hipoteses_tmp_gasto_cientista", "ambiente_local_jupyter_anaconda",
            "analise_requisitos_area_negocio", "analise_requisitos_tmp_gasto_cientista",
            "aprendizado_reforco", "auto_ml_cientista", "cadeias_markov_hmm_analise_dados",
            "coleta_limpeza_cientista", "coleta_limpeza_modelagem_analise",
            "construcao_dashboard_ferramenta_bi_analista", "controle_de_versao_cientista",
            "criacao_gerencia_feature_store_mlops", "criacao_manun_etl_dags_automacoes",
            "criacao_treinamento_llm", "dashboards_ferramenta_bi_tmp_gasto_cientista",
            "data_apps_cientista", "deploy_modelo_prod_criacao_api_monitoramento",
            "dev_ml_prod_tmp_gasto_cientista", "dev_modelo_ml", "dev_nuvem",
            "feature_store_cientista", "feature_store_ml_ops_tmp_gasto_cientista",
            "ferramenta_avanc_estatistica_analise_ajust_modelo",
            "ferramenta_avancadas_estatistica_analista_tmp_gasto_cientista",
            "ferramenta_bi_cientista", "ferramenta_estatistica_avanc_cientista",
            "ferramenta_etl_cientista",
            "infra_modelo_clusters_servidores_tmp_gasto_cientista",
            "infra_modelos_rodam_em_clusters_api_etc", "llm_cientista_dados_uso",
            "manutencao_etl_dag_tmp_gasto_cientista",
            "manutencao_ml_em_prod_monitoramento_ajuste_tmp_gasto_cientista",
            "manutencao_ml_prod_tmp_gasto_cientista",
            "manutencao_modelo_ml_producao_melhorias",
            "metodo_estatistico_bayesiano_analise", "metodos_estatisticos_classicos",
            "ml_deteccao_fraude", "modelo_deteccao_churn", "modelos_preditivos",
            "planilha_excel_cientista", "plataforma_ml_cientista",
            "redes_neurais_odelo_arvore", "regressao_logistica_glm", "sistema_recomendacao",
            "tecnicas_clusterizacao", "uso_adhoc_modelo_preditivo", "visao_computacional"
        ],
    },
    "atividades_engenheiro_dados": {
        2023: [
            "SSIS", "alteryx_1", "apache_airflow", "apache_nifi", "aws_glue",
            "criacao_componentes_ingestao_dados", "dados_streaming_data_lake_lakehouse",
            "databricks_1", "engenheiro_dados_sem_ferramenta_etl", "etl_com_ferramentas_bi",
            "etl_pentaho_talent_etc", "exportacao_rel_para_area_neg", "fivetran",
            "google_dataflow", "ibm_data_stage", "integracao_dados_plataformas_dados",
            "integracao_fonte_dados_diferentes_tmp_gasto", "knime", "luigi",
            "manutencao_criacao_rep_dados_streaming",
            "modelagem_arquitetura_dados_tmp_gasto", "modelagem_dados_dw_data_mart",
            "modelagem_dados_dw_data_mart_1", "nenhuma_opcao_engenheiro_dados",
            "nenhuma_opcao_engenheiro_dados_1", "oracle_data_integrator", "pentaho_1",
            "pipeline_dados_ling_prog", "pipelines_com_codigo", "qlik_sense",
            "quali_dados_dicionario", "qualidade_dados_tmp_gasto",
            "relatorios_sql_exportados", "sap_bw_etl", "sas_data_integration",
            "script_python", "sql_stored_procedures", "stitch", "talend"
        ],
        2024: [
            "SSIS", "apache_airflow", "apache_nifi", "aws_glue",
            "criacao_componentes_ingestao_dados", "dados_streaming_data_lake_lakehouse",
            "engenheiro_dados_alteryx", "engenheiro_dados_databricks",
            "engenheiro_dados_pentaho", "engenheiro_dados_sem_ferramenta_etl",
            "etl_com_ferramentas_bi", "etl_pentaho_talent_etc",
            "exportacao_rel_para_area_neg", "fivetran", "google_dataflow", "ibm_data_stage",
            "integracao_dados_plataformas_dados",
            "integracao_fonte_dados_diferentes_tmp_gasto", "knime", "luigi",
            "manutencao_criacao_rep_dados_streaming",
            "modelagem_arquitetura_dados_tmp_gasto", "modelagem_dados_dw_data_mart",
            "modelagem_dados_dw_data_mart_1", "nenhuma_das_opcoes_tmp_gasto",
            "nenhuma_opcao_engenheiro_dados", "oracle_data_integrator",
            "pipeline_dados_ling_prog", "pipelines_com_codigo", "qlik_sense",
            "quali_dados_dicionario", "qualidade_dados_tmp_gasto",
            "relatorios_sql_exportados", "sap_bw_etl", "sas_data_integration",
            "script_python", "sql_stored_procedures", "stitch", "talend"
        ],
        2025: [
            "SSIS", "apache_airflow", "apache_nifi", "aws_glue",
            "criacao_componentes_ingestao_dados", "dados_streaming_data_lake_lakehouse",
            "engenheiro_dados_alteryx", "engenheiro_dados_databricks",
            "engenheiro_dados_pentaho", "engenheiro_dados_sem_ferramenta_etl",
            "etl_com_ferramentas_bi", "etl_pentaho_talent_etc",
            "exportacao_rel_para_area_neg", "fivetran", "google_dataflow", "ibm_data_stage",
            "integracao_dados_plataformas_dados",
            "integracao_fonte_dados_diferentes_tmp_gasto", "knime", "luigi",
            "manutencao_criacao_rep_dados_streaming",
            "modelagem_arquitetura_dados_tmp_gasto", "modelagem_dados_dw_data_mart",
            "modelagem_dados_dw_data_mart_1", "nenhuma_das_opcoes_tmp_gasto",
            "nenhuma_opcao_engenheiro_dados", "oracle_data_integrator",
            "pipeline_dados_ling_prog", "pipelines_com_codigo", "qlik_sense",
            "quali_dados_dicionario", "qualidade_dados_tmp_gasto",
            "relatorios_sql_exportados", "sap_bw_etl", "sas_data_integration",
            "script_python", "sql_stored_procedures", "stitch", "talend"
        ],
    },
    "bancos_dados": {
        2023: [
            "amazon_athena", "amazon_aurora_rds", "amazon_redshift", "cassandra",
            "coach_db", "databricks", "datomic", "db2", "dynamo_db", "elastic_search",
            "firebase", "firebird", "google_big_query", "google_firestore", "hbase", "hive",
            "maria_db", "microsoft_acess", "mongo_db", "my_sql", "nao_utilizo_nenhuma",
            "neo4j", "oracle", "oracle_1", "postgre_sql", "presto", "redis", "s3",
            "sap_hana", "snowflake", "splunk", "sql_server", "sqlite", "sybase", "vertica"
        ],
        2024: [
            "amazon_athena", "amazon_aurora_rds", "amazon_redshift", "cassandra",
            "coach_db", "databricks", "datomic", "db2", "dynamo_db", "elastic_search",
            "firebase", "firebird", "google_big_query", "google_firestore", "hbase", "hive",
            "maria_db", "microsoft_acess", "mongo_db", "my_sql", "nao_utilizo_nenhuma",
            "neo4j", "oracle", "oracle_1", "postgre_sql", "presto", "redis", "s3",
            "sap_hana", "snowflake", "splunk", "sql_server", "sqlite", "sybase", "vertica"
        ],
        2025: [
            "amazon_athena", "amazon_aurora_rds", "amazon_redshift", "cassandra",
            "coach_db", "databricks", "datomic", "db2", "dynamo_db", "elastic_search",
            "firebase", "firebird", "google_big_query", "google_firestore", "hbase", "hive",
            "maria_db", "microsoft_acess", "mongo_db", "my_sql", "nao_utilizo_nenhuma",
            "neo4j", "oracle", "oracle_1", "postgre_sql", "presto", "redis", "s3",
            "sap_hana", "snowflake", "splunk", "sql_server", "sqlite", "sybase", "vertica"
        ],
    },
    "barreiras_ia_generativa": {
        2023: [
            "alta_direcao_nao_ve_valor_prioridade", "falta_compreensao_caso_uso",
            "falta_confiab_saida_alucinacao_modelo", "falta_expertise_ou_recurso",
            "incerteza_rel_regulamentacao", "preocupacao_prop_intelectual",
            "seguranca_privacidade_dados"
        ],
        2024: [
            "alta_direcao_nao_ve_valor_prioridade", "falta_compreensao_caso_uso",
            "falta_confiab_saida_alucinacao_modelo", "falta_expertise_ou_recurso",
            "incerteza_rel_regulamentacao", "preocupacao_prop_intelectual",
            "seguranca_privacidade_dados"
        ],
        2025: [
            "alta_direcao_nao_ve_valor_prioridade", "falta_compreensao_caso_uso",
            "falta_confiab_saida_alucinacao_modelo", "falta_expertise_ou_recurso",
            "incerteza_rel_regulamentacao", "preocupacao_prop_intelectual",
            "seguranca_privacidade_dados"
        ],
    },
    "cargos_no_time": {
        2023: [
            "analista_bi", "analista_business", "analista_dados", "arquiteto_dados",
            "cientista_dados", "data_product_manager", "dba", "engenheiro_analytics",
            "engenheiro_dados"
        ],
        2024: [
            "analista_bi", "analista_business", "analista_dados", "arquiteto_dados",
            "cientista_dados", "data_product_manager", "dba", "engenheiro_analytics",
            "engenheiro_dados", "engenheiro_ml_ia"
        ],
        2025: [
            "analista_bi", "analista_business", "analista_dados", "arquiteto_dados",
            "cientista_dados", "data_product_manager", "dba", "engenheiro_analytics",
            "engenheiro_dados", "engenheiro_ml_ia"
        ],
    },
    "clouds": {
        2023: [
            "aws", "azure", "cloud_proprietaria", "gcp", "ibm", "on_premise"
        ],
        2024: [
            "aws", "azure", "cloud_proprietaria", "gcp", "ibm", "on_premise"
        ],
        2025: [
            "aws", "azure", "cloud_proprietaria", "gcp", "ibm", "on_premise"
        ],
    },
    "desafios_gestor": {
        2023: [
            "contratacao_area_dados", "contratacao_ferramentas_dados",
            "contratar_novos_talentos", "convencer_aumentar_invest_dados",
            "desenv_e_mant_modelos_ml_prod", "dividir_tempo_entregas_tec_gestao",
            "gerar_valor_area_neg_atrav_estud_experim",
            "gerenciar_expectativ_areas_neg_rel_equipe_dados", "gestao_equipe_em_remoto",
            "gestao_proj_multidisciplinaridades_empresa", "gestor_analise_dados",
            "gestor_ciencia_dados", "gestor_eng_dados", "gestor_ia", "gestor_pessoas",
            "gestor_produtos", "gestor_projetos", "inovacao_atraves_area_dados",
            "manutencao_projetos_model_prod_meio_cresc_empresa",
            "organizacao_treinamentos_iniciat_para_maior_maturidade_analitica",
            "organizar_info_resguard_quali_confiab", "processar_armazenar_big_data",
            "reter_talentos", "retorno_roi_projeto_dados", "visao_longo_prazo_dados_empresa"
        ],
        2024: [
            "contratacao_area_dados", "contratacao_ferramentas_dados",
            "contratar_novos_talentos", "convencer_aumentar_invest_dados",
            "desenv_e_mant_modelos_ml_prod", "dividir_tempo_entregas_tec_gestao",
            "gerar_valor_area_neg_atrav_estud_experim",
            "gerenciar_expectativ_areas_neg_rel_equipe_dados", "gestao_equipe_em_remoto",
            "gestao_proj_multidisciplinaridades_empresa", "gestor_analise_dados",
            "gestor_ciencia_dados", "gestor_eng_dados", "gestor_ia", "gestor_pessoas",
            "gestor_produtos", "gestor_projetos", "inovacao_atraves_area_dados",
            "manutencao_projetos_model_prod_meio_cresc_empresa",
            "organizacao_treinamentos_iniciat_para_maior_maturidade_analitica",
            "organizar_info_resguard_quali_confiab", "processar_armazenar_big_data",
            "reter_talentos", "retorno_roi_projeto_dados", "visao_longo_prazo_dados_empresa"
        ],
        2025: [
            "contratacao_area_dados", "contratacao_ferramentas_dados",
            "contratar_novos_talentos", "convencer_aumentar_invest_dados",
            "desenv_e_mant_modelos_ml_prod", "dividir_tempo_entregas_tec_gestao",
            "gerar_valor_area_neg_atrav_estud_experim",
            "gerenciar_expectativ_areas_neg_rel_equipe_dados", "gestao_equipe_em_remoto",
            "gestao_proj_multidisciplinaridades_empresa", "gestor_analise_dados",
            "gestor_ciencia_dados", "gestor_eng_dados", "gestor_ia", "gestor_pessoas",
            "gestor_produtos", "gestor_projetos", "inovacao_atraves_area_dados",
            "manutencao_projetos_model_prod_meio_cresc_empresa",
            "organizacao_treinamentos_iniciat_para_maior_maturidade_analitica",
            "organizar_info_resguard_quali_confiab", "processar_armazenar_big_data",
            "reter_talentos", "retorno_roi_projeto_dados", "visao_longo_prazo_dados_empresa"
        ],
    },
    "exp_prof_prejudicada": {
        2023: [
            "exp_prof_nao_prejud", "exp_prof_prejud_cor_raca_etnia",
            "exp_prof_prejud_ident_gen", "exp_prof_prejud_pcd"
        ],
        2024: [
            "exp_prof_nao_prejud", "exp_prof_prejud_cor_raca_etnia",
            "exp_prof_prejud_ident_gen", "exp_prof_prejud_pcd"
        ],
        2025: [
            "exp_prof_nao_prejud", "exp_prof_prejud_cor_raca_etnia",
            "exp_prof_prejud_ident_gen", "exp_prof_prejud_pcd"
        ],
    },
    "fatores_avaliacao_emprego": {
        2023: [
            "ambiente_clima_trabalho", "beneficios", "flexibilidade_trab_remoto",
            "maturidade_empresa_dados_tec", "oport_aprendizado_trab_ref_area",
            "plano_carreira_oport_cresc_prof", "proposito_trabalho_empresa",
            "qualidade_lideres_gestores", "remuneracao_salario", "rep_empresa_mercado"
        ],
        2024: [
            "ambiente_clima_trabalho_1", "beneficios_1", "flexibilidade_trab_remoto_1",
            "maturidade_empresa_dados_tec_1", "oport_aprendizado_trab_ref_area_1",
            "plano_carreira_oport_cresc_prof_1", "proposito_trabalho_empresa_1",
            "qualidade_lideres_gestores_1", "remuneracao_salario_1", "rep_empresa_mercado_1"
        ],
        2025: [
            "ambiente_clima_trabalho_1", "beneficios_1", "flexibilidade_trab_remoto_1",
            "maturidade_empresa_dados_tec_1", "oport_aprendizado_trab_ref_area_1",
            "plano_carreira_oport_cresc_prof_1", "proposito_trabalho_empresa_1",
            "qualidade_lideres_gestores_1", "remuneracao_salario_1", "rep_empresa_mercado_1"
        ],
    },
    "fatores_troca_emprego": {
        2023: [],
        2024: [
            "ambiente_clima_trabalho", "beneficios", "flexibilidade_trab_remoto",
            "maturidade_empresa_dados_tec", "oport_aprendizado_trab_ref_area",
            "plano_carreira_oport_cresc_prof", "proposito_trabalho_empresa",
            "qualidade_lideres_gestores", "remuneracao_salario", "rep_empresa_mercado",
            "trab_outra_area_atuacao"
        ],
        2025: [
            "ambiente_clima_trabalho", "beneficios", "flexibilidade_trab_remoto",
            "maturidade_empresa_dados_tec", "oport_aprendizado_trab_ref_area",
            "plano_carreira_oport_cresc_prof", "proposito_trabalho_empresa",
            "qualidade_lideres_gestores", "remuneracao_salario", "rep_empresa_mercado",
            "trab_outra_area_atuacao"
        ],
    },
    "ferramentas_bi": {
        2023: [
            "alteryx", "amazon_quicksight", "birst", "excel_planilha_apenas", "grafana",
            "ibm_analytics_cognos", "looker", "looker_studio", "metabase", "microstategy",
            "mode", "nenhuma_ferramenta_bi", "oracle_bi", "pbi", "pentaho",
            "qlik_view_sense", "redash", "salesforce_einstein_analytics",
            "sap_business_objects", "sas_visual_analytics", "superset", "tableau",
            "tibco_spotfire"
        ],
        2024: [
            "alteryx", "amazon_quicksight", "excel_planilha_apenas", "grafana", "looker",
            "looker_studio", "metabase", "nenhuma_ferramenta_bi", "oracle_bi", "pbi",
            "pentaho", "qlik_view_sense", "redash", "salesforce_einstein_analytics",
            "sap_business_objects", "sas_visual_analytics", "superset", "tableau"
        ],
        2025: [
            "alteryx", "amazon_quicksight", "excel_planilha_apenas", "grafana", "looker",
            "looker_studio", "metabase", "nenhuma_ferramenta_bi", "oracle_bi", "pbi",
            "pentaho", "qlik_view_sense", "redash", "salesforce_einstein_analytics",
            "sap_business_objects", "sas_visual_analytics", "superset", "tableau"
        ],
    },
    "fontes_dados": {
        2023: [
            "audio", "audio_1", "banco_no_sql", "banco_no_sql_1", "banco_relacional",
            "banco_relacional_1", "georefenciados", "georefenciados_1", "img", "img_1",
            "planilha", "planilha_1", "text_doc", "text_doc_1", "video", "video_1"
        ],
        2024: [
            "audio", "audio_fonte", "banco_no_sql", "banco_no_sql_fonte",
            "banco_relacional", "banco_relacional_fonte", "georefenciados",
            "georeferenciados_fonte", "img", "img_fonte", "planilha", "planilha_fonte",
            "text_doc", "text_doc_fonte", "video", "video_fonte"
        ],
        2025: [
            "audio", "banco_no_sql", "banco_relacional", "georefenciados", "img",
            "planilha", "text_doc", "video"
        ],
    },
    "linguagens": {
        2023: [
            "ccc", "java", "js", "julia", "matlab", "net", "php", "python", "r", "rust",
            "sas_stat", "scala", "sql", "vba"
        ],
        2024: [
            "ccc", "java", "js", "julia", "matlab", "net", "php", "python", "r", "rust",
            "sas_stat", "scala", "sql", "vba"
        ],
        2025: [
            "DAX", "ccc", "julia", "python", "r", "rust", "scala", "sql", "vba"
        ],
    },
    "motivos_insatisfacao_2023": {
        2023: [
            "clima_trabalho_ruim", "falta_maturidade_analitica_empresa",
            "falta_oportunidade_cresc", "mais_beneficios", "rel_ruim_lider_gestor",
            "salario_atual_n_corresponde_mercado", "trab_outra_area_atuacao"
        ],
        2024: [],
        2025: [],
    },
    "percepcao_carreira": {
        2023: [
            "aprov_processos_seletivos_entrevistas", "atencao_opiniao_ideias",
            "nvl_cobranca_e_stress_trab", "oportunidades_progresso_carreira",
            "qtd_oportunidades_vagas_emprego_receb",
            "rel_outros_membros_empresa_em_trabalho",
            "rel_outros_membros_empresa_integracao_fora_trab",
            "senioridade_vagas_recebidas_rel_experiencia", "vel_progressao_carreira"
        ],
        2024: [
            "aprov_processos_seletivos_entrevistas", "atencao_opiniao_ideias",
            "nvl_cobranca_e_stress_trab", "oportunidades_progresso_carreira",
            "qtd_oportunidades_vagas_emprego_receb",
            "rel_outros_membros_empresa_em_trabalho",
            "rel_outros_membros_empresa_integracao_fora_trab",
            "senioridade_vagas_recebidas_rel_experiencia", "vel_progressao_carreira"
        ],
        2025: [
            "aprov_processos_seletivos_entrevistas", "atencao_opiniao_ideias",
            "nvl_cobranca_e_stress_trab", "oportunidades_progresso_carreira",
            "qtd_oportunidades_vagas_emprego_receb",
            "rel_outros_membros_empresa_em_trabalho",
            "rel_outros_membros_empresa_integracao_fora_trab",
            "senioridade_vagas_recebidas_rel_experiencia", "vel_progressao_carreira"
        ],
    },
    "uso_ia_generativa": {
        2023: [
            "colaboradores_uso_ia_descentra_independ",
            "colaboradores_uso_ia_descentra_independ_1", "dados_empresa_nao_prep_ia_gen",
            "dev_usando_copilot", "dev_usando_copilot_1",
            "direcionamento_centralizado_ia_generativa",
            "direcionamento_centralizado_ia_generativa_1", "ia_gen_llm_melhorar_prod_ext",
            "ia_gen_llm_melhorar_prod_int_colaboradores",
            "ia_gen_llm_melhorar_prod_int_colaboradores_1",
            "ia_gen_llm_principal_frente_neg", "ia_gen_llm_principal_frente_neg_1",
            "ia_llm_empresa_prod_externo", "ia_llm_nao_prioridade",
            "ia_llm_nao_prioridade_1", "nao_uso_ia_gen_produtividade",
            "retorno_roi_nao_comprovado_ia_gen", "sem_opiniao_llm_ia_generativa",
            "sem_opiniao_llm_ia_generativa_1", "uso_copilot",
            "uso_ia_gen_gratuita_produtividade", "uso_pago_ia_gen_empresa_paga",
            "uso_pago_ia_gen_produtividade"
        ],
        2024: [
            "colaboradores_uso_ia_descentra_independ", "dados_empresa_nao_prep_ia_gen",
            "dev_usando_copilot", "direcionamento_centralizado_ia_generativa",
            "ia_gen_llm_melhorar_prod_ext", "ia_gen_llm_melhorar_prod_int_colaboradores",
            "ia_gen_llm_principal_frente_neg",
            "ia_llm_empresa_descentralizada_independente", "ia_llm_empresa_frente_negoc",
            "ia_llm_empresa_nao_prioridade", "ia_llm_empresa_prod_externo",
            "ia_llm_empresa_prod_interno", "ia_llm_empresa_sem_opiniao",
            "ia_llm_empresa_uso_centralizado", "ia_llm_empresa_uso_copilot",
            "ia_llm_nao_prioridade", "nao_uso_ia_gen_produtividade",
            "retorno_roi_nao_comprovado_ia_gen", "sem_opiniao_llm_ia_generativa",
            "uso_copilot", "uso_ia_gen_gratuita_produtividade",
            "uso_pago_ia_gen_empresa_paga", "uso_pago_ia_gen_produtividade"
        ],
        2025: [
            "colaboradores_uso_ia_descentra_independ", "dados_empresa_nao_prep_ia_gen",
            "dev_usando_copilot", "direcionamento_centralizado_ia_generativa",
            "ia_gen_llm_melhorar_prod_ext", "ia_gen_llm_melhorar_prod_int_colaboradores",
            "ia_gen_llm_principal_frente_neg",
            "ia_llm_empresa_descentralizada_independente", "ia_llm_empresa_frente_negoc",
            "ia_llm_empresa_nao_prioridade", "ia_llm_empresa_prod_externo",
            "ia_llm_empresa_prod_interno", "ia_llm_empresa_sem_opiniao",
            "ia_llm_empresa_uso_centralizado", "ia_llm_empresa_uso_copilot",
            "ia_llm_nao_prioridade", "nao_uso_ia_gen_produtividade",
            "retorno_roi_nao_comprovado_ia_gen", "sem_opiniao_llm_ia_generativa",
            "uso_copilot", "uso_ia_gen_gratuita_produtividade",
            "uso_pago_ia_gen_empresa_paga", "uso_pago_ia_gen_produtividade"
        ],
    },
}

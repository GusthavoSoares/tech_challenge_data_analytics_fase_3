"""
Camada GOLD: base compartilhada pelas 7 perguntas de negócio.

TC3 Grupo 21. Combinado do grupo: **cada um constrói a Gold que alimenta as
SUAS perguntas**, para não haver dois donos na mesma tabela. Este módulo é a
parte comum, leitura da Silver, dimensões conformadas e os utilitários que
evitam os erros de contagem que a base cobra caro.

Quem for escrever a Gold das suas perguntas: copie
`job_gold_pN_template.py`, importe daqui e escreva só as suas agregações.

Autor: Caio Bosnic (dono da Silver e da Gold base)
"""

import functools
import operator
import os

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql import types as T

# --------------------------------------------------------------------------- #
# caminhos: mesma ideia da Silver, reaproveitando o leitor de parâmetro dela
# --------------------------------------------------------------------------- #

from config_silver import parametro  # noqa: E402

BUCKET = parametro("TC3_BUCKET", "s3://tc3-grupo21-datalake")
PATH_SILVER = parametro("TC3_PATH_SILVER", f"{BUCKET}/silver/state_data")
PATH_GOLD = parametro("TC3_PATH_GOLD", f"{BUCKET}/gold")
DATABASE_GLUE = parametro("TC3_DATABASE", "state_of_data")

LINHAS_SILVER = 14002


def sessao(nome="tc3-gold"):
    spark = (
        SparkSession.builder
        .appName(nome)
        .config("spark.sql.sources.partitionOverwriteMode", "dynamic")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")
    return spark


def ler_silver(spark: SparkSession) -> DataFrame:
    """
    Lê a Silver e confere o contrato antes de deixar qualquer um agregar em
    cima. Se a Silver mudar de tamanho sem aviso, a Gold para aqui em vez de
    publicar número errado.
    """
    df = spark.read.parquet(PATH_SILVER)
    n = df.count()
    if n != LINHAS_SILVER:
        raise ValueError(
            f"Silver com {n} linhas, esperado {LINHAS_SILVER}. "
            f"Confirme com o Caio antes de rodar a Gold."
        )
    return df


# --------------------------------------------------------------------------- #
# AS TRÊS ARMADILHAS DA BASE
# --------------------------------------------------------------------------- #
# Documentadas em docs/CONTRATO_SILVER.md e docs/VALIDACAO_BRONZE.md. As três
# produzem número errado SEM dar erro: por isso viraram função, para ninguém
# reimplementar torto.


def base_da_pergunta(df: DataFrame, coluna: str) -> DataFrame:
    """
    ARMADILHA 1, o denominador.

    Boa parte dos blocos da pesquisa é condicional: só aparece para quem se
    encaixa. `ia_gen_prioridade` e `barreiras_ia_generativa`, por exemplo, são
    respondidas SÓ POR GESTORES: 2.593 de 14.002.

    Calcular percentual sobre a base inteira quando 2.593 viram a pergunta
    reporta 5% onde o número real é 28%. Sempre restrinja à população que
    respondeu ANTES de dividir.

        base_da_pergunta(silver, "ia_gen_prioridade")   # 2.593 linhas
    """
    return df.filter(F.col(coluna).isNotNull())


def apenas_comparavel(df: DataFrame) -> DataFrame:
    """
    ARMADILHA 2, a série temporal.

    1.282 linhas têm categoria que não existe nas três edições
    (`Especialista/Staff+` nasceu em 2025, arquiteto virou cargo separado em
    2024, etc.). Sem o filtro, opção nova de questionário vira "crescimento".

    Use em QUALQUER comparação entre anos. Para retrato de um ano só, não use.
    """
    return df.filter(F.col("serie_comparavel"))


def marcou(coluna: str, opcao: str):
    """
    ARMADILHA 3, múltipla escolha.

    Os 17 grupos são string separada por ", ". `LIKE '%python%'` casaria com
    `pythonic` se existisse; esta função casa a opção inteira, respeitando o
    separador.

        df.filter(marcou("linguagens", "python"))
    """
    alvo = F.concat(F.lit(", "), F.col(coluna), F.lit(", "))
    return alvo.contains(f", {opcao}, ")


# --------------------------------------------------------------------------- #
# ARMADILHA 4: a coluna que junta três perguntas
# --------------------------------------------------------------------------- #

# `uso_ia_generativa` NÃO é uma pergunta. É a fusão de TRÊS, que o de-para
# empilhou na mesma coluna porque a origem reaproveita o mesmo bloco de opções:
#
#   IA_PESSOAL   como a PESSOA usa IA no dia a dia
#   IA_EMPRESA   como a EMPRESA organiza o uso
#   IA_GESTOR    a visão do gestor sobre o uso na empresa
#
# Gestor nunca vê a pergunta de uso pessoal, e mesmo assim tem a coluna
# preenchida, pelas opções de gestor. `base_da_pergunta` nesta coluna inclui
# 2.547 gestores que nunca foram perguntados sobre uso próprio.

IA_PESSOAL = [
    "uso_ia_gen_gratuita_produtividade", "uso_pago_ia_gen_empresa_paga",
    "uso_pago_ia_gen_produtividade", "uso_copilot", "nao_uso_ia_gen_produtividade",
]
IA_EMPRESA = [
    # 2024-2025 e 2025-2026
    "ia_llm_empresa_descentralizada_independente", "ia_llm_empresa_uso_centralizado",
    "ia_llm_empresa_uso_copilot", "ia_llm_empresa_prod_interno",
    "ia_llm_empresa_prod_externo", "ia_llm_empresa_frente_negoc",
    "ia_llm_empresa_nao_prioridade", "ia_llm_empresa_sem_opiniao",
    # 2023-2024, a mesma pergunta com o sufixo `_1`
    "colaboradores_uso_ia_descentra_independ_1",
    "direcionamento_centralizado_ia_generativa_1", "dev_usando_copilot_1",
    "ia_gen_llm_melhorar_prod_int_colaboradores_1",
    "ia_gen_llm_principal_frente_neg_1", "ia_llm_nao_prioridade_1",
    "sem_opiniao_llm_ia_generativa_1",
]
IA_GESTOR = [
    "colaboradores_uso_ia_descentra_independ", "direcionamento_centralizado_ia_generativa",
    "dev_usando_copilot", "ia_gen_llm_melhorar_prod_int_colaboradores",
    "ia_gen_llm_melhorar_prod_ext", "ia_gen_llm_principal_frente_neg",
    "ia_llm_nao_prioridade", "sem_opiniao_llm_ia_generativa",
    "dados_empresa_nao_prep_ia_gen", "retorno_roi_nao_comprovado_ia_gen",
]


def _marcou_alguma(coluna: str, opcoes):
    """Condição: marcou pelo menos uma das opções da lista."""
    return functools.reduce(operator.or_, [marcou(coluna, o) for o in opcoes])


def base_uso_ia_pessoal(df: DataFrame) -> DataFrame:
    """
    Denominador correto da adoção INDIVIDUAL de IA generativa.

    Só quem marcou ao menos uma opção de uso pessoal, ou seja, quem de fato viu
    a pergunta: 9.494 respondentes, adoção de 89,2%.

    `base_da_pergunta(df, "uso_ia_generativa")` devolveria 12.041 e 91,5%, e os
    2.547 de diferença são gestores que responderam só o bloco deles.
    """
    return df.filter(_marcou_alguma("uso_ia_generativa", IA_PESSOAL))


def base_uso_ia_empresa(df: DataFrame) -> DataFrame:
    """
    Denominador de "como a empresa organiza o uso de IA".

    Mesma lógica de `base_uso_ia_pessoal`, do outro lado: só quem marcou opção
    do bloco de empresa. Sem isso, o percentual é dividido por gente que nunca
    viu essa pergunta.
    """
    return df.filter(_marcou_alguma("uso_ia_generativa", IA_EMPRESA))


def usa_ia_pessoal():
    """
    Condição de "usa IA", para aplicar sobre `base_uso_ia_pessoal`.

    Dentro dessa base, usa IA quem NÃO marcou explicitamente que não usa.
    """
    return ~marcou("uso_ia_generativa", "nao_uso_ia_gen_produtividade")


def pct(numerador, denominador, casas=1):
    """Percentual com denominador protegido, divisão por zero vira NULL."""
    return F.when(denominador > 0,
                  F.round(100.0 * numerador / denominador, casas))


def indicador(df: DataFrame, condicao, por=("ano_pesquisa",), rotulo="indicador"):
    """
    Contagem + percentual sobre a base já restringida, agrupado por `por`.

    O denominador é o número de linhas de `df` no grupo, por isso `df` tem de
    vir de `base_da_pergunta`, e não da Silver inteira.
    """
    por = list(por)
    return (
        df.groupBy(*por)
          .agg(F.count("*").alias("base"),
               F.count(F.when(condicao, 1)).alias("qtd"))
          .withColumn("pct", pct(F.col("qtd"), F.col("base")))
          .withColumn("indicador", F.lit(rotulo))
          .orderBy(*por)
    )


# --------------------------------------------------------------------------- #
# dimensões conformadas: comuns às 7 perguntas
# --------------------------------------------------------------------------- #

ORDEM_SENIORIDADE = ["Junior", "Pleno", "Senior", "Especialista/Staff+"]

ORDEM_TEMPO_EXP = [
    "Nao_tenho_experiencia_na_area_de_dados", "Menos_de_1_ano", "de_1_a_2_anos",
    "de_3_a_4_anos", "de_4_a_6_anos", "de_5_a_6_anos", "de_7_a_10_anos",
    "Mais_de_10_anos",
]


def _dim(spark, valores, colunas):
    return spark.createDataFrame(
        [(i + 1,) + tuple(v if isinstance(v, tuple) else (v,)) for i, v in enumerate(valores)],
        ["sk"] + colunas,
    )


def dim_tempo(spark) -> DataFrame:
    """A pesquisa é anual, o grão de tempo é a edição, não a data."""
    return spark.createDataFrame(
        [(2023, "2023-2024", "fim de 2023"),
         (2024, "2024-2025", "out-dez/2024"),
         (2025, "2025-2026", "out-dez/2025")],
        ["ano_pesquisa", "edicao", "periodo_coleta"],
    )


def dim_senioridade(spark) -> DataFrame:
    """Ordem explícita, sem ela o gráfico sai em ordem alfabética."""
    return _dim(spark, ORDEM_SENIORIDADE, ["nivel_senioridade"]) \
        .withColumnRenamed("sk", "ordem")


def dim_tempo_experiencia(spark) -> DataFrame:
    return _dim(spark, ORDEM_TEMPO_EXP, ["tempo_exp_dados"]) \
        .withColumnRenamed("sk", "ordem")


def dim_faixa_salarial(spark) -> DataFrame:
    """Faixa, ordem e ponto médio, para o eixo sair na ordem certa."""
    from config_silver import ORDEM_FAIXA_SALARIAL, PONTO_MEDIO_SALARIAL
    return spark.createDataFrame(
        [(i + 1, f, float(PONTO_MEDIO_SALARIAL[f]))
         for i, f in enumerate(ORDEM_FAIXA_SALARIAL)],
        ["ordem", "faixa_salarial", "ponto_medio"],
    )


def dim_geografia(spark, silver: DataFrame) -> DataFrame:
    """
    UF e região de MORADIA, derivadas de `estado`.

    ⚠️ Nunca montar geografia a partir da coluna `uf` da Bronze: em 2025-2026
    ela é o estado de nascimento. Ver VALIDACAO_BRONZE.md §3.1.
    """
    return (
        silver.filter(F.col("uf_moradia").isNotNull())
              .select(F.col("uf_moradia").alias("uf"),
                      F.col("estado_moradia").alias("estado"),
                      F.col("regiao_moradia").alias("regiao"))
              .distinct()
              .orderBy("regiao", "uf")
    )


# --------------------------------------------------------------------------- #
# escrita
# --------------------------------------------------------------------------- #


def gravar(df: DataFrame, tabela: str, particao=None, mostrar=True):
    """
    Grava uma tabela da Gold. Sem partição para as pequenas, particionar uma
    tabela de 30 linhas só cria arquivo pequeno à toa.
    """
    caminho = f"{PATH_GOLD}/{tabela}"
    escrita = df.coalesce(1).write.mode("overwrite")
    if particao:
        escrita = escrita.partitionBy(particao)
    escrita.parquet(caminho)
    print(f"[OK] {tabela}: {df.count()} linhas -> {caminho}")
    if mostrar:
        df.show(10, truncate=44)
    return caminho

"""
Camada SILVER: união harmonizada das 3 edições do State of Data Brasil.

Grão de saída: 1 linha por respondente por edição.
Entrada:  bronze_dw_state_data_{2023_2024, 2024_2025, 2025_2026}  (Parquet, tudo string)
Saída:    silver_dw_fat_respondente                               (Parquet, particionado por ano_pesquisa)

O que esta camada faz (e a Bronze não pode fazer):
  1. injeta `ano_pesquisa` a partir da ORIGEM do arquivo, nenhuma base tem
     coluna de edição;
  2. cria `sk_respondente`, porque a chave primária muda de nome entre edições
     (`id` em 2023-2024, `token_user` nas outras);
  3. remove linhas duplicadas (duplicatas exatas, conferidas na validação);
  4. renomeia as colunas para o padrão canônico do de-para;
  5. tipa de forma consciente, a Bronze é toda string por decisão;
  6. normaliza booleano, porque 2024 grava TRUE/FALSE onde as outras gravam 1/0;
  7. corrige rótulos com erro de digitação na origem;
  8. NÃO agrega nada, agregação é Gold.

Executa como Glue Job (PySpark). Para rodar local, ver notebooks/03_silver_uniao.ipynb.

Autor: Caio Bosnic (Grupo 21)
"""

import sys

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql import types as T

from normalizacao_bronze import normalizar_valores, renomear_colunas  # noqa: E402
from config_silver import (
    CATEGORIAS_NAO_COMPARAVEIS,
    COLUNAS_BOOLEANAS,
    CORRECOES_ORIGEM,
    DATABASE_GLUE,
    DE_PARA_CATEGORIAS,
    DE_PARA_COLUNAS,
    EDICOES,
    FORMATO_DATA_ENVIO,
    COLUNAS_MULTIVALORADAS_TEXTO,
    GRUPOS_MULTIPLA_ESCOLHA,
    GRUPOS_NAO_COMPARAVEIS,
    ROTULOS_MULTIPLA_ESCOLHA,
    SEPARADOR_MULTIPLA_ESCOLHA,
    LAYOFF_AFETADO,
    LAYOFF_HOUVE,
    MAPA_BOOLEANO,
    PARTICAO_SILVER,
    PATH_BRONZE,
    PATH_SILVER,
    PONTO_MEDIO_SALARIAL,
    TABELA_SILVER,
    UF_PARA_REGIAO,
)

# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #


def _mapa_para_expr(coluna, mapa, default=None):
    """Traduz um dicionário Python em CASE WHEN, sem UDF (deixa o Catalyst otimizar)."""
    expr = F.lit(default) if default is None else F.lit(default)
    for origem, destino in mapa.items():
        expr = F.when(F.col(coluna) == F.lit(origem), F.lit(destino)).otherwise(expr)
    return expr


def _sigla_do_estado(coluna):
    """`Sao_Paulo_(SP)` -> `SP`. As três edições usam esse formato em `estado`."""
    return F.regexp_extract(F.col(coluna), r"\(([A-Z]{2})\)", 1)


def _nulo_se_vazio(coluna):
    limpo = F.trim(F.col(coluna))
    return F.when(limpo.isin("", "nan", "NaN", "NULL", "null", "-"), None).otherwise(limpo)


def _marcada(coluna):
    """True quando a opção de múltipla escolha foi marcada na origem."""
    return F.col(coluna).isin("1", "TRUE", "true", "True")


def consolidar_multipla_escolha(df: DataFrame, ano: int):
    """
    Converte cada grupo de colunas binárias em duas colunas.

        linguagens      "python, r, sql"
        qtd_linguagens  3

    Devolve a lista de expressões, para entrar no mesmo select do de-para.

    Distinção importante: NÃO respondeu (a pergunta não se aplicava a ele) é
    diferente de respondeu e não marcou nada. O primeiro vira NULL nas duas
    colunas; o segundo vira string vazia e zero. Somar zeros de quem nunca viu
    a pergunta é o tipo de erro que infla denominador e derruba percentual.
    """
    expressoes = []

    for grupo, por_ano in GRUPOS_MULTIPLA_ESCOLHA.items():
        colunas = [c for c in por_ano.get(ano, []) if c in df.columns]
        # O rótulo da opção é o CANÔNICO, não o nome da coluna de origem: o
        # nome muda entre edições para o mesmo conceito (`remuneracao_salario`
        # em 2023, `remuneracao_salario_1` em 2025). Ver config §2c.
        rotulo = ROTULOS_MULTIPLA_ESCOLHA.get(grupo, {}).get(ano, {})

        if not colunas:
            expressoes.append(F.lit(None).cast(T.StringType()).alias(grupo))
            expressoes.append(F.lit(None).cast(T.IntegerType()).alias(f"qtd_{grupo}"))
            continue

        # respondeu o bloco? basta uma das colunas do grupo estar preenchida
        respondeu = F.col(colunas[0]).isNotNull()
        for c in colunas[1:]:
            respondeu = respondeu | F.col(c).isNotNull()

        # concat_ws ignora NULL nativamente, então cada opção não marcada some
        # da lista sozinha. Evita array_compact, que só existe no Spark 3.4+
        # e o Glue 4.0 roda 3.3.
        lista = F.concat_ws(
            SEPARADOR_MULTIPLA_ESCOLHA,
            *[F.when(_marcada(c), F.lit(rotulo.get(c, c))) for c in colunas],
        )
        quantidade = sum(
            (F.when(_marcada(c), F.lit(1)).otherwise(F.lit(0)) for c in colunas),
            F.lit(0),
        )

        expressoes.append(F.when(respondeu, lista).alias(grupo))
        expressoes.append(
            F.when(respondeu, quantidade).cast(T.IntegerType()).alias(f"qtd_{grupo}")
        )

    return expressoes


# --------------------------------------------------------------------------- #
# leitura e harmonização de uma edição
# --------------------------------------------------------------------------- #


def ler_bronze(spark: SparkSession, ano: int) -> DataFrame:
    """
    Lê uma edição da Bronze e a deixa pronta para o de-para.

    ⚠️ A BRONZE É CRUA, E A NORMALIZAÇÃO ACONTECE AQUI.
    Renomear coluna e tirar acento de valor são trabalho desta camada, não da
    Bronze, que é cópia fidedigna da origem. As duas funções estão em
    `normalizacao_bronze.py`.

    O que chega é tudo string, é assim que a Bronze é gravada.
    """
    cfg = EDICOES[ano]
    caminho = f"{PATH_BRONZE}/{cfg['tabela_bronze']}/"
    df = spark.read.parquet(caminho)

    # Guarda de contrato: se a Bronze mudar de shape, o job para aqui em vez de
    # produzir uma Silver silenciosamente errada.
    n_linhas = df.count()
    if n_linhas != cfg["linhas_esperadas"]:
        raise ValueError(
            f"[{ano}] Bronze com {n_linhas} linhas, esperado {cfg['linhas_esperadas']}. "
            f"Confirme com o dono da Bronze antes de rodar a Silver."
        )
    n_colunas = len(df.columns)
    if n_colunas != cfg["colunas_esperadas"]:
        raise ValueError(
            f"[{ano}] Bronze com {n_colunas} colunas, esperado "
            f"{cfg['colunas_esperadas']}. A Bronze deve ser cópia fiel da origem: "
            f"nem coluna a mais, nem a menos."
        )

    df = renomear_colunas(df, ano)
    return normalizar_valores(df)


def harmonizar(df: DataFrame, ano: int) -> DataFrame:
    """Aplica o de-para e devolve o DataFrame no schema canônico da Silver."""
    cfg = EDICOES[ano]

    # 1) dedup: as duplicatas conferidas são linhas 100% idênticas
    df = df.dropDuplicates()

    selecao = []

    # 2) chave temporal injetada a partir da origem (achado: nenhuma base tem)
    selecao.append(F.lit(ano).cast(T.IntegerType()).alias("ano_pesquisa"))
    selecao.append(F.lit(cfg["edicao"]).alias("edicao"))

    # 3) demais colunas, pelo de-para
    for canonico, por_ano in DE_PARA_COLUNAS.items():
        origem = por_ano.get(ano)

        if origem is None or origem not in df.columns:
            # pergunta ausente nesta edição -> NULL explícito, nunca 0 nem ""
            selecao.append(F.lit(None).cast(T.StringType()).alias(canonico))
            continue

        col = _nulo_se_vazio(origem)

        if canonico in CORRECOES_ORIGEM:
            for errado, certo in CORRECOES_ORIGEM[canonico].items():
                col = F.when(col == F.lit(errado), F.lit(certo)).otherwise(col)

        if canonico in DE_PARA_CATEGORIAS:
            for de, para in DE_PARA_CATEGORIAS[canonico].items():
                col = F.when(col == F.lit(de), F.lit(para)).otherwise(col)

        selecao.append(col.alias(canonico))

    # 4) as ~320 binárias viram 17 pares (lista, contagem)
    selecao.extend(consolidar_multipla_escolha(df, ano))

    return df.select(*selecao)


def tipar(df: DataFrame) -> DataFrame:
    """Tipagem consciente, o que a Bronze deliberadamente não fez."""

    # booleanos: resolve o TRUE/FALSE de 2024 contra o 1/0 das outras
    for c in COLUNAS_BOOLEANAS:
        df = df.withColumn(c, _mapa_para_expr(c, MAPA_BOOLEANO).cast(T.BooleanType()))

    df = (
        df
        .withColumn("idade", F.col("idade").cast(T.IntegerType()))
        .withColumn(
            "data_envio",
            F.to_timestamp(F.col("data_envio"), FORMATO_DATA_ENVIO),
        )
        # ponto médio da faixa, para permitir média na Gold
        .withColumn(
            "salario_medio_mensal",
            _mapa_para_expr("faixa_salarial", PONTO_MEDIO_SALARIAL).cast(T.DoubleType()),
        )
        # sigla derivada de `estado`: NUNCA da coluna `uf` da Bronze, que muda
        # de significado entre edições (2025: `uf` é onde nasceu, não onde mora)
        .withColumn("uf_moradia", _sigla_do_estado("estado_moradia"))
        .withColumn(
            "uf_origem",
            F.when(F.col("estado_origem").isNotNull(), _sigla_do_estado("estado_origem")),
        )
        .withColumn("pcd_flag", F.when(F.col("pcd") == "Sim", True)
                                 .when(F.col("pcd") == "Nao", False))
        # layoff tem 3 respostas, não 2: os dois flags abaixo separam
        # "houve na empresa" de "me atingiu", que são perguntas diferentes
        .withColumn("houve_layoff",
                    _mapa_para_expr("empresa_passou_layoff", LAYOFF_HOUVE).cast(T.BooleanType()))
        .withColumn("fui_afetado_layoff",
                    _mapa_para_expr("empresa_passou_layoff", LAYOFF_AFETADO).cast(T.BooleanType()))
    )

    # Campos que parecem resposta única e são múltipla escolha concatenada
    # (ver config §2d). Normaliza para o formato dos 17 grupos: opções
    # ordenadas, separador ", ". Ordenar resolve "Python,_SQL" x "SQL,_Python",
    # que sem isso viram duas categorias para a mesma resposta.
    for c in COLUNAS_MULTIVALORADAS_TEXTO:
        partes = F.split(F.col(c), ",")
        limpo = F.transform(partes, lambda x: F.regexp_replace(F.trim(x), "^_+", ""))
        limpo = F.filter(limpo, lambda x: x != "")
        df = (df
              .withColumn(f"qtd_{c}",
                          F.when(F.col(c).isNotNull(), F.size(limpo)).cast(T.IntegerType()))
              .withColumn(c, F.when(F.col(c).isNotNull(),
                                    F.array_join(F.array_sort(limpo),
                                                 SEPARADOR_MULTIPLA_ESCOLHA))))
    return df


def adicionar_surrogate_key(df: DataFrame) -> DataFrame:
    """
    sk_respondente = hash(ano_pesquisa + id_origem).

    Determinística: o mesmo respondente gera sempre a mesma sk, então reprocessar
    a Silver não invalida a Gold. Inclui o ano porque o mesmo token nunca se
    repete entre edições (interseção conferida = 0), mas o ano deixa a chave
    autoexplicativa e imune a uma edição futura que reaproveite tokens.
    """
    return df.withColumn(
        "sk_respondente",
        F.sha2(F.concat_ws("||", F.col("ano_pesquisa").cast("string"), F.col("id_origem")), 256),
    )


def marcar_comparabilidade(df: DataFrame) -> DataFrame:
    """
    Marca as linhas cujo valor só existe em parte das edições.

    Sem isso, uma categoria que nasceu em 2025 (ex.: senioridade
    "Especialista/Staff+") aparece como crescimento quando é, na verdade, opção
    nova de questionário.
    """
    condicoes = []
    for coluna, valores in CATEGORIAS_NAO_COMPARAVEIS.items():
        if coluna not in df.columns:
            continue
        for valor, anos in valores.items():
            condicoes.append((F.col(coluna) == F.lit(valor)) & (F.col("ano_pesquisa").isin(anos)))

    if not condicoes:
        return df.withColumn("serie_comparavel", F.lit(True))

    nao_comparavel = condicoes[0]
    for c in condicoes[1:]:
        nao_comparavel = nao_comparavel | c

    return df.withColumn("serie_comparavel", ~F.coalesce(nao_comparavel, F.lit(False)))


# --------------------------------------------------------------------------- #
# validações de saída (o job falha em vez de gravar Silver errada)
# --------------------------------------------------------------------------- #


def validar_silver(df: DataFrame) -> None:
    total = df.count()
    distintas = df.select("sk_respondente").distinct().count()
    if total != distintas:
        raise ValueError(f"sk_respondente não é única: {total} linhas / {distintas} chaves")

    nulos_ano = df.filter(F.col("ano_pesquisa").isNull()).count()
    if nulos_ano:
        raise ValueError(f"{nulos_ano} linhas sem ano_pesquisa")

    anos = {r[0] for r in df.select("ano_pesquisa").distinct().collect()}
    if anos != set(EDICOES):
        raise ValueError(f"Anos na Silver: {anos}. Esperado: {set(EDICOES)}")

    # a data de envio precisa cair no ano da edição: é a contraprova da injeção
    fora = (
        df.filter(F.col("data_envio").isNotNull())
          .filter(F.year("data_envio") != F.col("ano_pesquisa"))
          .count()
    )
    if fora:
        raise ValueError(f"{fora} linhas com data_envio fora do ano_pesquisa injetado")

    # Grupos de múltipla escolha que não existem nas três edições. Não marcam
    # a linha (isso derrubaria a base inteira): são ressalva de COLUNA, e
    # quem montar série temporal precisa saber.
    for grupo, anos_grupo in GRUPOS_NAO_COMPARAVEIS.items():
        print(f"[!] `{grupo}` só existe em {anos_grupo}, não usar em comparação entre anos.")

    print(f"[OK] Silver validada: {total} linhas, {len(anos)} edições, sk única.")


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #


def construir_silver(spark: SparkSession) -> DataFrame:
    partes = []
    for ano in sorted(EDICOES):
        bruto = ler_bronze(spark, ano)
        partes.append(harmonizar(bruto, ano))

    # unionByName: as partes já estão no schema canônico e na mesma ordem, mas
    # casar por nome torna o job imune a uma mudança de ordem no de-para.
    silver = partes[0]
    for parte in partes[1:]:
        silver = silver.unionByName(parte)

    silver = adicionar_surrogate_key(silver)
    silver = tipar(silver)
    silver = marcar_comparabilidade(silver)

    colunas = ["sk_respondente", "ano_pesquisa", "edicao", "id_origem", "data_envio"]
    colunas += [c for c in silver.columns if c not in colunas]
    return silver.select(*colunas)


def main() -> None:
    spark = (
        SparkSession.builder
        .appName("tc3-grupo21-silver")
        .config("spark.sql.sources.partitionOverwriteMode", "dynamic")
        .getOrCreate()
    )

    silver = construir_silver(spark)
    validar_silver(silver)

    (
        silver
        # Uma partição de saída por ano. Sem isso o Spark grava um arquivo por
        # partição interna (24 arquivos de ~580 linhas para 14 mil no total).
        # É o "small files problem": no S3 cada arquivo é um GET, e o Athena passa
        # mais tempo abrindo arquivo do que lendo dado. A base é pequena, então
        # um arquivo por ano é o tamanho certo.
        .repartition(PARTICAO_SILVER)
        .write
        .mode("overwrite")
        .partitionBy(PARTICAO_SILVER)
        .parquet(PATH_SILVER)
    )
    print(f"[OK] Gravado em {PATH_SILVER} (particionado por {PARTICAO_SILVER}).")
    print(f"[i] Catalogar como {DATABASE_GLUE}.{TABELA_SILVER} via crawler ou DDL no Athena.")

    # Sem `spark.stop()`: no Glue quem encerra o contexto é o próprio serviço,
    # e parar por conta própria pode cortar a entrega dos logs.


if __name__ == "__main__":
    # `main()` direto, sem `sys.exit()`. O Glue trata qualquer SystemExit vindo
    # do script como falha do job (Error Category: SYSTEM_EXIT_ERROR), mesmo
    # quando o código de saída é 0. Um `sys.exit(main())` com main retornando
    # None marca o job como Failed depois de ter feito o trabalho todo.
    main()

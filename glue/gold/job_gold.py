"""
Camada GOLD: modelo dimensional único do TC3.

    UMA Gold, que responde as SETE perguntas de negócio.

Star schema clássico: um fato no grão de respondente, dimensões conformadas e
uma bridge para as múltiplas escolhas. Não há uma Gold por pergunta, as
perguntas viram consulta no Athena ou medida DAX sobre este mesmo modelo.

    gold_dw_fat_profissionais       14.002 linhas · 1 por respondente por edição
    gold_dw_dim_tempo                    3 · a edição é o grão de tempo
    gold_dw_dim_geografia               27 · UF, estado e região (para o mapa)
    gold_dw_dim_cargo                   18 · cargo + família
    gold_dw_dim_senioridade              4 · com ordem
    gold_dw_dim_faixa_salarial          13 · com ordem, limites e ponto médio
    gold_dw_dim_setor                   21
    gold_dw_dim_formacao                 7 · com ordem
    gold_dw_dim_area_formacao           12
    gold_dw_dim_modelo_trabalho          4 · com flags de remoto e flexibilidade
    gold_dw_dim_genero                   4
    gold_dw_dim_tempo_experiencia        8 · com ordem
    gold_dw_dim_opcao                  529 · o catálogo de todas as opções
    gold_dw_bridge_respondente_opcao ~378k · liga o fato às opções marcadas

POR QUE A BRIDGE
Os 20 grupos de múltipla escolha vivem na Silver como string ("python, sql").
Isso é ótimo para ler e péssimo para relacionar. A bridge explode cada opção
em uma linha, e é ela que permite o Power BI filtrar "quem usa Python" sem
`CONTAINS` em medida. Basta um relacionamento.

POR QUE NÃO HÁ dim_calendario
A pesquisa é anual e não tem data de evento: o grão de tempo é a edição. Uma
tabela de datas com 1.095 linhas para 3 valores distintos só cria relacionamento
morto. Decisão registrada em DECISOES_E_ACHADOS.md.

Autor: Caio Bosnic (Grupo 21)
"""

import functools
import os
import sys

def _raiz_do_projeto():
    """
    Sobe a partir deste arquivo até achar a raiz (a pasta que contém `glue/`).

    Assim o import funciona de qualquer lugar: rodando o script direto, pelo
    notebook, ou com o Glue copiando os módulos para o mesmo diretório.
    """
    p = os.path.dirname(os.path.abspath(__file__))
    for _ in range(5):
        if os.path.isdir(os.path.join(p, "glue")):
            return p
        pai = os.path.dirname(p)
        if pai == p:
            break
        p = pai
    return None


_AQUI = os.path.dirname(os.path.abspath(__file__))
_RAIZ = _raiz_do_projeto()
for _p in [_AQUI, os.path.join(_AQUI, "..", "silver"),
           os.path.join(_RAIZ, "glue", "silver") if _RAIZ else None,
           os.path.join(_RAIZ, "glue", "gold") if _RAIZ else None]:
    if _p and os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)


from pyspark.sql import DataFrame  # noqa: E402
from pyspark.sql import functions as F  # noqa: E402
from pyspark.sql import types as T  # noqa: E402

import config_silver as scfg  # noqa: E402
import benchmark_externo as B  # noqa: E402
import dim_rotulos as R  # noqa: E402
import recomendacoes as REC  # noqa: E402
from gold_comum import (  # noqa: E402
    IA_EMPRESA, IA_GESTOR, IA_PESSOAL, gravar, ler_silver, sessao,
)
from grupos_multipla_escolha import GRUPOS_MULTIPLA_ESCOLHA  # noqa: E402

PREFIXO = "gold_dw_"

# Todos os campos que a bridge cobre: os 17 grupos binários mais as 3 colunas
# que pareciam resposta única e são múltipla escolha concatenada (config §2d).
GRUPOS_BRIDGE = list(GRUPOS_MULTIPLA_ESCOLHA) + list(scfg.COLUNAS_MULTIVALORADAS_TEXTO)


# --------------------------------------------------------------------------- #
# ⚠️ `uso_ia_generativa` NÃO É UMA PERGUNTA, SÃO TRÊS
# --------------------------------------------------------------------------- #
# A Silver agrupa por máscara de resposta e junta num grupo só três blocos que
# a pesquisa faz a públicos diferentes. Medido na bridge, opção por opção,
# contra `eh_gestor` do fato: a separação é limpa, sem uma única exceção.
#
#   uso_ia_pessoal   9.494 pessoas, TODAS não gestoras. "Como VOCÊ usa IA."
#   uso_ia_empresa   as MESMAS 9.494. "Como a empresa que você trabalha usa."
#   uso_ia_gestor    2.505 pessoas, TODAS gestoras. O bloco de estratégia.
#
# Enquanto os três eram um grupo só, `% de adoção` dividia tudo por 11.999, a
# união dos dois públicos, e os dois gráficos da página de IA mostravam a mesma
# lista de opções misturadas. É a mesma armadilha de denominador do resto do
# trabalho, só que dentro de um grupo.
#
# O SUFIXO `_1` DE 2023
# A pergunta sobre a empresa mudou de nome de coluna entre as edições: em
# 2023-2024 ela vem com sufixo `_1`, em 2024-2025 e 2025-2026 vem como
# `ia_llm_empresa_*`. Os rótulos são harmonizados em dim_rotulos para as três
# edições caírem na mesma barra, senão a série de 2023 aparece separada.

# As três listas de opções vivem em `gold_comum`, para que os jobs de análise
# usem exatamente as mesmas. Fonte única: se uma opção mudar de bloco, muda
# num lugar só.
_IA_PESSOAL, _IA_EMPRESA, _IA_GESTOR = IA_PESSOAL, IA_EMPRESA, IA_GESTOR

SUBGRUPO = {
    "uso_ia_generativa": {
        **{o: "uso_ia_pessoal" for o in _IA_PESSOAL},
        **{o: "uso_ia_empresa" for o in _IA_EMPRESA},
        **{o: "uso_ia_gestor" for o in _IA_GESTOR},
    },
}


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #


def _expr_mapa(coluna, mapa, default_col=True):
    """Dicionário Python -> CASE WHEN. Sem entrada no mapa, devolve o valor cru."""
    expr = F.col(coluna) if default_col else F.lit(None)
    for de, para in mapa.items():
        expr = F.when(F.col(coluna) == F.lit(de), F.lit(para)).otherwise(expr)
    return expr


def _expr_ordem(coluna, ordem):
    """Posição na lista; o que não está nela vai para o fim (999)."""
    expr = F.lit(999)
    for i, valor in enumerate(ordem, start=1):
        expr = F.when(F.col(coluna) == F.lit(valor), F.lit(i)).otherwise(expr)
    return expr


def _sk(*colunas):
    """
    Chave substituta determinística a partir dos atributos naturais.

    Hash em vez de sequencial de propósito: reprocessar a Gold não renumera
    nada, então um .pbix salvo continua apontando para as mesmas linhas.
    """
    return F.sha2(F.concat_ws("||", *[F.coalesce(F.col(c).cast("string"), F.lit("~"))
                                      for c in colunas]), 256).substr(1, 16)


def _dim_simples(silver, coluna, nome_valor, rotulos=None, ordem=None, extras=None):
    """Uma dimensão de atributo único: chave, valor original, rótulo e ordem."""
    d = (silver.filter(F.col(coluna).isNotNull())
               .select(F.col(coluna).alias(nome_valor))
               .distinct())
    d = d.withColumn(f"sk_{nome_valor}", _sk(nome_valor))
    d = d.withColumn("rotulo", _expr_mapa(nome_valor, rotulos or {}))
    if ordem:
        d = d.withColumn("ordem", _expr_ordem(nome_valor, ordem))
    for nome, expr in (extras or {}).items():
        d = d.withColumn(nome, expr)
    colunas = [f"sk_{nome_valor}", nome_valor, "rotulo"]
    colunas += [c for c in d.columns if c not in colunas]
    return d.select(*colunas).orderBy("ordem" if ordem else "rotulo")


COLUNAS_DE_EXIBICAO = {"rotulo", "estado_rotulo", "regiao", "pais", "familia",
                       "grupo_rotulo", "opcao_rotulo"}


def _acrescentar_nao_informado(spark, dim, nome_dim, sk_col):
    """
    Acrescenta à dimensão as linhas que representam ausência de resposta.

    Cada uma recebe rótulo próprio ("Gestor, sem cargo técnico"), chave fixa e
    ordem alta, para cair no fim de qualquer eixo ordenado.
    """
    linhas = NAO_INFORMADO.get(nome_dim)
    if not linhas:
        return dim
    campos = dim.columns
    novas = []
    for rotulo, slug, ordem in linhas:
        valores = {}
        for c in campos:
            if c == sk_col:
                valores[c] = f"ni_{slug}"
            elif c in COLUNAS_DE_EXIBICAO:
                # Colunas que aparecem em eixo ou filtro levam o rótulo legível.
                # Sem isto, o filtro de Região mostrava "nao_declarado".
                valores[c] = rotulo
            elif c == "ordem":
                valores[c] = ordem
            else:
                valores[c] = slug if dim.schema[c].dataType.simpleString() == "string" else None
        novas.append(tuple(valores[c] for c in campos))
    return dim.unionByName(spark.createDataFrame(novas, dim.schema))


# --------------------------------------------------------------------------- #
# dimensões
# --------------------------------------------------------------------------- #


def construir_dimensoes(spark, silver):
    d = {}

    # --- tempo: a edição é o grão. Sem calendário, de propósito. ---------
    d["dim_tempo"] = spark.createDataFrame(
        [(2023, "2023-2024", "fim de 2023", "2023-24"),
         (2024, "2024-2025", "out–dez/2024", "2024-25"),
         (2025, "2025-2026", "out–dez/2025", "2025-26")],
        ["ano_pesquisa", "edicao", "periodo_coleta", "rotulo"],
    )

    # --- geografia: UF é o que o Power BI geocodifica -------------------
    # ⚠️ Derivada de `estado`, nunca da coluna `uf` da Bronze: em 2025-2026
    # ela é o estado de NASCIMENTO. Ver VALIDACAO_BRONZE §3.1.
    d["dim_geografia"] = (
        silver.filter(F.col("uf_moradia").isNotNull() & (F.col("uf_moradia") != ""))
              .select(F.col("uf_moradia").alias("uf"),
                      F.col("estado_moradia").alias("estado"),
                      F.col("regiao_moradia").alias("regiao_bronze"))
              .distinct()
              .withColumn("sk_geografia", _sk("uf"))
              # A coluna da Bronze não cobre AC e RR. A sigla cobre.
              .withColumn("regiao", F.coalesce(
                  _expr_mapa("uf", scfg.UF_PARA_REGIAO, default_col=False),
                  F.col("regiao_bronze")))
              .drop("regiao_bronze")
              .withColumn("estado_rotulo",
                          F.regexp_replace(F.regexp_replace(F.col("estado"), r"_\([A-Z]{2}\)$", ""),
                                           "_", " "))
              .withColumn("pais", F.lit("Brasil"))
              .select("sk_geografia", "uf", "estado", "estado_rotulo", "regiao", "pais")
              .orderBy("regiao", "uf")
    )

    d["dim_cargo"] = _dim_simples(
        silver, "cargo_atual", "cargo", R.ROTULO_CARGO,
    ).withColumn("familia", _expr_mapa("rotulo", R.FAMILIA_CARGO))

    d["dim_senioridade"] = _dim_simples(
        silver, "nivel_senioridade", "senioridade",
        R.ROTULO_SENIORIDADE, R.ORDEM_SENIORIDADE,
    )

    d["dim_setor"] = _dim_simples(silver, "setor_empresa", "setor", R.ROTULO_SETOR)
    d["dim_genero"] = _dim_simples(silver, "genero", "genero_valor", R.ROTULO_GENERO)
    d["dim_area_formacao"] = _dim_simples(silver, "area_formacao", "area_formacao",
                                          R.ROTULO_AREA_FORMACAO)

    d["dim_formacao"] = _dim_simples(
        silver, "nivel_ensino", "nivel_ensino", R.ROTULO_ENSINO, R.ORDEM_ENSINO,
    )

    d["dim_tempo_experiencia"] = _dim_simples(
        silver, "tempo_exp_dados", "tempo_experiencia",
        R.ROTULO_TEMPO_EXPERIENCIA, R.ORDEM_TEMPO_EXPERIENCIA,
    )

    # --- modelo de trabalho, com os flags que a análise usa -------------
    d["dim_modelo_trabalho"] = _dim_simples(
        silver, "forma_trabalho", "modelo_trabalho", R.ROTULO_MODELO_TRABALHO,
        extras={
            "eh_remoto": F.col("modelo_trabalho") == "Modelo_100%_remoto",
            "eh_presencial": F.col("modelo_trabalho") == "Modelo_100%_presencial",
            # A distinção que explica 7 pontos de satisfação: ter ou não
            # autonomia sobre QUANDO ir ao escritório.
            "tem_autonomia": F.col("modelo_trabalho").isin(
                "Modelo_100%_remoto",
                "Modelo_hibrido_flexivel_(o_funcionario_tem_liberdade_para_escolher"
                "_quando_estar_no_escritorio_presencialmente)"),
        },
    )

    # --- faixa salarial: ordem, limites e ponto médio --------------------
    linhas = [(v, R.FAIXA_SALARIAL[v][0], i + 1, R.FAIXA_SALARIAL[v][1],
               R.FAIXA_SALARIAL[v][2], float(R.FAIXA_SALARIAL[v][3]))
              for i, v in enumerate(R.FAIXA_SALARIAL)]
    esquema = T.StructType([
        T.StructField("faixa_salarial", T.StringType()),
        T.StructField("rotulo", T.StringType()),
        T.StructField("ordem", T.IntegerType()),
        T.StructField("limite_inferior", T.IntegerType()),
        T.StructField("limite_superior", T.IntegerType(), True),
        T.StructField("ponto_medio", T.DoubleType()),
    ])
    d["dim_faixa_salarial"] = (
        spark.createDataFrame(linhas, esquema)
             .withColumn("sk_faixa_salarial", _sk("faixa_salarial"))
             .select("sk_faixa_salarial", "faixa_salarial", "rotulo", "ordem",
                     "limite_inferior", "limite_superior", "ponto_medio")
    )

    # --- benchmark externo: contexto de mercado para os visuais ---------
    # Não vem da Silver. São referências de fontes independentes, conferidas
    # uma a uma na origem, para validar, delimitar ou complementar o nosso
    # número. Ver glue/gold/benchmark_externo.py.
    esquema_bm = T.StructType([
        T.StructField("indicador", T.StringType()),
        T.StructField("valor", T.DoubleType()),
        T.StructField("unidade", T.StringType()),
        T.StructField("fonte", T.StringType()),
        T.StructField("ano_referencia", T.IntegerType()),
        T.StructField("publicado_em", T.StringType()),
        T.StructField("populacao", T.StringType()),
        T.StructField("amostra", T.IntegerType(), True),
        T.StructField("uso", T.StringType()),
        T.StructField("nosso_indicador", T.StringType(), True),
        T.StructField("nosso_valor", T.DoubleType(), True),
        T.StructField("leitura", T.StringType()),
        T.StructField("ressalva", T.StringType(), True),
        T.StructField("ressalva_curta", T.StringType(), True),
        T.StructField("url", T.StringType()),
        T.StructField("diferenca_pct", T.DoubleType(), True),
        # Versões em texto: célula vazia numa tabela de fontes lê como
        # descuido, e "não divulgada" é a informação correta.
        T.StructField("amostra_texto", T.StringType(), True),
        T.StructField("comparacao", T.StringType(), True),
        T.StructField("diferenca_texto", T.StringType(), True),
        T.StructField("valor_texto", T.StringType(), True),
    ])
    linhas_bm = [tuple(r[c.name] for c in esquema_bm.fields) for r in B.como_tabela()]
    d["dim_benchmark"] = (
        spark.createDataFrame(linhas_bm, esquema_bm)
             .withColumn("sk_benchmark", _sk("indicador", "fonte"))
             .select("sk_benchmark", *[c.name for c in esquema_bm.fields])
             .orderBy("uso", "indicador")
    )

    # --- recomendações: a síntese da página de Oportunidades -------------
    # Também sem relacionamento com o fato. É a leitura que o grupo faz dos
    # próprios números, com o indicador e a base ao lado de cada decisão.
    esquema_rec = T.StructType([
        T.StructField("ordem", T.IntegerType()),
        T.StructField("decisao", T.StringType()),
        T.StructField("por_que", T.StringType()),
        T.StructField("indicador", T.StringType()),
        # ⚠️ `valor_indicador`, e não `valor`: ver o cabeçalho de recomendacoes.py.
        T.StructField("valor_indicador", T.StringType()),
        T.StructField("base", T.StringType()),
        T.StructField("onde_ver", T.StringType()),
    ])
    linhas_rec = [tuple(r[c.name] for c in esquema_rec.fields) for r in REC.como_tabela()]
    d["dim_recomendacao"] = (
        spark.createDataFrame(linhas_rec, esquema_rec)
             .withColumn("sk_recomendacao", _sk("ordem"))
             .select("sk_recomendacao", *[c.name for c in esquema_rec.fields])
             .orderBy("ordem")
    )

    for nome_dim, sk_col in [("dim_cargo", "sk_cargo"),
                            ("dim_senioridade", "sk_senioridade"),
                            ("dim_setor", "sk_setor"),
                            ("dim_geografia", "sk_geografia"),
                            ("dim_modelo_trabalho", "sk_modelo_trabalho"),
                            ("dim_faixa_salarial", "sk_faixa_salarial"),
                            ("dim_tempo_experiencia", "sk_tempo_experiencia"),
                            ("dim_area_formacao", "sk_area_formacao")]:
        d[nome_dim] = _acrescentar_nao_informado(spark, d[nome_dim], nome_dim, sk_col)
    return d


# --------------------------------------------------------------------------- #
# dim_opcao + bridge: o que resolve as múltiplas escolhas
# --------------------------------------------------------------------------- #


def construir_bridge(silver):
    """
    Explode os 20 grupos em (sk_respondente, sk_opcao).

    Só entram linhas de quem MARCOU a opção. Quem não respondeu o bloco não
    aparece, e isso é intencional: a contagem de uma opção nunca deve incluir
    quem nunca viu a pergunta.
    """
    partes = []
    for grupo in GRUPOS_BRIDGE:
        if grupo not in silver.columns:
            continue
        partes.append(
            silver.filter(F.col(grupo).isNotNull() & (F.col(grupo) != ""))
                  .select("sk_respondente", "ano_pesquisa",
                          F.lit(grupo).alias("grupo"),
                          F.explode(F.split(F.col(grupo),
                                            scfg.SEPARADOR_MULTIPLA_ESCOLHA)).alias("opcao"))
        )

    bridge = partes[0]
    for p in partes[1:]:
        bridge = bridge.unionByName(p)
    bridge = bridge.withColumn("opcao", F.trim(F.col("opcao"))).filter(F.col("opcao") != "")

    # Divide os grupos que a Silver juntou por máscara e que na verdade são mais
    # de uma pergunta. Ver SUBGRUPO no topo do arquivo: sem isso o denominador
    # de `% de adoção` soma dois públicos que nunca viram a mesma tela.
    for grupo, mapa in SUBGRUPO.items():
        novo = _expr_mapa("opcao", mapa, default_col=False)
        bridge = bridge.withColumn(
            "grupo", F.when(F.col("grupo") == grupo, F.coalesce(novo, F.col("grupo")))
                      .otherwise(F.col("grupo")))

    dim_opcao = (
        bridge.select("grupo", "opcao").distinct()
              .withColumn("sk_opcao", _sk("grupo", "opcao"))
              .withColumn("opcao_rotulo",
                          _expr_mapa("opcao",
                                     {**R.ROTULO_TECNOLOGIA, **R.ROTULO_OPCAO_EXTRA}))
              .withColumn("grupo_rotulo", _expr_mapa("grupo", R.ROTULO_GRUPO))
              # Marca o grupo cujo rótulo não harmoniza entre edições: quem
              # montar série temporal precisa saber. Ver config §2c.
              .withColumn("comparavel_entre_anos",
                          ~F.col("grupo").isin(scfg.GRUPOS_ROTULO_NAO_HARMONIZADO))
              .select("sk_opcao", "grupo", "grupo_rotulo", "opcao", "opcao_rotulo",
                      "comparavel_entre_anos")
              .orderBy("grupo", "opcao")
    )

    bridge = (bridge.join(dim_opcao.select("sk_opcao", "grupo", "opcao"),
                          ["grupo", "opcao"])
                    .select("sk_respondente", "sk_opcao", "ano_pesquisa"))

    return dim_opcao, bridge


# --------------------------------------------------------------------------- #
# fato
# --------------------------------------------------------------------------- #


def construir_fato(silver: DataFrame, dims: dict) -> DataFrame:
    """
    Grão: 1 respondente por edição. Mesmo grão da Silver, a Gold aqui não
    agrega, ela CONFORMA. As agregações são medidas no Power BI e consultas no
    Athena, não tabelas materializadas.
    """
    f = silver

    ligacoes = [
        ("dim_cargo", "cargo_atual", "cargo", "sk_cargo"),
        ("dim_senioridade", "nivel_senioridade", "senioridade", "sk_senioridade"),
        ("dim_setor", "setor_empresa", "setor", "sk_setor"),
        ("dim_genero", "genero", "genero_valor", "sk_genero_valor"),
        ("dim_formacao", "nivel_ensino", "nivel_ensino", "sk_nivel_ensino"),
        ("dim_area_formacao", "area_formacao", "area_formacao", "sk_area_formacao"),
        ("dim_modelo_trabalho", "forma_trabalho", "modelo_trabalho", "sk_modelo_trabalho"),
        ("dim_tempo_experiencia", "tempo_exp_dados", "tempo_experiencia", "sk_tempo_experiencia"),
        ("dim_faixa_salarial", "faixa_salarial", "faixa_salarial", "sk_faixa_salarial"),
    ]
    for nome_dim, col_fato, col_dim, col_sk in ligacoes:
        d = dims[nome_dim].select(F.col(col_dim).alias("_j"), F.col(col_sk).alias(col_sk))
        f = f.join(d, f[col_fato] == d["_j"], "left").drop("_j")

    g = dims["dim_geografia"].select(F.col("uf").alias("_j"), "sk_geografia")
    f = f.join(g, f["uf_moradia"] == g["_j"], "left").drop("_j")

    # Flags derivadas: calculadas ANTES da projeção, porque dependem de
    # colunas da Silver que não entram no fato.
    f = (
        f
        # ⚠️ A PERGUNTA DE USO PESSOAL NÃO É FEITA A GESTOR.
        # ⚠️ A regra é "marcou alguma opção do bloco de USO PESSOAL", nunca
        # "a coluna do grupo está preenchida". `uso_ia_generativa` junta três
        # perguntas, e o gestor que respondeu só o bloco da empresa tem a
        # coluna preenchida sem nunca ter sido perguntado sobre uso próprio:
        # entraria como usuário de IA, inflando a base de 9.494 para 12.041 e
        # a taxa de 89,2% para 91,5%.
        .withColumn(
            "_opcoes_ia",
            F.transform(F.split(F.col("uso_ia_generativa"),
                                scfg.SEPARADOR_MULTIPLA_ESCOLHA), F.trim))
        .withColumn(
            "_respondeu_uso_pessoal",
            functools.reduce(
                lambda a, b: a | b,
                [F.array_contains(F.col("_opcoes_ia"), F.lit(o)) for o in _IA_PESSOAL]))
        .withColumn("usa_ia_generativa",
                    F.when(F.col("_respondeu_uso_pessoal"),
                           ~F.array_contains(F.col("_opcoes_ia"),
                                             F.lit("nao_uso_ia_gen_produtividade"))))
        .drop("_opcoes_ia", "_respondeu_uso_pessoal")
        .withColumn("respondeu_bloco_ia_empresa", F.col("ia_gen_prioridade").isNotNull())
        .withColumn("respondeu_bloco_maturidade", F.col("empresa_possui_datalake").isNotNull())
        # "Prioridade alta" são as duas respostas que começam com "Sim,". A
        # regra mora aqui, e não espalhada em medida DAX: assim o dashboard e
        # as tabelas de conferência contam a mesma coisa por construção.
        .withColumn("ia_prioridade_alta",
                    F.when(F.col("ia_gen_prioridade").isNotNull(),
                           F.col("ia_gen_prioridade").startswith(
                               R.PREFIXO_IA_PRIORIDADE_ALTA)))
    )

    # Migração: nasceu numa região e mora em outra. Fica nulo quando alguma
    # das pontas não foi declarada, para não contar ausência como "não mudou".
    # ⚠️ `regiao_origem` da Bronze NÃO é confiável: em parte das linhas traz a
    # macrorregião ("Sudeste") e em outra o estado por extenso ("Sao_Paulo_(SP)").
    # Comparada com `regiao_moradia`, ela faz todo respondente que declarou
    # estado parecer migrante: a taxa saía 75,9% quando o valor real é 20,7%.
    # A região de origem é derivada da sigla, mesma regra da de moradia.
    f = f.withColumn("regiao_origem_uf",
                     _expr_mapa("uf_origem", scfg.UF_PARA_REGIAO, default_col=False))
    f = f.withColumn(
        "mudou_regiao",
        F.when(F.col("regiao_origem_uf").isNotNull() & F.col("regiao_moradia").isNotNull(),
               F.col("regiao_origem_uf") != F.col("regiao_moradia")))

    # Rótulo dos atributos degenerados. Eles ficam no fato, mas vão parar em
    # eixo de gráfico, e a frase crua da pesquisa é ilegível ali.
    # Dois respondentes não declararam cor ou raça. Sem rótulo, a tabela de
    # recorte racial abre com duas linhas de categoria vazia.
    f = f.withColumn("cor_raca_etnia",
                     F.coalesce(F.col("cor_raca_etnia"), F.lit("nao_declarado")))
    for coluna, mapa in [("cor_raca_etnia", R.ROTULO_COR_RACA),
                         ("ia_gen_prioridade", R.ROTULO_IA_PRIORIDADE),
                         ("llms_bom_resultado", R.ROTULO_LLMS_RESULTADO),
                         ("empresa_passou_layoff", R.ROTULO_LAYOFF_EMPRESA)]:
        expr = F.col(coluna)
        for de, para in mapa.items():
            expr = F.when(F.col(coluna) == de, F.lit(para)).otherwise(expr)
        f = f.withColumn(coluna + "_rotulo", expr)

    colunas = [
        # chave e FKs
        "sk_respondente", "ano_pesquisa",
        "sk_geografia", "sk_cargo", "sk_senioridade", "sk_setor", "sk_genero_valor",
        "sk_nivel_ensino", "sk_area_formacao", "sk_modelo_trabalho",
        "sk_tempo_experiencia", "sk_faixa_salarial",

        # atributos degenerados: cardinalidade baixa demais para virar dimensão
        "edicao", "cor_raca_etnia", "cor_raca_etnia_rotulo",
        "pcd", "faixa_etaria",

        # origem geográfica: fica no fato, e não numa segunda dim_geografia,
        # porque só serve para responder "veio de fora?". Uma dimensão com
        # papel duplo criaria caminho ambíguo até o fato.
        "uf_origem", F.col("regiao_origem_uf").alias("regiao_origem"),
        "mudou_estado", "mudou_regiao",

        # métricas
        F.col("idade").alias("idade"),
        F.col("salario_medio_mensal").alias("salario_estimado"),

        # flags booleanas: o que a maioria das medidas conta
        "eh_gestor", "pcd_flag", "vive_brasil", "satisfeito_empresa",
        "empresa_possui_datalake", "empresa_possui_dw",
        "houve_layoff", "fui_afetado_layoff", "serie_comparavel",

        # respostas de escolha única que não viraram dimensão
        "ia_gen_prioridade", "ia_gen_prioridade_rotulo",
        "empresa_passou_layoff", "empresa_passou_layoff_rotulo",
        "llms_bom_resultado", "llms_bom_resultado_rotulo",

        # quantidades já calculadas na Silver
        *[c for c in silver.columns if c.startswith("qtd_")],

        # flags derivadas: uma coluna aqui evita repetir a mesma expressão
        # em 20 medidas DAX, e deixa o denominador explícito
        "usa_ia_generativa", "ia_prioridade_alta",
        "respondeu_bloco_ia_empresa", "respondeu_bloco_maturidade",

        # rastreabilidade até a origem
        "id_origem", "data_envio",
    ]

    f = f.select(*colunas)

    # ⚠️ MEMBRO EXPLÍCITO NO LUGAR DA CHAVE NULA
    # Sem isto, o Power BI cria "(Em branco)" e ele aparece no filtro, no eixo
    # e dentro das medidas. Com o membro nomeado, o dashboard mostra o motivo:
    # "Gestor" e "Fora da área" são respostas, não ausência de dado.
    # Cargo e senioridade têm dois motivos distintos de ausência, e o rótulo
    # precisa dizer qual: gestor não declara cargo técnico, e quem está fora da
    # área não declara nada de emprego.
    eh_gestor = F.col("eh_gestor") == True   # noqa: E712
    for coluna in ["sk_cargo", "sk_senioridade"]:
        slug = "gestor_sem_cargo" if coluna == "sk_cargo" else "gestor_sem_senioridade"
        f = f.withColumn(coluna, F.coalesce(
            F.col(coluna),
            F.when(eh_gestor, F.lit(f"ni_{slug}")).otherwise(F.lit("ni_fora_da_area"))))
    for coluna in ["sk_setor", "sk_geografia", "sk_modelo_trabalho",
                   "sk_faixa_salarial", "sk_tempo_experiencia", "sk_area_formacao"]:
        f = f.withColumn(coluna, F.coalesce(F.col(coluna), F.lit("ni_nao_declarado")))
    return f


# --------------------------------------------------------------------------- #
# membros explícitos: o que estava vindo como chave nula
# --------------------------------------------------------------------------- #
# A pesquisa é condicional e três populações não veem parte das perguntas:
#
#   2.668 gestores   não declaram cargo técnico nem senioridade (respondem o
#                    bloco de gestão: time, desafios e estratégia de IA)
#   1.161 pessoas    não declaram nada de emprego (fora da área de dados)
#     382 pessoas    não declaram o estado
#
# Deixar a FK nula faz o Power BI inventar uma linha "(Em branco)" que aparece
# no filtro, no eixo e dentro das medidas, e ninguém entende o que ela é.
# Nomear o membro transforma ausência em informação.

NAO_INFORMADO = {
    "dim_cargo": [
        ("Gestor, sem cargo técnico", "gestor_sem_cargo", 90),
        ("Fora da área de dados", "fora_da_area", 91),
    ],
    "dim_senioridade": [
        ("Gestor, sem senioridade", "gestor_sem_senioridade", 90),
        ("Fora da área de dados", "fora_da_area", 91),
    ],
    "dim_setor": [("Não declarado", "nao_declarado", 90)],
    "dim_geografia": [("Não declarado", "nao_declarado", 90)],
    "dim_modelo_trabalho": [("Não declarado", "nao_declarado", 90)],
    "dim_faixa_salarial": [("Não declarado", "nao_declarado", 90)],
    "dim_tempo_experiencia": [("Não declarado", "nao_declarado", 90)],
    "dim_area_formacao": [("Não declarado", "nao_declarado", 90)],
}

# Rótulos que NÃO são resposta de verdade. As medidas de denominador e os
# filtros de visual excluem estes, e é por eles que a base de cada indicador
# fica explícita no dashboard.
ROTULOS_NAO_INFORMADO = sorted({r for v in NAO_INFORMADO.values() for r, _, _ in v})


# --------------------------------------------------------------------------- #
# validação
# --------------------------------------------------------------------------- #


def validar(fato, dims, dim_opcao, bridge):
    erros = []

    n = fato.count()
    if n != 14002:
        erros.append(f"fato com {n} linhas, esperado 14002")
    if fato.select("sk_respondente").distinct().count() != n:
        erros.append("sk_respondente não é única no fato")

    # Integridade referencial: FK preenchida tem de existir na dimensão.
    for nome_dim, col_sk in [
        ("dim_cargo", "sk_cargo"), ("dim_senioridade", "sk_senioridade"),
        ("dim_setor", "sk_setor"), ("dim_geografia", "sk_geografia"),
        ("dim_faixa_salarial", "sk_faixa_salarial"),
        ("dim_modelo_trabalho", "sk_modelo_trabalho"),
    ]:
        orfas = (fato.filter(F.col(col_sk).isNotNull())
                     .join(dims[nome_dim].select(col_sk), col_sk, "left_anti").count())
        if orfas:
            erros.append(f"{orfas} linhas do fato com {col_sk} sem correspondente em {nome_dim}")

    orfas = bridge.join(dim_opcao.select("sk_opcao"), "sk_opcao", "left_anti").count()
    if orfas:
        erros.append(f"{orfas} linhas da bridge sem opção em dim_opcao")
    orfas = bridge.join(fato.select("sk_respondente"), "sk_respondente", "left_anti").count()
    if orfas:
        erros.append(f"{orfas} linhas da bridge sem respondente no fato")

    if erros:
        raise ValueError("Gold inválida:\n  - " + "\n  - ".join(erros))

    # dim_benchmark é uma dimensão SEM relacionamento com o fato, de
    # propósito: ela não descreve respondente, descreve o mercado. No Power BI
    # vira tabela desconectada, lida por medida.
    bm = dims["dim_benchmark"]
    sem_fonte = bm.filter(F.col("fonte").isNull() | F.col("url").isNull()).count()
    if sem_fonte:
        raise ValueError(f"{sem_fonte} benchmarks sem fonte ou URL")

    # Guarda de regressão da divisão de `uso_ia_generativa`. A separação entre
    # os três blocos é por público, e é exata: se alguma edição futura misturar
    # gestor com não gestor num deles, o denominador volta a mentir e é melhor
    # o job quebrar aqui do que o dashboard publicar o número errado.
    publico = (bridge.join(dim_opcao.select("sk_opcao", "grupo"), "sk_opcao")
                     .filter(F.col("grupo").startswith("uso_ia_"))
                     .join(fato.select("sk_respondente", "eh_gestor"), "sk_respondente")
                     .groupBy("grupo").agg(
                         F.countDistinct("sk_respondente").alias("pessoas"),
                         F.countDistinct(F.when(F.col("eh_gestor"), F.col("sk_respondente")))
                          .alias("gestores")))
    esperado = {"uso_ia_pessoal": 0, "uso_ia_empresa": 0}
    for linha in publico.collect():
        print(f"       {linha['grupo']:16s} {linha['pessoas']:6d} pessoas, "
              f"{linha['gestores']} gestores")
        if linha["grupo"] in esperado and linha["gestores"] != esperado[linha["grupo"]]:
            raise ValueError(f"{linha['grupo']} com {linha['gestores']} gestores, "
                             "esperado nenhum: a divisão dos blocos de IA quebrou")
        if linha["grupo"] == "uso_ia_gestor" and linha["gestores"] != linha["pessoas"]:
            raise ValueError("uso_ia_gestor com não gestor dentro")

    print(f"[OK] Gold validada: fato {n} linhas, {len(dims)} dimensões, "
          f"{dim_opcao.count()} opções, {bridge.count()} linhas na bridge.")


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #


def main():
    spark = sessao("tc3-gold")
    silver = ler_silver(spark).cache()

    print("\n=== GOLD: modelo dimensional único ===\n")

    dims = construir_dimensoes(spark, silver)
    dim_opcao, bridge = construir_bridge(silver)
    fato = construir_fato(silver, dims).cache()

    validar(fato, dims, dim_opcao, bridge)

    print()
    gravar(fato, PREFIXO + "fat_profissionais", particao="ano_pesquisa", mostrar=False)
    for nome, df in dims.items():
        gravar(df, PREFIXO + nome, mostrar=False)
    gravar(dim_opcao, PREFIXO + "dim_opcao", mostrar=False)
    gravar(bridge, PREFIXO + "bridge_respondente_opcao", mostrar=False)

    # Sem `spark.stop()`: no Glue quem encerra o contexto é o próprio serviço,
    # e parar por conta própria pode cortar a entrega dos logs.


if __name__ == "__main__":
    # `main()` direto, sem `sys.exit()`. O Glue trata qualquer SystemExit vindo
    # do script como falha do job (Error Category: SYSTEM_EXIT_ERROR), mesmo
    # quando o código de saída é 0. Um `sys.exit(main())` com main retornando
    # None marca o job como Failed depois de ter feito o trabalho todo.
    main()

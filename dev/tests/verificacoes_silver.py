"""
As verificações da camada Silver, uma função por bloco.

Este módulo não roda nada sozinho. Ele é consumido por dois lugares:

    tests/test_silver_local.py            → linha de comando, saída OK/FALHA
    notebooks/03b_validacao_silver.ipynb  → célula a célula, com evidência

A lógica das asserções mora AQUI e só aqui. Se estivesse duplicada nos dois,
uma correção num lugar sairia divergente do outro na primeira semana.

Autor: Caio Bosnic
"""

import glob
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

from pyspark.sql import functions as F


import config_silver as cfg  # noqa: E402

# Contagens esperadas por edição, já sem as duplicatas exatas.
LINHAS_ESPERADAS = {2023: 5293, 2024: 5215, 2025: 3494}


# --------------------------------------------------------------------------- #
# acumulador de resultados
# --------------------------------------------------------------------------- #


class Verificador:
    """Acumula o resultado das asserções e sabe se resume em texto ou tabela."""

    def __init__(self, silencioso=False):
        self.resultados = []
        self.silencioso = silencioso

    def checar(self, condicao, descricao, detalhe=""):
        ok = bool(condicao)
        self.resultados.append({"ok": ok, "verificacao": descricao, "detalhe": detalhe})
        if not self.silencioso:
            print(f"  [{'OK  ' if ok else 'FALHA'}] {descricao}"
                  f"{(', ' + detalhe) if detalhe else ''}")
        return ok

    @property
    def falhas(self):
        return [r for r in self.resultados if not r["ok"]]

    def tabela(self):
        """DataFrame do pandas, para o notebook renderizar."""
        import pandas as pd

        df = pd.DataFrame(self.resultados)
        if df.empty:
            return df
        df.insert(0, "status", df["ok"].map({True: "OK", False: "FALHA"}))
        return df.drop(columns=["ok"])

    def resumo(self):
        total, falhas = len(self.resultados), len(self.falhas)
        linha = "=" * 62
        if falhas:
            corpo = f"{falhas} FALHA(S) de {total}:\n" + "\n".join(
                f"  - {f['verificacao']}" + (f", {f['detalhe']}" if f["detalhe"] else "")
                for f in self.falhas
            )
        else:
            corpo = f"TODAS AS {total} VERIFICAÇÕES PASSARAM"
        return f"{linha}\n{corpo}\n{linha}"


# --------------------------------------------------------------------------- #
# montagem da Bronze de teste
# --------------------------------------------------------------------------- #


def achar_csv(pasta_csv, ano):
    """
    Localiza o CSV da edição pelo ano no fim do nome.

    Casa com `bronze_dw_state_data_2023.csv`, `bronze_2023.csv`, qualquer
    coisa que termine no ano.
    """
    achados = sorted(glob.glob(os.path.join(pasta_csv, f"*{ano}.csv")))
    if not achados:
        disponiveis = [os.path.basename(p) for p in glob.glob(os.path.join(pasta_csv, "*.csv"))]
        raise FileNotFoundError(
            f"Não achei o CSV de {ano} em {pasta_csv}.\n"
            f"  Arquivos .csv na pasta: {disponiveis or 'nenhum'}\n"
            f"  O nome precisa terminar em '{ano}.csv'."
        )
    if len(achados) > 1:
        print(f"  [!] {len(achados)} arquivos casam com {ano}; "
              f"usando {os.path.basename(achados[0])}")
    return achados[0]


def montar_bronze(spark, pasta_csv, destino, verboso=True):
    """Converte os CSVs para Parquet no layout que o job espera na Bronze."""
    for ano, meta in cfg.EDICOES.items():
        origem = achar_csv(pasta_csv, ano)
        (
            spark.read
            .option("header", "true")
            .option("multiLine", "true")
            .option("escape", '"')
            .option("inferSchema", "false")   # Bronze é toda string, por decisão
            .csv(origem)
            .write.mode("overwrite").parquet(os.path.join(destino, meta["tabela_bronze"]))
        )
        if verboso:
            print(f"  {os.path.basename(origem)}  ->  {meta['tabela_bronze']}")


def _regiao_da_uf(coluna):
    expr = F.lit(None)
    for uf, regiao in cfg.UF_PARA_REGIAO.items():
        expr = F.when(coluna == F.lit(uf), F.lit(regiao)).otherwise(expr)
    return expr


# --------------------------------------------------------------------------- #
# as verificações
# --------------------------------------------------------------------------- #


def verificar_contagens(silver, v, ctx=None):
    """Cada edição entregou o número de linhas do contrato?"""
    obtido = {r["ano_pesquisa"]: r["n"] for r in
              silver.groupBy("ano_pesquisa").agg(F.count("*").alias("n")).collect()}
    for ano in sorted(LINHAS_ESPERADAS):
        v.checar(obtido.get(ano) == LINHAS_ESPERADAS[ano],
                 f"{ano}: {obtido.get(ano)} linhas", f"esperado {LINHAS_ESPERADAS[ano]}")
    total = silver.count()
    v.checar(total == sum(LINHAS_ESPERADAS.values()),
             f"total = {total}", f"esperado {sum(LINHAS_ESPERADAS.values())}")


def verificar_chave(silver, v, ctx=None):
    """A surrogate key é única e nenhum respondente perdeu o id de origem."""
    v.checar(silver.select("sk_respondente").distinct().count() == silver.count(),
             "sk_respondente é única")
    v.checar(silver.filter(F.col("id_origem").isNull()).count() == 0,
             "id_origem sem nulos")


def verificar_ano_injetado(silver, v, ctx=None):
    """
    Contra-prova da injeção do `ano_pesquisa`.

    Nenhuma base tem coluna de edição, o ano vem da ORIGEM do arquivo. Onde
    existe data de envio (2024 e 2025), ela tem de cair dentro do ano injetado.
    """
    for ano in (2024, 2025):
        fora = (silver.filter((F.col("ano_pesquisa") == ano) & F.col("data_envio").isNotNull())
                      .filter(F.year("data_envio") != ano).count())
        v.checar(fora == 0, f"{ano}: nenhuma data_envio fora do ano injetado")
    nulos = silver.filter((F.col("ano_pesquisa") == 2023) & F.col("data_envio").isNull()).count()
    v.checar(nulos == LINHAS_ESPERADAS[2023],
             "2023 sem data_envio (esperado, a edição não coleta)")


def verificar_booleanos(silver, v, ctx=None):
    """
    O `TRUE`/`FALSE` de 2024-2025 virou booleano junto com o `0`/`1` das outras.

    Exige True E False no domínio, não só "domínio contido em {True,False,None}".
    A versão frouxa deixou passar uma coluna 100% nula, o teste dizia OK e o
    dado estava vazio.
    """
    for col in cfg.COLUNAS_BOOLEANAS:
        dominio = {r[0] for r in silver.select(col).distinct().collect()}
        v.checar(dominio <= {True, False, None} and {True, False} <= dominio,
                 f"{col}: domínio {sorted(dominio, key=str)}")

    por_ano = {r["ano_pesquisa"]: r["n"] for r in
               silver.filter(F.col("eh_gestor")).groupBy("ano_pesquisa")
                     .agg(F.count("*").alias("n")).collect()}
    v.checar(all(por_ano.get(a, 0) > 0 for a in (2023, 2024, 2025)),
             "eh_gestor=True presente nas 3 edições", str(por_ano))


def verificar_colunas_nao_vazias(silver, v, ctx=None):
    """Nenhuma coluna saiu 100% nula, o sintoma de de-para apontando pro nada."""
    total = silver.count()
    nulos = silver.select(
        [F.count(F.when(F.col(c).isNull(), c)).alias(c) for c in silver.columns]
    ).collect()[0]
    vazias = [c for c in silver.columns if nulos[c] == total]
    v.checar(not vazias, "toda coluna tem ao menos um valor", f"vazias: {vazias}")


def verificar_layoff(silver, v, ctx=None):
    """As 3 respostas de layoff viraram 2 flags coerentes entre si."""
    for col in ("houve_layoff", "fui_afetado_layoff"):
        dominio = {r[0] for r in silver.select(col).distinct().collect()}
        v.checar({True, False} <= dominio, f"{col}: domínio {sorted(dominio, key=str)}")
    inconsistentes = silver.filter(F.col("fui_afetado_layoff") & ~F.col("houve_layoff")).count()
    v.checar(inconsistentes == 0, "ninguém foi afetado por layoff que não houve")


def verificar_uf_moradia(silver, v, ctx=None):
    """
    O achado do drift semântico.

    Se `uf` da Bronze tivesse sido usada direto, 2025-2026 traria o estado de
    NASCIMENTO. Aqui a sigla é derivada de `estado`, então tem de bater com a
    região de moradia nas três edições.
    """
    conferido = (
        silver.filter(F.col("uf_moradia").isNotNull() & F.col("regiao_moradia").isNotNull())
              .withColumn("regiao_calc", _regiao_da_uf(F.col("uf_moradia")))
    )
    divergentes = conferido.filter(F.col("regiao_calc") != F.col("regiao_moradia")).count()
    v.checar(divergentes == 0,
             "uf_moradia derivada bate com regiao_moradia em 100% das linhas",
             f"{divergentes} divergências")


def verificar_salario(silver, v, ctx=None):
    """Toda faixa tem ponto médio, e os dois typos da origem sumiram."""
    sem_mapa = silver.filter(
        F.col("faixa_salarial").isNotNull() & F.col("salario_medio_mensal").isNull()
    ).count()
    v.checar(sem_mapa == 0, "toda faixa preenchida tem ponto médio", f"{sem_mapa} sem mapa")
    v.checar(silver.filter(F.col("faixa_salarial").contains("R$_101/")).count() == 0,
             "typo 'R$_101' corrigido")
    v.checar(silver.filter(F.col("faixa_salarial").contains("_R$_3000/")).count() == 0,
             "typo 'R$_3000' corrigido")


def verificar_comparabilidade(silver, v, ctx=None):
    """Categoria que só existe em parte das edições está marcada."""
    nao_comparaveis = silver.filter(~F.col("serie_comparavel")).count()
    v.checar(nao_comparaveis > 0, f"{nao_comparaveis} linhas marcadas como não comparáveis")
    especialista = silver.filter(F.col("nivel_senioridade") == "Especialista/Staff+")
    v.checar(especialista.filter(F.col("serie_comparavel")).count() == 0,
             "'Especialista/Staff+' (só 2025) marcado como não comparável")


def verificar_ausentes_viram_nulo(silver, v, ctx=None):
    """Pergunta que não existe na edição virou NULL, nunca zero nem vazio."""
    v.checar(
        silver.filter((F.col("ano_pesquisa") == 2023) & F.col("estado_origem").isNotNull()).count() == 0,
        "estado_origem nulo em 2023 (pergunta não existe)")
    v.checar(
        silver.filter((F.col("ano_pesquisa") < 2025) & F.col("llms_bom_resultado").isNotNull()).count() == 0,
        "llms_bom_resultado só existe em 2025")


def verificar_multipla_escolha_contra_origem(silver, v, ctx):
    """
    Contra-prova: a lista consolidada tem exatamente as opções marcadas na
    Bronze crua?

    Precisa de `ctx["spark"]` e `ctx["path_bronze"]` para reabrir a origem.
    """
    spark, base = ctx["spark"], ctx["path_bronze"]
    amostras = [(2023, "linguagens"), (2024, "bancos_dados"),
                (2025, "ferramentas_bi"), (2025, "atividades_cientista_dados")]

    for ano, grupo in amostras:
        meta = cfg.EDICOES[ano]
        cru = spark.read.parquet(os.path.join(base, meta["tabela_bronze"]))
        colunas = [c for c in cfg.GRUPOS_MULTIPLA_ESCOLHA[grupo][ano] if c in cru.columns]

        alvo = (silver.filter((F.col("ano_pesquisa") == ano) & (F.col(f"qtd_{grupo}") >= 2))
                      .select("id_origem", grupo, f"qtd_{grupo}").first())
        if alvo is None:
            v.checar(False, f"{ano}/{grupo}: nenhuma linha com 2+ opções para conferir")
            continue

        origem = cru.filter(F.col(meta["col_chave"]) == alvo["id_origem"]).first()
        esperado = sorted(c for c in colunas if origem[c] in ("1", "TRUE", "true", "True"))
        obtido = (sorted(alvo[grupo].split(cfg.SEPARADOR_MULTIPLA_ESCOLHA))
                  if alvo[grupo] else [])
        v.checar(esperado == obtido, f"{ano}/{grupo}: lista bate com os binários",
                 f"{len(obtido)} opções")
        v.checar(alvo[f"qtd_{grupo}"] == len(esperado),
                 f"{ano}/{grupo}: qtd_ bate com a lista")


def verificar_grupos(silver, v, ctx=None):
    """
    Os 17 grupos existem, têm conteúdo e a lista concorda com a contagem.

    Um único agregado para todos: 17 counts separados fazem o teste levar
    minutos sem necessidade.
    """
    grupos = sorted(cfg.GRUPOS_MULTIPLA_ESCOLHA)
    faltando = [g for g in grupos
                if g not in silver.columns or f"qtd_{g}" not in silver.columns]
    v.checar(not faltando, "todos os grupos viraram coluna (lista + qtd)", str(faltando))

    presentes = [g for g in grupos if g not in faltando]
    if not presentes:
        return

    aggs = []
    for g in presentes:
        aggs.append(F.count(F.when(F.col(g).isNotNull(), 1)).alias(f"{g}__ok"))
        # NULL ≠ zero: quem não respondeu o bloco tem NULL nas DUAS colunas;
        # quem respondeu e não marcou nada tem "" e 0. Confundir os dois infla
        # denominador e derruba percentual.
        aggs.append(F.count(F.when(F.col(g).isNull() != F.col(f"qtd_{g}").isNull(), 1))
                     .alias(f"{g}__incoerente"))
        aggs.append(F.max(F.col(f"qtd_{g}")).alias(f"{g}__maxqtd"))
    r = silver.agg(*aggs).collect()[0]

    for g in presentes:
        v.checar(r[f"{g}__ok"] > 0 and r[f"{g}__incoerente"] == 0, g,
                 f"{r[f'{g}__ok']} preenchidas, máx {r[f'{g}__maxqtd']} opções")


def verificar_estabilidade_das_bases(silver, v, ctx=None):
    """
    A base de um grupo não pode despencar de um ano para o outro.

    Foi assim que apareceu o bug do sufixo `_1` invertido: o grupo tinha 4.727
    respondentes em 2023 e 1.527 em 2024, porque o agrupamento por nome juntou
    a pergunta ampla de uma edição com a estreita da outra. Nenhuma outra
    verificação pegava isso, o dado existia, estava preenchido e coerente
    consigo mesmo; só era a pergunta errada.

    Compara a proporção da base (respondentes / total do ano), não o número
    absoluto, porque 2025 tem 33% menos respondentes que 2023 por natureza.
    """
    total = {r["ano_pesquisa"]: r["n"] for r in
             silver.groupBy("ano_pesquisa").agg(F.count("*").alias("n")).collect()}

    for grupo in sorted(cfg.GRUPOS_MULTIPLA_ESCOLHA):
        anos_com_grupo = [a for a in (2023, 2024, 2025)
                          if cfg.GRUPOS_MULTIPLA_ESCOLHA[grupo].get(a)]
        if len(anos_com_grupo) < 2:
            continue   # grupo de uma edição só não tem série para comparar

        prop = {}
        for r in (silver.filter(F.col(grupo).isNotNull())
                        .groupBy("ano_pesquisa").agg(F.count("*").alias("n")).collect()):
            prop[r["ano_pesquisa"]] = r["n"] / total[r["ano_pesquisa"]]

        valores = [prop.get(a, 0) for a in anos_com_grupo]
        maior, menor = max(valores), min(valores)
        # 2.5x de variação na proporção é folgado para oscilação real de
        # pesquisa e apertado o bastante para pegar troca de pergunta.
        ok = menor > 0 and (maior / menor) <= 2.5
        v.checar(ok, f"{grupo}: base estável entre edições",
                 " ".join(f"{a}={prop.get(a,0):.0%}" for a in anos_com_grupo))


def verificar_rotulos_harmonizados(silver, v, ctx=None):
    """
    A mesma opção tem de aparecer nas edições em que o grupo existe.

    Foi assim que passou despercebido que `remuneracao_salario` (2023) e
    `remuneracao_salario_1` (2024/25) são a MESMA opção: a tabela de fatores
    saiu 81,4% em 2023 e 0,0% em 2025. Sem erro, sem nulo, a lista simplesmente
    não continha o rótulo que o filtro procurava.

    Confere sobre o dado GRAVADO, não sobre o dicionário: é o rótulo que saiu
    na coluna que a Gold vai filtrar.
    """
    for grupo in sorted(cfg.GRUPOS_MULTIPLA_ESCOLHA):
        anos = [a for a in (2023, 2024, 2025) if cfg.GRUPOS_MULTIPLA_ESCOLHA[grupo].get(a)]
        if len(anos) < 2:
            continue

        explodido = (silver.filter(F.col(grupo).isNotNull() & (F.col(grupo) != ""))
                           .select("ano_pesquisa",
                                   F.explode(F.split(F.col(grupo),
                                                     cfg.SEPARADOR_MULTIPLA_ESCOLHA)).alias("op")))
        por_ano = {}
        for r in explodido.distinct().collect():
            por_ano.setdefault(r["ano_pesquisa"], set()).add(r["op"])

        conjuntos = [por_ano.get(a, set()) for a in anos]
        comuns = set.intersection(*conjuntos) if conjuntos else set()
        uniao = set.union(*conjuntos) if conjuntos else set()

        if grupo in cfg.GRUPOS_ROTULO_NAO_HARMONIZADO:
            v.checar(True, f"{grupo}: rótulo NAO harmonizado (declarado no config)",
                     f"{len(comuns)}/{len(uniao)} opções comuns")
            continue

        ok = bool(uniao) and len(comuns) / len(uniao) >= 0.5
        v.checar(ok, f"{grupo}: rótulos batem entre edições",
                 f"{len(comuns)}/{len(uniao)} comuns")


# Ordem de execução. O runner e o notebook consomem esta lista: acrescentar
# uma verificação aqui a faz aparecer nos dois.
VERIFICACOES = [
    ("contagens por edição", verificar_contagens),
    ("chave", verificar_chave),
    ("ano_pesquisa validado contra a data de envio", verificar_ano_injetado),
    ("booleano normalizado (o TRUE/FALSE de 2024)", verificar_booleanos),
    ("nenhuma coluna 100% nula", verificar_colunas_nao_vazias),
    ("layoff: 3 respostas viram 2 flags", verificar_layoff),
    ("uf_moradia corrigida (o drift semântico)", verificar_uf_moradia),
    ("salário: faixa -> ponto médio", verificar_salario),
    ("comparabilidade de série", verificar_comparabilidade),
    ("colunas ausentes viraram NULL, não zero", verificar_ausentes_viram_nulo),
    ("múltipla escolha: contra-prova com a origem", verificar_multipla_escolha_contra_origem),
    ("os 17 grupos: presença e coerência", verificar_grupos),
    ("estabilidade da base de cada grupo", verificar_estabilidade_das_bases),
    ("rotulos de opcao harmonizados", verificar_rotulos_harmonizados),
]


def rodar_todas(silver, ctx, silencioso=False):
    """Roda a bateria inteira e devolve o Verificador com os resultados."""
    v = Verificador(silencioso=silencioso)
    for titulo, funcao in VERIFICACOES:
        if not silencioso:
            print(f"\n=== {titulo} ===")
        funcao(silver, v, ctx)
    return v

"""
Gold da PERGUNTA 5: "Qual é o índice de adoção de IA e seu impacto?"

⚠️⚠️ A ARMADILHA MAIS CARA DE TODA A BASE ESTÁ AQUI ⚠️⚠️

Existem TRÊS populações e elas não se misturam:

    uso individual de IA ..........  9.494  (quem VIU a pergunta de uso pessoal)
    estratégia de IA da empresa ...  2.593  (SÓ GESTORES: 100% eh_gestor=true)
    maturidade de dados ...........  2.396  (SÓ ENGENHEIROS DE DADOS não-gestores)

E tem uma quarta armadilha dentro da primeira: `uso_ia_generativa` tem 12.041
linhas preenchidas, mas NÃO é uma pergunta. É a fusão de três, que a origem
empilhou no mesmo bloco de opções. Os 2.547 de diferença são gestores que
responderam só o bloco deles. Por isso este job usa `base_uso_ia_pessoal()`, e
não `base_da_pergunta(silver, "uso_ia_generativa")`: a segunda infla a adoção
de 89,2% para 91,5%.

Verificado: 100% de quem respondeu `ia_gen_prioridade` tem `eh_gestor = true`,
e 0% de quem respondeu `empresa_possui_datalake` é gestor. São blocos
condicionais de públicos diferentes, não amostragem.

⚠️ A interseção entre os dois blocos de empresa é ZERO. Não existe cruzamento
possível entre "prioriza IA" e "tem data lake" nesta base.

Consequência: "61% das empresas priorizam IA" é uma frase sobre GESTORES.
Calculada sobre os 14.002 daria 3%, e o número estaria errado por um fator
de 20. Toda tabela aqui carrega `base` para o denominador ir junto no slide.

"Impacto" também tem duas leituras, e as duas estão aqui:
  · impacto NA EMPRESA ...... prioridade, forma de uso, barreiras
  · impacto NO PROFISSIONAL .. uso pago x gratuito, copilot, produtividade
"""

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


from pyspark.sql import Window as W  # noqa: E402
from pyspark.sql import functions as F  # noqa: E402

from gold_comum import (  # noqa: E402
    IA_PESSOAL,
    _marcou_alguma,
    base_da_pergunta,
    base_uso_ia_empresa,
    base_uso_ia_pessoal,
    gravar,
    indicador,
    ler_silver,
    marcou,
    pct,
    sessao,
    usa_ia_pessoal,
)

NUMERO, PREFIXO = "5", "gold_dw_p5_"
PERGUNTA = "Qual é o índice de adoção de IA e seu impacto?"

PRIORIDADE_ALTA = [
    "Sim,_e_nossa_principal_prioridade_como_empresa_(com_foco_executivo_significativo"
    "_e_alocacao_de_orcamento_relevante).",
    "Sim,_esta_entre_nossas_principais_prioridades_para_os_proximos_2-4_anos"
    "_(com_discussoes_de_iniciativas_e_orcamentos_de_curto_a_medio_prazo).",
]


def construir(silver):
    t = {}

    # =====================================================================
    # A prova do denominador: a tabela que evita o erro
    # =====================================================================
    # As duas primeiras colunas são o mesmo erro e o mesmo acerto lado a lado:
    # `coluna_preenchida` conta quem tem QUALQUER opção de IA marcada, inclusive
    # gestor que só respondeu o bloco dele. `base_uso_pessoal` conta só quem viu
    # a pergunta de uso individual. A diferença entre as duas é a armadilha.
    t["quem_responde_o_que"] = (
        silver.agg(
            F.count("*").alias("silver_total"),
            F.count("uso_ia_generativa").alias("coluna_preenchida"),
            F.count(F.when(_marcou_alguma("uso_ia_generativa", IA_PESSOAL), 1))
             .alias("base_uso_pessoal"),
            F.count(F.when(_marcou_alguma("uso_ia_generativa", IA_PESSOAL)
                           & F.col("eh_gestor"), 1)).alias("gestores_no_uso_pessoal"),
            F.count("ia_gen_prioridade").alias("base_estrategia_empresa"),
            F.count(F.when(F.col("ia_gen_prioridade").isNotNull() & F.col("eh_gestor"), 1))
             .alias("desses_sao_gestores"),
        )
    )

    # =====================================================================
    # ADOÇÃO INDIVIDUAL: base ~85%
    # =====================================================================
    base_ind = base_uso_ia_pessoal(silver)

    t["adocao_individual"] = indicador(
        base_ind, usa_ia_pessoal(),
        por=["ano_pesquisa"], rotulo="Usa IA generativa no trabalho",
    )

    formas = [
        ("uso_ia_gen_gratuita_produtividade", "Usa versão gratuita"),
        ("uso_pago_ia_gen_produtividade", "Paga do próprio bolso"),
        ("uso_pago_ia_gen_empresa_paga", "A empresa paga"),
        ("uso_copilot", "Usa copilot de código"),
        ("nao_uso_ia_gen_produtividade", "Não usa"),
    ]
    t["forma_de_uso"] = None
    for col, rotulo in formas:
        parcial = indicador(base_ind, marcou("uso_ia_generativa", col),
                            por=["ano_pesquisa"], rotulo=rotulo)
        t["forma_de_uso"] = parcial if t["forma_de_uso"] is None \
            else t["forma_de_uso"].unionByName(parcial)
    t["forma_de_uso"] = t["forma_de_uso"].orderBy("ano_pesquisa", F.desc("pct"))

    # Quem banca a ferramenta é um indicador de maturidade: empresa pagando
    # significa uso institucionalizado, não experimento individual.
    t["quem_paga"] = (
        base_ind.groupBy("ano_pesquisa")
                .agg(F.count("*").alias("base"),
                     F.count(F.when(marcou("uso_ia_generativa", "uso_pago_ia_gen_empresa_paga"), 1)).alias("empresa_paga"),
                     F.count(F.when(marcou("uso_ia_generativa", "uso_pago_ia_gen_produtividade"), 1)).alias("proprio_bolso"),
                     F.count(F.when(marcou("uso_ia_generativa", "uso_ia_gen_gratuita_produtividade"), 1)).alias("so_gratuito"))
                .withColumn("pct_empresa_paga", pct(F.col("empresa_paga"), F.col("base")))
                .withColumn("pct_proprio_bolso", pct(F.col("proprio_bolso"), F.col("base")))
                .orderBy("ano_pesquisa")
    )

    # Adoção individual por perfil: quem puxa a adoção
    for dim in ["cargo_atual", "nivel_senioridade", "setor_empresa", "regiao_moradia"]:
        t[f"adocao_por_{dim}"] = (
            base_ind.filter(F.col(dim).isNotNull())
                    .groupBy(dim)
                    .agg(F.count("*").alias("base"),
                         F.count(F.when(usa_ia_pessoal(), 1)).alias("usa"))
                    .withColumn("pct_adocao", pct(F.col("usa"), F.col("base")))
                    .filter(F.col("base") >= 30)
                    .orderBy(F.desc("pct_adocao"))
        )

    # =====================================================================
    # ESTRATÉGIA DA EMPRESA: base SÓ GESTORES
    # =====================================================================
    base_emp = base_da_pergunta(silver, "ia_gen_prioridade")

    t["prioridade_empresa"] = (
        base_emp.groupBy("ano_pesquisa", "ia_gen_prioridade")
                .agg(F.count("*").alias("gestores"))
                .withColumn("pct", F.round(100.0 * F.col("gestores")
                                           / F.sum("gestores").over(W.partitionBy("ano_pesquisa")), 1))
                .orderBy("ano_pesquisa", F.desc("gestores"))
    )

    t["prioridade_alta"] = indicador(
        base_emp, F.col("ia_gen_prioridade").isin(PRIORIDADE_ALTA),
        por=["ano_pesquisa"], rotulo="IA é prioridade alta na empresa",
    )

    # O gap entre as duas populações: o achado que sustenta a resposta
    t["gap_pessoa_empresa"] = (
        t["adocao_individual"].select("ano_pesquisa",
                                      F.col("pct").alias("pct_pessoas_usam"),
                                      F.col("base").alias("base_pessoas"))
        .join(t["prioridade_alta"].select("ano_pesquisa",
                                          F.col("pct").alias("pct_empresas_priorizam"),
                                          F.col("base").alias("base_gestores")), "ano_pesquisa")
        .withColumn("gap_pp", F.round(F.col("pct_pessoas_usam") - F.col("pct_empresas_priorizam"), 1))
        .orderBy("ano_pesquisa")
    )

    # Como a empresa organiza o uso: centralizado x descentralizado
    usos_empresa = [
        ("ia_llm_empresa_descentralizada_independente", "Uso descentralizado pelos colaboradores"),
        ("ia_llm_empresa_uso_centralizado", "Direcionamento centralizado"),
        ("ia_llm_empresa_uso_copilot", "Copilot para desenvolvimento"),
        ("ia_llm_empresa_prod_interno", "Produto interno"),
        ("ia_llm_empresa_prod_externo", "Produto externo / cliente"),
        ("ia_llm_empresa_frente_negoc", "Principal frente de negócio"),
        ("ia_llm_empresa_nao_prioridade", "Não é prioridade"),
    ]
    base_org = base_uso_ia_empresa(silver)
    t["organizacao_do_uso"] = None
    for col, rotulo in usos_empresa:
        parcial = indicador(base_org, marcou("uso_ia_generativa", col),
                            por=["ano_pesquisa"], rotulo=rotulo)
        t["organizacao_do_uso"] = parcial if t["organizacao_do_uso"] is None \
            else t["organizacao_do_uso"].unionByName(parcial)
    t["organizacao_do_uso"] = t["organizacao_do_uso"].orderBy("ano_pesquisa", F.desc("pct"))

    # Barreiras: base gestores
    base_barr = base_da_pergunta(silver, "barreiras_ia_generativa")
    barreiras = [
        ("falta_expertise_ou_recurso", "Falta de expertise ou recurso"),
        ("falta_compreensao_caso_uso", "Falta de compreensão do caso de uso"),
        ("seguranca_privacidade_dados", "Segurança e privacidade"),
        ("falta_confiab_saida_alucinacao_modelo", "Confiabilidade da saída"),
        ("alta_direcao_nao_ve_valor_prioridade", "Alta direção não vê valor"),
        ("incerteza_rel_regulamentacao", "Incerteza regulatória"),
        ("preocupacao_prop_intelectual", "Propriedade intelectual"),
    ]
    t["barreiras"] = None
    for col, rotulo in barreiras:
        parcial = indicador(base_barr, marcou("barreiras_ia_generativa", col),
                            por=["ano_pesquisa"], rotulo=rotulo)
        t["barreiras"] = parcial if t["barreiras"] is None else t["barreiras"].unionByName(parcial)
    t["barreiras"] = t["barreiras"].orderBy("ano_pesquisa", F.desc("pct"))

    # =====================================================================
    # IMPACTO PERCEBIDO: só 2025 tem a pergunta
    # =====================================================================
    base_llm = base_da_pergunta(silver, "llms_bom_resultado")
    t["resultado_com_llm"] = (
        base_llm.groupBy("ano_pesquisa", "llms_bom_resultado")
                .agg(F.count("*").alias("respondentes"))
                .withColumn("pct", F.round(100.0 * F.col("respondentes")
                                           / F.sum("respondentes").over(W.partitionBy("ano_pesquisa")), 1))
                .orderBy(F.desc("respondentes"))
    )

    # ⚠️ NÃO EXISTE cruzamento entre prioridade de IA e maturidade de dados.
    # `ia_gen_prioridade` e `empresa_possui_datalake` têm interseção ZERO:
    # são blocos condicionais de públicos diferentes. O primeiro é respondido
    # por gestores; o segundo, por engenheiros de dados NÃO-gestores. Nenhum
    # respondente aparece nos dois. Qualquer tabela cruzando os dois sai vazia.

    return t


def main():
    spark = sessao(f"tc3-gold-p{NUMERO}")
    silver = ler_silver(spark).cache()
    print(f"\n=== Gold da pergunta {NUMERO} ===\n{PERGUNTA}\n")
    for nome, df in construir(silver).items():
        gravar(df, PREFIXO + nome, mostrar=False)
    spark.stop()


if __name__ == "__main__":
    main()

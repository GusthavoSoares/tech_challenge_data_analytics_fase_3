"""
TEMPLATE da Gold. Copie este arquivo para escrever a sua pergunta.

    cp job_gold_pN_template.py job_gold_p3.py

Depois: troque PERGUNTA, RESPONSAVEL e escreva as suas agregações em
`construir()`. Não precisa mexer em mais nada, leitura da Silver, dimensões e
gravação vêm de `gold_comum`.

Combinado do grupo: cada um é dono das tabelas das SUAS perguntas. As tabelas
saem com o prefixo `gold_dw_p<N>_`, então ninguém escreve por cima de ninguém.

--------------------------------------------------------------------------
AS TRÊS ARMADILHAS, todas produzem número errado SEM dar erro
--------------------------------------------------------------------------

1. DENOMINADOR. Vários blocos são condicionais. `ia_gen_prioridade` e
   `barreiras_ia_generativa` só são respondidos por GESTORES (2.593 de 14.002);
   `atividades_cientista_dados` só por quem é cientista (2.010).
   Use `base_da_pergunta(silver, "coluna")` antes de dividir.

2. SÉRIE TEMPORAL. Use `apenas_comparavel(df)` em qualquer comparação entre
   anos, sem ele, categoria que nasceu em 2025 vira "crescimento".

3. MÚLTIPLA ESCOLHA. Use `marcou("linguagens", "python")`, não `LIKE '%python%'`.

--------------------------------------------------------------------------
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


from pyspark.sql import functions as F  # noqa: E402

from gold_comum import (  # noqa: E402
    apenas_comparavel,
    base_da_pergunta,
    dim_faixa_salarial,
    dim_geografia,
    dim_senioridade,
    dim_tempo,
    gravar,
    indicador,
    ler_silver,
    marcou,
    pct,
    sessao,
)

# ⬇️ AJUSTE
NUMERO = "N"
PERGUNTA = "enunciado da sua pergunta aqui"
RESPONSAVEL = "seu nome"

PREFIXO = f"gold_dw_p{NUMERO}_"


def construir(silver):
    """Devolve {nome_da_tabela: DataFrame}. Escreva as suas agregações aqui."""

    tabelas = {}

    # --- exemplo 1: distribuição simples, base inteira -------------------
    tabelas["distribuicao_exemplo"] = (
        silver.groupBy("ano_pesquisa", "nivel_senioridade")
              .agg(F.count("*").alias("respondentes"))
              .orderBy("ano_pesquisa", "nivel_senioridade")
    )

    # --- exemplo 2: percentual com o denominador certo -------------------
    # `base_da_pergunta` restringe a quem VIU a pergunta.
    base = base_da_pergunta(silver, "forma_trabalho")
    tabelas["remoto_por_ano"] = indicador(
        base,
        F.col("forma_trabalho") == "Modelo_100%_remoto",
        por=["ano_pesquisa"],
        rotulo="trabalha 100% remoto",
    )

    # --- exemplo 3: múltipla escolha -------------------------------------
    base_ling = base_da_pergunta(silver, "linguagens")
    tabelas["python_por_ano"] = indicador(
        base_ling, marcou("linguagens", "python"),
        por=["ano_pesquisa"], rotulo="usa Python",
    )

    # --- exemplo 4: comparação entre anos (com o filtro) -----------------
    tabelas["senioridade_comparavel"] = (
        apenas_comparavel(silver)
        .filter(F.col("nivel_senioridade").isNotNull())
        .groupBy("ano_pesquisa", "nivel_senioridade")
        .agg(F.count("*").alias("respondentes"))
        .orderBy("ano_pesquisa", "nivel_senioridade")
    )

    return tabelas


def main():
    spark = sessao(f"tc3-gold-p{NUMERO}")
    silver = ler_silver(spark).cache()

    print(f"\n=== Gold da pergunta {NUMERO}: {RESPONSAVEL} ===")
    print(f"{PERGUNTA}\n")

    for nome, df in construir(silver).items():
        gravar(df, PREFIXO + nome)

    spark.stop()


if __name__ == "__main__":
    main()

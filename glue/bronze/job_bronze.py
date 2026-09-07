"""
Camada BRONZE: ingestão das 3 edições do State of Data Brasil.

Entrada:  os 3 CSV como baixados do Kaggle, em `entrada/`
Saída:    bronze_dw_state_data_{2023_2024, 2024_2025, 2025_2026}  (Parquet, tudo string)

O que esta camada faz:
  1. lê o CSV sem inferir tipo nenhum;
  2. grava em Parquet, uma tabela por edição;
  3. confere o contrato (linhas e colunas) e para com erro se divergir.

O que esta camada NÃO faz, por definição de SOR:
  não renomeia coluna, não tira acento, não corrige rótulo, não tipa, não junta
  edição. Nome de coluna vai como veio, inclusive `('P1_a ', 'Idade')` de
  2023-2024. Quem harmoniza é a Silver, em `glue/silver/normalizacao_bronze.py`.

Este arquivo NÃO importa nada da Silver de propósito: camada de baixo não pode
depender da de cima. As três linhas do manifesto abaixo repetem o que existe em
`config_silver.EDICOES`, e a duplicação é intencional.

Origem do código: notebook do Gusthavo (`notebooks/01_bronze.ipynb`).

Executa como Glue Job (PySpark). Grupo 21.
"""

import os
import sys

from pyspark.sql import DataFrame, SparkSession

# --------------------------------------------------------------------------- #
# caminhos: Job parameter no Glue, variável de ambiente na máquina
# --------------------------------------------------------------------------- #

def parametro(nome: str, padrao: str) -> str:
    """
    Lê uma configuração, nesta ordem de precedência:

      1. argumento de linha de comando `--NOME valor` (ou `--NOME=valor`);
      2. variável de ambiente `NOME`;
      3. o padrão.

    O passo 1 existe porque o Glue **não** transforma "Job parameter" em
    variável de ambiente: ele entrega em `sys.argv`. Um job configurado com
    `--TC3_BUCKET` que só lesse `os.getenv` cairia no padrão e escreveria no
    bucket errado, sem erro aparente.

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


BUCKET = parametro("TC3_BUCKET", "s3://tc3-grupo21-datalake")
PATH_ENTRADA = parametro("TC3_PATH_ENTRADA", f"{BUCKET}/entrada")
PATH_BRONZE = parametro("TC3_PATH_BRONZE", f"{BUCKET}/bronze/state_data")

# arquivo de origem -> tabela de destino -> contrato esperado (linhas, colunas)
EDICOES = [
    ("state_of_data_2023_2024.csv", "bronze_dw_state_data_2023_2024", 5293, 399),
    ("state_of_data_2024_2025.csv", "bronze_dw_state_data_2024_2025", 5217, 403),
    ("state_of_data_2025_2026.csv", "bronze_dw_state_data_2025_2026", 3495, 388),
]


def ler_csv(spark: SparkSession, caminho: str) -> DataFrame:
    """
    Lê o CSV da origem sem inferir nada.

    `inferSchema=false` deixa tudo string de propósito. Com a inferência ligada,
    coluna binária de texto vira float e quebra o join entre edições: afetava
    328 das 399 colunas de 2023-2024.

    `multiLine` e `escape` são necessários porque as respostas abertas da
    pesquisa têm quebra de linha e aspas dentro do campo.
    """
    return (
        spark.read
        .format("csv")
        .option("header", "true")
        .option("inferSchema", "false")
        .option("multiLine", "true")
        .option("quote", '"')
        .option("escape", '"')
        .option("encoding", "UTF-8")
        .load(caminho)
    )


def gravar(df: DataFrame, caminho: str) -> None:
    """Grava em Parquet, um arquivo por tabela. A base é pequena, não particiona."""
    df.repartition(1).write.mode("overwrite").parquet(caminho)


def main() -> None:
    spark = SparkSession.builder.appName("tc3-grupo21-bronze").getOrCreate()

    erros = []
    for arquivo, tabela, linhas_ok, colunas_ok in EDICOES:
        origem = f"{PATH_ENTRADA}/{arquivo}"
        destino = f"{PATH_BRONZE}/{tabela}"

        df = ler_csv(spark, origem)
        gravar(df, destino)

        # Confere lendo de volta o que foi gravado, não o DataFrame em memória:
        # é a Bronze em disco que a Silver vai consumir.
        gravado = spark.read.parquet(destino)
        linhas, colunas = gravado.count(), len(gravado.columns)
        situacao = "OK" if (linhas, colunas) == (linhas_ok, colunas_ok) else "DIVERGENTE"
        print(f"[{situacao}] {tabela:34s} {linhas:6d} linhas, {colunas:4d} colunas -> {destino}")
        if situacao == "DIVERGENTE":
            erros.append(
                f"{tabela}: esperado {linhas_ok} linhas e {colunas_ok} colunas, "
                f"veio {linhas} e {colunas}"
            )

    if erros:
        # Para aqui de propósito. Bronze errada gera Silver silenciosamente errada,
        # e o erro só apareceria lá na frente, no Power BI.
        raise ValueError("Contrato da Bronze não bateu:\n  " + "\n  ".join(erros))

    print(f"[OK] As 3 edições gravadas em {PATH_BRONZE}.")
    # Sem `spark.stop()`: no Glue quem encerra o contexto é o próprio serviço,
    # e parar por conta própria pode cortar a entrega dos logs.


if __name__ == "__main__":
    # `main()` direto, nunca `sys.exit(main())`: o Glue trata qualquer
    # SystemExit vindo do script como falha do job, mesmo com código 0.
    main()

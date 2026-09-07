"""
Converte os CSVs da Bronze para Parquet numa pasta local, para o notebook rodar
sem AWS.

O `test_silver_local.py` faz isso num diretório temporário e apaga no fim, bom
para o teste, ruim para o notebook, que precisa da Bronze parada em algum lugar
enquanto você explora célula a célula. Este script grava numa pasta que fica.

Uso:
    python scripts/preparar_bronze_local.py <pasta_com_os_csv> [pasta_destino]

Padrão do destino: data/bronze/

Depois disso, no notebook:
    os.environ["TC3_PATH_BRONZE"] = "../data/bronze"
    os.environ["TC3_PATH_SILVER"] = "../data/silver"
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


RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DESTINO_PADRAO = os.path.join(RAIZ, "data", "bronze")


def achar_csv(pasta, ano):
    achados = sorted(glob.glob(os.path.join(pasta, f"*{ano}.csv")))
    if not achados:
        disponiveis = [os.path.basename(p) for p in glob.glob(os.path.join(pasta, "*.csv"))]
        raise FileNotFoundError(
            f"Não achei o CSV de {ano} em {pasta}.\n"
            f"  Arquivos .csv na pasta: {disponiveis or 'nenhum'}\n"
            f"  O nome precisa terminar em '{ano}.csv'."
        )
    return achados[0]


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    pasta_csv = os.path.abspath(sys.argv[1])
    destino = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else DESTINO_PADRAO

    if not os.path.isdir(pasta_csv):
        print(f"[ERRO] Pasta não existe: {pasta_csv}")
        return 1

    from pyspark.sql import SparkSession

    import config_silver as cfg

    spark = (
        SparkSession.builder
        .appName("tc3-preparar-bronze-local")
        .master("local[*]")
        .config("spark.driver.memory", "3g")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")

    print(f"\norigem : {pasta_csv}")
    print(f"destino: {destino}\n")

    for ano, meta in cfg.EDICOES.items():
        origem = achar_csv(pasta_csv, ano)
        saida = os.path.join(destino, meta["tabela_bronze"])

        df = (
            spark.read
            .option("header", "true")
            .option("multiLine", "true")     # respostas de texto livre têm quebra de linha
            .option("escape", '"')
            .option("inferSchema", "false")  # Bronze é toda string, por decisão de camada
            .csv(origem)
        )
        linhas, colunas = df.count(), len(df.columns)
        df.write.mode("overwrite").parquet(saida)

        esperado = (meta["linhas_esperadas"], meta["colunas_esperadas"])
        marca = "OK " if (linhas, colunas) == esperado else "!! "
        print(f"[{marca}] {os.path.basename(origem):38s} -> {meta['tabela_bronze']}")
        print(f"       {linhas} x {colunas}   (esperado {esperado[0]} x {esperado[1]})")

    print(f"\nPronto. No notebook, aponte TC3_PATH_BRONZE para:\n  {destino}")
    spark.stop()
    return 0


if __name__ == "__main__":
    sys.exit(main())

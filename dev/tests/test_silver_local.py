"""
Teste local da camada Silver: roda o MESMO job_silver.py que vai para o Glue,
só que contra uma Bronze de mentira montada a partir dos CSVs.

Serve para provar a lógica antes de gastar sessão do AWS Academy Lab.

Uso:
    python tests/test_silver_local.py <pasta_com_os_csv>

Acha o CSV de cada edição por qualquer nome que termine no ano dela. Serve
tanto para `bronze_dw_state_data_2023.csv` (como o Gusthavo exporta) quanto
para `bronze_2023.csv`.

As asserções ficam em `verificacoes_silver.py`, compartilhadas com o notebook
`03b_validacao_silver.ipynb`. Este arquivo é só o runner de linha de comando.

Passo a passo completo em docs/COMO_RODAR_LOCAL.md.
"""

import os
import shutil
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
import tempfile


BASE = tempfile.mkdtemp(prefix="tc3_bronze_")
os.environ["TC3_PATH_BRONZE"] = BASE
os.environ["TC3_PATH_SILVER"] = os.path.join(BASE, "_silver")

RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

try:
    from pyspark.sql import SparkSession  # noqa: E402
except ModuleNotFoundError:
    # O erro cru é só "No module named 'pyspark'" e não diz o principal: quase
    # sempre é o Python errado, não a falta de instalação. Acontece ao usar o
    # botão ▶ do VS Code, que roda o interpretador selecionado e ignora a venv.
    print("\n[ERRO] pyspark não está instalado NESTE Python.\n")
    print(f"  Python em uso: {sys.executable}\n")
    if ".venv" not in sys.executable:
        print("  Esse não é o Python da .venv do projeto. Ative-a primeiro:\n")
        print(f'      cd "{RAIZ}"')
        print("      python -m venv .venv")
        print("      .\\.venv\\Scripts\\Activate.ps1      (Windows)")
        print("      source .venv/bin/activate          (Linux/Mac)")
        print("      pip install -r requirements.txt\n")
        print("  Com a venv ativa o prompt mostra (.venv) no começo.")
        print("  No VS Code: Ctrl+Shift+P -> 'Python: Select Interpreter' -> o da .venv.")
    else:
        print("  A venv está ativa mas falta instalar as dependências:\n")
        print("      pip install -r requirements.txt")
    print("\n  Detalhes em docs/COMO_RODAR_LOCAL.md\n")
    sys.exit(1)

from job_silver import construir_silver, validar_silver  # noqa: E402
from verificacoes_silver import montar_bronze, rodar_todas  # noqa: E402


def main(pasta_csv):
    if pasta_csv is None:
        print("\n[ERRO] Falta dizer onde estão os CSVs da Bronze.\n")
        print("  Uso:")
        print("      python tests\\test_silver_local.py \"C:\\caminho\\da\\pasta\\com\\os\\csv\"\n")
        print("  A pasta é a que tem os 3 arquivos do Gusthavo. Não precisa")
        print("  renomeá-los, basta o nome terminar no ano da edição.\n")
        return 1

    if not os.path.isdir(pasta_csv):
        print(f"\n[ERRO] Pasta não existe: {pasta_csv}")
        print(f"  (o diretório atual é {os.getcwd()})\n")
        return 1

    spark = (
        SparkSession.builder
        .appName("tc3-teste-silver")
        .master("local[*]")
        .config("spark.sql.shuffle.partitions", "8")
        .config("spark.driver.memory", "3g")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")

    try:
        print("\n=== montando Bronze de teste ===")
        montar_bronze(spark, pasta_csv, BASE)

        print("\n=== construindo Silver ===")
        silver = construir_silver(spark).cache()
        validar_silver(silver)

        v = rodar_todas(silver, {"spark": spark, "path_bronze": BASE})

        print("\n=== amostra ===")
        silver.select("sk_respondente", "ano_pesquisa", "genero", "nivel_senioridade",
                      "uf_moradia", "faixa_salarial", "salario_medio_mensal",
                      "eh_gestor", "serie_comparavel").show(6, truncate=38)

        print("\n" + v.resumo())
        return 1 if v.falhas else 0
    finally:
        spark.stop()
        shutil.rmtree(BASE, ignore_errors=True)


if __name__ == "__main__":
    # Sem default "." de propósito: rodar sem argumento a partir de uma pasta
    # qualquer dava "não achei o CSV de 2023" e escondia o erro real.
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else None))

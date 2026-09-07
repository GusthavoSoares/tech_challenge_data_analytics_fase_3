# Como rodar a Silver na sua máquina

Roda o **mesmo** `job_silver.py` que vai para o Glue, contra os CSVs da Bronze,
sem consumir sessão do AWS Academy Lab. Windows + PowerShell.

---

## O caminho curto

Se você só quer ver os resultados:

```powershell
cd "C:\caminho\para\tech_challenge_3"

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

python dev\tests\test_silver_local.py "C:\caminho\da\pasta\com\os\csv"
```

O último comando faz tudo: monta uma Bronze de mentira em Parquet a partir dos
CSVs, roda o job da Silver e imprime **86 verificações**. Leva ~2 minutos.

A pasta dos CSVs é a que tem os três arquivos do Gusthavo. Não precisa
renomeá-los, o script acha cada edição por qualquer nome que **termine no
ano** (`bronze_dw_state_data_2023.csv` funciona).

---

## Antes: dois pré-requisitos

### 1. Java

O Spark roda em JVM. Sem Java, o PySpark quebra com `JAVA_HOME is not set` ou
`Py4JJavaError` logo na primeira célula.

```powershell
java -version
```

Se não responder, instale o **JDK 11 ou 17** (não o 21, o Spark 3.5 ainda
reclama de algumas coisas nele). O Temurin resolve:

```powershell
winget install EclipseAdoptium.Temurin.17.JDK
```

Feche e reabra o PowerShell depois de instalar.

### 2. `winutils.exe`: a pegadinha do Windows

O Spark usa bibliotecas do Hadoop que **no Windows** dependem de dois arquivos
que não vêm com o pip. Sem eles você vai ver:

```
java.io.FileNotFoundException: HADOOP_HOME and hadoop.home.dir are unset
```

ou, pior, o job roda e **falha só na hora de gravar o Parquet**, depois de dois
minutos de processamento.

Resolver, um comando, sem precisar navegar no GitHub:

```powershell
New-Item -ItemType Directory -Force -Path C:\hadoop\bin | Out-Null

$base = "https://raw.githubusercontent.com/cdarlint/winutils/master/hadoop-3.3.6/bin"
Invoke-WebRequest "$base/winutils.exe" -OutFile C:\hadoop\bin\winutils.exe
Invoke-WebRequest "$base/hadoop.dll"  -OutFile C:\hadoop\bin\hadoop.dll

[Environment]::SetEnvironmentVariable("HADOOP_HOME", "C:\hadoop", "User")
```

**Reabra o PowerShell**, a variável só entra em sessão nova. Conferir:

```powershell
$env:HADOOP_HOME      # C:\hadoop
dir C:\hadoop\bin     # winutils.exe e hadoop.dll
```

### Por que a 3.3.6

O PySpark 3.5.1 empacota o Hadoop **3.3.4**, dá para confirmar assim:

```powershell
dir .venv\Lib\site-packages\pyspark\jars\hadoop-client-api-*.jar
```

O repo do `winutils` não tem a 3.3.4 (pula de 3.3.5 para 3.3.6), e dentro da
série 3.3.x os binários são compatíveis. Se um dia o `requirements.txt` subir
para uma série diferente (3.4.x, por exemplo), troque a pasta na URL pela
correspondente.

Só esses dois arquivos importam, o resto da pasta `bin` não é necessário.

> Se der muito trabalho, roda no **WSL** ou no **Colab** que nada disso é
> necessário, é problema exclusivo do Spark no Windows.

---

## Se `Activate.ps1` for bloqueado

O PowerShell bloqueia scripts por padrão:

```
não pode ser carregado porque a execução de scripts foi desabilitada
```

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

---

## O que o teste imprime

```
=== montando Bronze de teste ===
  bronze_dw_state_data_2023.csv  ->  bronze_dw_state_data_2023_2024
  ...
=== contagens por edição ===
  [OK  ] 2023: 5293 linhas, esperado 5293
  [OK  ] 2024: 5215 linhas, esperado 5215
  [OK  ] 2025: 3494 linhas, esperado 3494
  [OK  ] total = 14002, esperado 14002
=== chave ===
  [OK  ] sk_respondente é única
...
==============================================================
TODAS AS VERIFICAÇÕES PASSARAM
==============================================================
```

As 86 verificações cobrem: contagem por edição · unicidade da `sk_respondente` ·
`ano_pesquisa` conferido contra a data de envio real · domínio dos booleanos
(o `TRUE`/`FALSE` de 2024) · `uf_moradia` derivada × região · cobertura do mapa
salarial e os dois typos · marcação de comparabilidade · ausência de coluna
100% nula · e a contra-prova de cada grupo de múltipla escolha contra os
binários da origem.

**Se alguma falhar**, o resumo no fim lista quais, e o número esperado ao lado
do obtido diz onde olhar.

---

## As mesmas 86 verificações, em notebook

Se você quer ver a **evidência** de cada verificação, por que ela existe, qual
número ela está conferindo, em vez de só `OK` / `FALHA`:

```powershell
jupyter notebook notebooks\02b_validacao_silver.ipynb
```

Ajuste `PASTA_CSV` na primeira célula e rode. Ele monta a Bronze de teste,
constrói a Silver e chama as verificações uma por célula, mostrando a tabela
por trás de cada uma: a distribuição de datas de envio que valida o
`ano_pesquisa`, a comparação de `uf` contra `estado` nas três edições, a
contagem de gestores por ano que prova a normalização booleana, e assim por
diante.

As asserções ficam em `dev/tests/verificacoes_silver.py` e são importadas tanto
pelo notebook quanto pelo script, não existem duas cópias que possam divergir.

| Quero… | Uso |
|---|---|
| conferir rápido que está tudo verde | `test_silver_local.py` |
| entender ou investigar uma verificação | `02b_validacao_silver.ipynb` |

---

## Para explorar no notebook

O teste apaga a Bronze temporária no fim. Para o notebook, você precisa dela
parada em algum lugar:

```powershell
python dev\scripts\preparar_bronze_local.py "C:\caminho\da\pasta\com\os\csv"
```

Grava em `data\bronze\` e confere o shape de cada edição contra o contrato.

Depois, abra o notebook e **descomente as duas linhas** da primeira célula de
código:

```python
os.environ["TC3_PATH_BRONZE"] = "../data/bronze"
os.environ["TC3_PATH_SILVER"] = "../data/silver"
```

```powershell
jupyter notebook notebooks\02_silver.ipynb
```

Aí dá para rodar célula a célula e ver a evidência de cada achado, o drift do
`uf`, o `TRUE`/`FALSE` de 2024, os 17 grupos de múltipla escolha.

> `data\bronze\` e `data\silver\` estão no `.gitignore`. Não vão para o repo.

---

## Rodar o job direto, sem teste e sem notebook

```powershell
$env:TC3_PATH_BRONZE = "$PWD\data\bronze"
$env:TC3_PATH_SILVER = "$PWD\data\silver"
python glue\silver\job_silver.py
```

É exatamente o que o Glue executa. A diferença é só o valor dessas duas
variáveis, no Glue elas apontam para o S3. Nenhum `if` no código.

---

## Erros comuns

| Mensagem | Causa | Solução |
|---|---|---|
| `JAVA_HOME is not set` | sem Java | instalar JDK 17 |
| `HADOOP_HOME ... unset` | falta `winutils.exe` | passo 2 acima |
| `Activate.ps1 não pode ser carregado` | política do PowerShell | `Set-ExecutionPolicy` acima |
| `No module named 'pyspark'` | Python errado, não falta de instalação | ver abaixo |
| `Não achei o CSV de 2023` | pasta errada | o nome tem que terminar em `2023.csv` |
| `Bronze com N linhas, esperado 5293` | a Bronze mudou | falar com o Gusthavo antes de mexer na Silver |
| `Java heap space` | pouca memória | baixar `spark.driver.memory` para `2g` |
| trava em `Stage 0` | Windows Defender no `.venv` | adicionar exceção na pasta |

### `No module named 'pyspark'`: quase sempre é o Python errado

O `pyspark` está instalado **dentro da `.venv`**. Se você rodar com outro
Python, ele não existe. Os dois jeitos mais comuns de cair nisso:

- apertar o **botão ▶ do VS Code** ("Run Python File"), que usa o interpretador
  selecionado na janela, costuma ser o da Microsoft Store
  (`AppData\Local\Microsoft\WindowsApps\python3.11.exe`);
- abrir um terminal novo e esquecer de ativar a venv.

Descubra qual Python está rodando:

```powershell
python -c "import sys; print(sys.executable)"
```

Tem de terminar em `tech_challenge_3\.venv\Scripts\python.exe`. Se não
terminar:

```powershell
cd "...\techchallenge\tech_challenge_3"
.\.venv\Scripts\Activate.ps1
```

Com a venv ativa o prompt mostra `(.venv)` no começo. Para o botão ▶ funcionar,
`Ctrl+Shift+P` → **Python: Select Interpreter** → escolha o da `.venv`, mas
lembre que pelo botão não dá para passar a pasta dos CSVs, então prefira o
terminal.

> O script detecta esse caso e imprime o caminho do Python em uso junto com o
> que fazer, não precisa decorar.

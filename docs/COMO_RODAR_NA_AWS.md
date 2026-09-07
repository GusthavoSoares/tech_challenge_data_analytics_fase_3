# Como rodar o pipeline na AWS

Roteiro do zero: entrar no AWS Academy Lab, subir a Bronze no S3, rodar Silver e Gold como Glue
Job, catalogar e consultar no Athena.

O acesso e as regras do laboratório vêm da **Aula 3 do Módulo 1, Armazenamento de dados na
nuvem** (`fase_3/1.big_data_para_ciencia_de_dados/`), aulas 3.2 a 3.7. O que é adaptação nossa
está marcado.

---

## Parte 1: entrar no laboratório

### 1.1 O convite

Chega por e-mail, **remetente AWS Academy**, assunto "convite para o curso". Tem um botão de
começar, e é esse link que vale. Se não chegou, o professor disse para sinalizar no **Discord**
marcando o professor e o coordenador do curso.

### 1.2 Criar a conta

O link abre uma tela com duas opções: **login de estudante** e login de educador. É a primeira.

Dá para vincular uma conta Gmail, que é o caminho mais rápido, ou fazer cadastro simples com
usuário e senha.

O ambiente é o **AWS Academy**, que roda em Canvas (`awsacademy.instructure.com`). Entrar
sempre pelo link do convite na primeira vez, porque é ele que faz a matrícula.

### 1.3 Abrir o laboratório

Dentro do curso, escolher **Laboratório de Aprendizagem da AWS Academy** (AWS Academy Learner
Lab) e clicar para iniciar os laboratórios.

Na tela do lab:

- **Start Lab** provisiona o sandbox. O sinal fica **verde** quando está pronto.
- Um **timer de 4 horas** começa a correr. Quando zera, a sessão cai e você inicia outra.
- **AWS Details** mostra as credenciais para acesso local (AWS CLI, VS Code), se você quiser
  trabalhar de fora do console.
- Clicar em **AWS** abre o console, idêntico ao de produção.

### 1.4 As regras do lab, e o que elas mudam no plano

| Regra | Consequência prática |
|---|---|
| Voucher de **US$ 50** por aluno | não dá para estourar com o nosso volume; se estourar, só perde o acesso, sem cobrança |
| Sessão de **4 horas** | dá para fazer o pipeline inteiro numa sessão, mas planeje |
| **O trabalho NÃO é perdido** ao encerrar a sessão | pode parar no meio e continuar depois, bucket e tabelas continuam lá |
| Região fixa: **Norte da Virgínia (us-east-1)** | ⚠️ **não mudar para São Paulo**, o lab não funciona fora dela |
| A permissão é sempre a role **`LabRole`** | todo serviço que pedir IAM Role recebe `LabRole` |
| O Data Catalog vem **vazio** | criar o database na mão antes do crawler, `Add database` no próprio wizard |
| Conta AWS com **ID único por aluno** | fica no canto superior direito, e vai no nome do bucket |

---

## Parte 2: o nosso pipeline no lab

O que muda em relação ao hands-on da aula: lá foram dois CSV pequenos com **Visual ETL**. Aqui
são três edições da pesquisa e o código já está escrito em PySpark, então usamos o **Script
editor**, que é a opção que o próprio professor indicou para pipeline automatizada.

### 2.1 Criar o bucket

S3 → Criar bucket. O nome é **único no mundo inteiro**, então a recomendação da aula é
`lab-<id da conta>`, por exemplo `lab-123456789012`.

Estrutura de pastas dentro dele, na nossa arquitetura de camadas:

```
lab-<id>/
├── bronze/state_data/          Parquet cru, uma pasta por edição
├── silver/state_data/          Parquet unificado das 3 edições
├── gold/                       modelo dimensional (fato, dimensões, bridge)
├── scripts/                    os .py dos jobs e o módulos.zip
├── entrada/                    os 3 CSV originais do Kaggle
└── log/                        resultado das consultas do Athena
```

A pasta `log/` não é opcional: o Athena se recusa a rodar sem um local de resultado
configurado, e é ela.

### 2.2 Subir os arquivos de entrada

Arrastar os três CSV do Kaggle para `entrada/`. Upload manual mesmo, como na aula.

> A base é a mesma dos três anos: https://www.kaggle.com/datahackers/datasets

### 2.3 Empacotar os módulos auxiliares

⚠️ **Adaptação nossa, não estava na aula.** Nossos jobs importam módulos que moram ao lado
deles (`config_silver.py`, `grupos_multipla_escolha.py`, `gold_comum.py`, `dim_rotulos.py`,
`benchmark_externo.py`, `recomendacoes.py`). No Glue, isso vai como um zip.

São **sete** módulos. A lista não é chute: veio de ler os `import` dos jobs com
`ast` e seguir as dependências entre os módulos.

| Módulo | De onde | Quem importa |
|---|---|---|
| `config_silver.py` | `glue/silver/` | Silver e Gold |
| `grupos_multipla_escolha.py` | `glue/silver/` | `config_silver` e Gold |
| `normalizacao_bronze.py` | `glue/silver/` | Silver |
| `gold_comum.py` | `glue/gold/` | Gold |
| `dim_rotulos.py` | `glue/gold/` | Gold |
| `benchmark_externo.py` | `glue/gold/` | Gold |
| `recomendacoes.py` | `glue/gold/` | Gold |

O `job_bronze.py` não importa nenhum: camada de baixo não depende da de cima.

O `modulos.zip` já vem pronto na entrega. Para gerar de novo, no PowerShell,
dentro do repositório:

```powershell
Compress-Archive -Path glue\silver\config_silver.py, `
                       glue\silver\grupos_multipla_escolha.py, `
                       glue\silver\normalizacao_bronze.py, `
                       glue\gold\gold_comum.py, `
                       glue\gold\dim_rotulos.py, `
                       glue\gold\benchmark_externo.py, `
                       glue\gold\recomendacoes.py `
                 -DestinationPath modulos.zip -Force
```

> ⚠️ Os `.py` têm que ficar na **raiz** do zip, soltos, não dentro de
> `glue/silver/`. O Glue põe o zip no `sys.path`, então `from config_silver
> import ...` só resolve se o arquivo estiver no primeiro nível.

Subir `modulos.zip`, `job_bronze.py`, `job_silver.py` e `job_gold.py` para
`s3://lab-<id>/scripts/`.

### 2.4 Criar os Glue Jobs

Glue → **ETL jobs** → **Script editor** → Spark → Create.

Em **Job details**, para cada job:

| Campo | Valor |
|---|---|
| Name | `tc3-bronze`, depois `tc3-silver`, depois `tc3-gold` |
| IAM Role | **LabRole** |
| Type | Spark |
| Glue version | 4.0 ou superior (4.0 é Spark 3.3, 5.0 é Spark 3.5) |
| Language | Python 3 |
| Script path | `s3://lab-<id>/scripts/job_<camada>.py` |
| Number of workers | 2 basta para 14 mil linhas |
| Job timeout | reduzir de 480 para **60** minutos |

Em **Advanced properties**:

- **Python library path**: `s3://lab-<id>/scripts/modulos.zip`
- **Job parameters**, uma linha por variável:

| Chave | Valor |
|---|---|
| `--TC3_BUCKET` | `s3://lab-<id>` |
| `--TC3_PATH_ENTRADA` | `s3://lab-<id>/entrada` |
| `--TC3_PATH_BRONZE` | `s3://lab-<id>/bronze/state_data` |
| `--TC3_PATH_SILVER` | `s3://lab-<id>/silver/state_data` |
| `--TC3_PATH_GOLD` | `s3://lab-<id>/gold` |

> ⚠️ **O Glue não transforma Job parameter em variável de ambiente.** Ele entrega em
> `sys.argv`, como `--TC3_BUCKET s3://...`. Um script que só lê `os.getenv` cai no
> valor padrão e grava no bucket errado, sem erro aparente: o job termina como
> Succeeded e a pasta fica vazia.
>
> Por isso os três jobs usam a função `parametro()`, que lê nesta ordem: `sys.argv`,
> depois variável de ambiente, depois o padrão. Ela não importa
> `awsglue.utils.getResolvedOptions` de propósito, porque aquele módulo só existe
> dentro do Glue e quebraria a execução local. É o que mantém um arquivo só rodando
> nos dois lugares, sem `if nuvem`.

### 2.5 A ordem de execução

1. **`tc3-bronze`**: lê os 3 CSV de `entrada/` e escreve Parquet em `bronze/`.
2. **`tc3-silver`**: lê as três tabelas Bronze, harmoniza e escreve `silver/`, 14.002 linhas.
3. **`tc3-gold`**: lê a Silver e escreve o modelo dimensional em `gold/`.

Os três param sozinhos se o resultado divergir do esperado. A Bronze confere
linhas e colunas por edição, a Silver confere as 14.002 e a unicidade da chave.
Erro cedo é melhor que dashboard errado.

Cada um: **Save** e depois **Run**. Acompanhar em **Runs**. Se falhar, o erro está no
**CloudWatch** (a aula mostra: error logs, output logs, all logs).

### 2.6 Catalogar

O database **não existe até você criar**. No wizard do crawler tem `Add database`.
Nome usado: **`state_of_data`**, que nomeia o dado e não o time: a composição
do grupo muda a cada fase, e database batizado com número de turma
envelhece mal.

Duas formas de catalogar, as duas valem:

- **No próprio job**, marcando a opção de criar a tabela no Data Catalog ao escrever
  (foi o que a aula fez no Visual ETL).
- **Por Crawler**: Glue → Crawlers → apontar para `s3://lab-<id>/gold/`, role `LabRole`,
  database `state_of_data`. Roda uma vez e cria uma tabela por pasta.

O Crawler é mais prático aqui, porque a Gold tem 16 pastas e criar tabela a tabela na mão é
trabalho repetido.

### 2.7 Consultar no Athena

Athena → Editor → **Configurações**, informar o local de resultado: `s3://lab-<id>/log/`.

Database `state_of_data`, e as tabelas aparecem no painel esquerdo.

Detalhes que a aula avisa e que economizam tempo:

- O editor **não é notebook**: se houver mais de um bloco, **selecione** o que quer rodar,
  senão dá erro.
- `Ctrl+Enter` executa, `Ctrl+/` comenta.
- Athena **não é case-sensitive**.
- `LIMIT`, não `TOP` nem `ROWNUM`.
- Coluna que veio como string precisa de `CAST` para somar.

As consultas por pergunta estão em `sql/`. Rodar pelo menos uma por pergunta de negócio, e
**baixar o CSV do resultado** (botão no painel de resultados) para `results/`.

---

## Parte 3: o que printar durante a sessão

O lab guarda o trabalho, mas a apresentação precisa da prova. Tirar print **durante** a
execução, não depois:

1. **S3** com o bucket aberto mostrando as pastas `bronze/`, `silver/`, `gold/`.
2. **S3** dentro de `gold/` mostrando as pastas do modelo dimensional.
3. **Glue → ETL jobs** com os dois jobs listados.
4. **Glue → Runs** com status **Succeeded** e a duração.
5. **Glue → Job details** mostrando a Glue version e a role `LabRole`.
6. **Glue → Data Catalog → Tables** com as tabelas catalogadas.
7. **Athena** com uma consulta e o resultado na tela.
8. **CloudWatch** de uma execução, se sobrar espaço no material.

São os prints que sustentam o item "pipeline em cloud" da avaliação.

---

## Parte 4: se algo não estiver disponível no lab

O laboratório não expõe todos os serviços da AWS. Se **Glue ETL jobs** não aparecer:

- **Glue Notebook** resolve, e o enunciado aceita: "tratamento e consultas analíticas com Glue
  Notebook ou Athena". O mesmo código roda numa célula.
- Se nem o Glue aparecer, o caminho é S3 mais Athena com tabelas externas, e o Spark entra pelo
  notebook. Perde-se a catalogação automática, que passa a ser DDL manual (temos em `sql/`).

Conferir logo na primeira sessão, em **All Services**, quais desses existem: **S3**, **Glue**,
**Athena**, **CloudWatch**. É a primeira coisa a fazer depois do Start Lab, porque muda o
roteiro.

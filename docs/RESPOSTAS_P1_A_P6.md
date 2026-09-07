# Respostas das perguntas 1 a 6

**TC3 Grupo 21** · Caio Bosnic · 30/08/2026
Fonte: `gold_dw_p1_*` a `gold_dw_p6_*`, sobre a Silver (14.002 respondentes)
A pergunta 7 está em [`RESPOSTA_P7.md`](RESPOSTA_P7.md).

---

## Regra que vale para todas as respostas

A pesquisa faz perguntas condicionais: vários blocos só aparecem para parte da
base. Os denominadores das seis perguntas:

| Bloco | Quem responde | Base |
|---|---|---|
| Demografia, cargo, salário | quase todos | ~12.800 |
| Tecnologias (linguagem, cloud, BI, banco) | quem trabalha na área | ~9.400 |
| Uso individual de IA | **quem viu a pergunta de uso pessoal** | 9.494 |
| Estratégia de IA da empresa | **só gestores** | 2.593 |
| Maturidade de dados (data lake / DW) | **só engenheiros de dados** | 2.396 |
| Percepção de carreira | subconjunto | 3.372 |

Toda tabela da Gold carrega a coluna `base`. **Nunca cite um percentual sem
olhar o denominador dele.**

---

# P1: Como está estruturado o mercado brasileiro de Dados?

### O retrato em três anos

| | 2023 | 2024 | 2025 |
|---|---|---|---|
| Respondentes | 5.293 | 5.215 | 3.494 |
| Idade média | 32,0 | 32,4 | **33,7** |
| Salário médio | R$ 10.423 | R$ 11.918 | **R$ 13.048** |
| Gestores | 896 | 1.045 | 727 |

O mercado **envelheceu 1,7 ano em dois anos** e o salário médio subiu 25%. As
duas coisas andam juntas: não é inflação salarial, é mudança de composição.

### Onde estão (2025)

| Região | Profissionais | % |
|---|---|---|
| Sudeste | 2.170 | **64,4%** |
| Sul | 540 | 16,0% |
| Nordeste | 380 | 11,3% |
| Centro-oeste | 231 | 6,9% |
| Norte | 48 | 1,4% |

Concentração extrema: dois terços num único eixo.

### Em que setor (2025)

Finanças/Bancos **18,5%** · Tecnologia/Software 17,4% · Consultoria 8,8% ·
Indústria 7,3% · Varejo 5,6%.

> Relevante para o cliente: **o setor financeiro é o maior empregador da área**.
> Ele não está entrando num mercado novo, está disputando um mercado onde já é
> o maior comprador.

### Que cargo (2025)

Analista de Dados **24,0%** · Cientista de Dados 16,9% · Engenheiro de Dados
16,1% · Analista de BI 8,6% · Analytics Engineer 5,4%.

### Que formação (2025)

Pós-graduação **40,2%** · Graduação 30,6% · Mestrado 12,7% · Doutorado 4,4%.

**Mais de 57% tem pós-graduação ou acima.** É uma área de alta escolaridade
formal, o que encarece a entrada e explica a escassez de júnior.

### Como são os times (2025, base 599 gestores)

| Cargo presente no time | % |
|---|---|
| Engenheiro de Dados | 66,4% |
| Analista de Dados | 65,8% |
| Cientista de Dados | 55,9% |
| Analista de BI | 52,1% |
| Engenheiro de ML/IA | 35,4% |
| Arquiteto de Dados | 30,4% |
| DBA | 18,5% |

O time típico tem engenheiro, analista e cientista. **Engenheiro de ML/IA está
em só 1 de cada 3 times**. É a função que ainda não virou padrão.

---

# P2: Quais perfis profissionais são mais valorizados?

"Valorizado" tem duas leituras e as duas estão respondidas: quanto o mercado
**paga** e quanto o mercado **disputa**.

### Quanto paga: por cargo (três edições, 50+ respondentes)

| Cargo | n | Média | Mediana | P75 |
|---|---|---|---|---|
| **Arquiteto de Dados** | 76 | **R$ 16.553** | 14.001 | 18.001 |
| **Engenheiro de ML / IA** | 284 | **R$ 15.886** | 14.001 | **22.501** |
| Data Product Manager | 194 | R$ 12.665 | 10.001 | 14.001 |
| Engenheiro de Dados | 1.698 | R$ 12.588 | 10.001 | 14.001 |
| Analytics Engineer | 502 | R$ 11.575 | 10.001 | 14.001 |
| Cientista de Dados | 1.797 | R$ 11.572 | 10.001 | 14.001 |
| Analista de Negócios | 520 | R$ 8.251 | 7.001 | 10.001 |
| Analista de Dados | 2.463 | R$ 7.866 | 7.001 | 10.001 |
| Analista de BI | 1.117 | R$ 6.588 | 5.001 | 10.001 |

O **Engenheiro de ML/IA tem o maior P75 de todos (R$ 22.501)**, o teto da
carreira é mais alto que o do arquiteto, mesmo com média menor.

### O perfil mais valorizado, cruzando cargo e senioridade

| Perfil | n | Salário médio |
|---|---|---|
| **Engenheiro de ML/IA Sênior** | 120 | **R$ 20.180** |
| Engenheiro de Dados Sênior | 745 | R$ 16.750 |
| Cientista de Dados Sênior | 680 | R$ 15.741 |
| Analytics Engineer Sênior | 228 | R$ 14.599 |
| Analista de Dados Sênior | 708 | R$ 11.749 |

**Resposta direta: Engenheiro de ML/IA Sênior.** R$ 20.180: 72% acima de um
Analista de Dados Sênior.

### O salto entre níveis (2025)

| Nível | Salário médio | Salto |
|---|---|---|
| Júnior | R$ 4.153 | |
| Pleno | R$ 8.286 | **+99,5%** |
| Sênior | R$ 14.319 | +72,8% |
| Especialista/Staff+ | R$ 19.685 | +37,5% |

**O salto júnior → pleno dobra o salário.** É o degrau mais rentável da carreira
e o mais barato para a empresa formar internamente.

### Gestão x especialização (2025)

Gestor R$ 19.776 (n=727) contra R$ 11.092 de quem não é (n=2.500), **78% a
mais**. Mas o Especialista/Staff+ chega a R$ 19.685, praticamente empatado.
A carreira em Y funciona: dá para chegar ao mesmo patamar sem virar gestor.

### Formação paga? (2025)

Mestrado R$ 17.767 · Doutorado R$ 17.463 · Pós-graduação R$ 14.244 ·
Graduação R$ 11.344.

Mestrado paga **57% mais** que graduação. Mas atenção ao efeito de composição:
quem tem mestrado também tem mais anos de carreira.

### Quanto o mercado disputa (2025, base 838)

Tem oportunidade de progredir 53,0% · Progressão rápida 51,6% · Vagas
compatíveis com a senioridade 35,8% · Recebe muitas oportunidades 35,6%.

Só **1 em 3 acha que recebe vagas compatíveis com a própria senioridade**, há
descasamento entre o que o mercado oferece e o que o profissional acha que vale.

---

# P3: Qual é o cenário de diversidade de gênero?

Quatro perguntas distintas, e reportar só a primeira é o erro clássico.

### 1. Representação: está piorando

| Ano | Masculino | Feminino |
|---|---|---|
| 2023 | 75,1% | **24,4%** |
| 2024 | 76,1% | 23,5% |
| 2025 | **77,5%** | **22,0%** |

**A participação feminina caiu 2,4 pontos em dois anos.** Não é estagnação: é retrocesso, e é consistente nas três edições.

### 2. Equidade salarial: o gap cresce com a senioridade

Gap salarial (homens − mulheres), controlado por nível:

| Nível | 2023 | 2024 | 2025 |
|---|---|---|---|
| Júnior | 7,5% | −1,1% | 12,5% |
| Pleno | 1,3% | 3,8% | **−0,7%** |
| **Sênior** | 10,9% | 16,8% | **19,0%** |
| Especialista/Staff+ | | | 13,5% |

O achado: **no pleno não há gap** (−0,7% em 2025, ou seja, mulheres ganham
marginalmente mais). **No sênior o gap é de 19% e vem crescendo**, de 10,9%
para 19,0% em dois anos.

Em reais: sênior homem R$ 14.908, sênior mulher R$ 12.082. **R$ 2.826 por mês
pelo mesmo nível.**

### 3. Acesso à senioridade e à liderança (2025)

| | Feminino | Masculino |
|---|---|---|
| Júnior | 27,1% | 20,7% |
| Pleno | 35,2% | 36,8% |
| **Sênior** | **37,6%** | **42,5%** |
| **É gestor** | **19,1%** | **23,6%** |

A pirâmide feminina é mais jovem: mais júnior, menos sênior. E a chance de ser
gestora é **4,5 pontos menor**.

### 4. Experiência vivida (2025)

| | Feminino | Masculino |
|---|---|---|
| **Prejudicado por identidade de gênero** | **61,9%** | 4,0% |
| Não se sentiu prejudicado | 30,8% | 70,5% |

**6 em cada 10 mulheres relatam prejuízo profissional por gênero**, contra 4 em
cada 100 homens. É uma diferença de 15x.

### Síntese da P3

Os quatro indicadores contam a mesma história e ela é ruim: menos mulheres
entrando, gap salarial que **cresce** com a senioridade, menos acesso à
liderança, e prejuízo relatado por 62% delas. Não há um único indicador
melhorando.

---

# P4: Quais tecnologias têm maior adoção?

Base 2025: ~2.100 respondentes (quem trabalha na área).

### Linguagens

| | % de adoção |
|---|---|
| **Python** | **92,0%** |
| **SQL** | **84,2%** |
| R | 15,6% |
| Scala | 3,3% |
| C/C++/C# | 2,3% |

Python e SQL não são "as mais populares", são **o padrão**. Qualquer outra
linguagem é nicho.

### Cloud

AWS **48,3%** · Azure 34,8% · GCP 30,9% · On-premise 14,3% · Cloud proprietária 5,4%.

AWS lidera com folga, mas a soma passa de 100%: **multi-cloud é a norma**
(média de 1,35 cloud por profissional).

> Relevante para o TC: o pipeline do trabalho está em AWS, que é o que quase
> metade do mercado usa.

### Ferramentas de BI

**Power BI 59,0%** · Looker 22,6% · Looker Studio 15,6% · Tableau 13,6% ·
Nenhuma 11,4% · Só Excel 10,3%.

**Power BI é dominante**, quase 3x o segundo colocado.

### Bancos e plataformas de dados

PostgreSQL **36,8%** · SQL Server 33,5% · **Databricks 32,9%** · S3 28,8% ·
MySQL 28,5% · BigQuery 27,0%.

Databricks em terceiro, à frente do MySQL, é o dado que mais mudou nos últimos
anos, plataforma de lakehouse já disputa com banco relacional tradicional.

### Amplitude do stack

| Ano | Linguagens | Bancos | Clouds | BI |
|---|---|---|---|---|
| 2023 | 2,07 | 2,85 | 1,29 | 1,85 |
| 2024 | 2,11 | 2,92 | 1,24 | 1,77 |
| 2025 | 2,00 | **3,45** | 1,35 | 1,77 |

Linguagens e BI estão estáveis; **bancos cresceram 21%** (2,85 → 3,45). O stack
de armazenamento está fragmentando, o de linguagem consolidando.

---

# P5: Qual é o índice de adoção de IA e seu impacto?

⚠️ **Esta é a pergunta com o maior risco de erro de denominador.** Duas
populações: uso individual (9.494) e estratégia da empresa (2.593, só gestores).

> A coluna `uso_ia_generativa` tem **12.041** linhas preenchidas, mas a base
> correta é **9.494**. A coluna junta três perguntas (uso pessoal, organização
> na empresa e visão do gestor), e os 2.547 de diferença são gestores que
> responderam só o bloco deles, sem nunca terem sido perguntados sobre uso
> próprio. Usar 12.041 como denominador infla a adoção de 89,2% para 91,5%.
> A tabela `gold_dw_p5_quem_responde_o_que` traz as duas colunas lado a lado.

### Adoção individual: praticamente universal

| Ano | Usa IA generativa | Base |
|---|---|---|
| 2023 | 80,3% | 3.772 |
| 2024 | 93,5% | 3.617 |
| 2025 | **97,9%** | 2.105 |

**Só 2,1% não usa.** A adoção individual está saturada, não há mais o que
crescer.

### Adoção por senioridade (todas as edições)

Especialista/Staff+ 98,4% · Pleno 89,3% · Sênior 89,0% · Júnior 88,1%.

Diferença pequena, **IA não é coisa de sênior nem de júnior**, é transversal.

### Quem paga: a mudança real dos últimos dois anos

| Ano | A empresa paga | Do próprio bolso | Só gratuito |
|---|---|---|---|
| 2023 | 6,4% | 6,9% | 2.401 |
| 2024 | 19,3% | 15,5% | 1.943 |
| 2025 | **42,3%** | **26,9%** | 643 |

**A empresa pagando saltou de 6,4% para 42,3%: 6,6x em dois anos.** É o
indicador que mostra a IA saindo do experimento individual para o orçamento
corporativo. Mas ainda: 1 em cada 4 paga do próprio bolso para trabalhar melhor.

### Estratégia da empresa: base gestores

| Ano | IA é prioridade alta | Base |
|---|---|---|
| 2023 | 36,2% | 896 |
| 2024 | 53,6% | 1.045 |
| 2025 | **60,6%** | 652 |

### O gap: o achado central

| Ano | Pessoas usam | Empresas priorizam | Gap |
|---|---|---|---|
| 2023 | 80,3% | 36,2% | **44,1 p.p.** |
| 2024 | 93,5% | 53,6% | 39,9 p.p. |
| 2025 | 97,9% | 60,6% | **37,3 p.p.** |

O gap está fechando (quase 7 pontos em dois anos), mas ainda há **37 pontos de
distância** entre o que o profissional já faz e o que a empresa assumiu como
prioridade.

### O que trava (2025, base 587 gestores)

Falta de expertise **38,8%** · Falta de compreensão do caso de uso 32,0% ·
Segurança e privacidade 27,8% · Confiabilidade da saída 17,0% · Incerteza
regulatória 9,9% · Alta direção não vê valor 7,5%.

**As duas primeiras somam 71% e são de capital humano.** As barreiras que
dominam a conversa executiva (regulação, PI, ceticismo da direção) somam menos
de 27%.

---

# P6: Diferenças entre regiões, senioridades e modelos de trabalho?

**Sim, e as três dimensões interagem.**

### Região (2025)

| Região | n | % | Salário médio |
|---|---|---|---|
| Sudeste | 2.170 | 64,4% | R$ 13.387 |
| Sul | 540 | 16,0% | R$ 12.082 |
| Centro-oeste | 231 | 6,9% | R$ 12.632 |
| Norte | 48 | 1,4% | R$ 12.403 |
| Nordeste | 380 | 11,3% | **R$ 10.224** |

O Nordeste é o **único outlier para baixo**: 24% abaixo do Sudeste. Centro-oeste
e Norte pagam quase o mesmo que o Sul.

### Migração: o mercado drena as regiões periféricas

Proporção de quem nasceu na região e mora em outra (2025):

| Região de origem | % que saiu |
|---|---|
| **Norte** | **93,9%** |
| Nordeste | 83,0% |
| Centro-oeste | 79,3% |
| Sul | 57,7% |
| Sudeste | 39,6% |

**94% de quem nasce no Norte trabalha fora dele.** A concentração no Sudeste
não é só onde as pessoas nascem, é migração ativa.

### O remoto paga mais, controlando por senioridade

| Nível | Presencial/híbrido | 100% remoto | Diferença |
|---|---|---|---|
| Júnior | R$ 3.941 | R$ 4.254 | +7,9% |
| Pleno | R$ 7.444 | R$ 8.428 | +13,2% |
| Sênior | R$ 12.802 | R$ 15.180 | **+18,6%** |
| Especialista/Staff+ | R$ 17.770 | R$ 21.484 | **+20,9%** |

O prêmio do remoto **cresce com a senioridade**, de 7,9% no júnior a 20,9% no
especialista. Controlado por nível, então não é composição.

### Satisfação por modelo (2025)

| Modelo | Satisfeitos |
|---|---|
| Híbrido flexível | **75,0%** |
| 100% remoto | 74,5% |
| Híbrido com dias fixos | 67,8% |
| **100% presencial** | **54,0%** |

**21 pontos separam o presencial do híbrido flexível.** O que diferencia não é
remoto x presencial, é ter ou não **autonomia sobre quando ir**: o híbrido
flexível (75,0%) supera o híbrido de dias fixos (67,8%) em 7 pontos.

### O cruzamento das três: onde está o melhor custo-benefício

Combinações mais bem pagas (todas as edições, 20+ respondentes):

| Região | Nível | Modelo | n | Salário |
|---|---|---|---|---|
| Norte | Sênior | 100% remoto | 28 | R$ 16.893 |
| Centro-oeste | Sênior | 100% remoto | 117 | R$ 16.612 |
| Nordeste | Sênior | 100% remoto | 238 | R$ 15.156 |
| Sudeste | Sênior | 100% remoto | 1.091 | R$ 14.958 |
| Sul | Sênior | 100% remoto | 417 | R$ 14.613 |

**As cinco primeiras posições são todas "Sênior + 100% remoto"**, o modelo de
trabalho pesa mais que a região. E o sênior remoto do Norte ganha **mais** que
o do Sudeste, porque quem contrata remoto no Norte é empresa de fora pagando
salário de fora.

### Resposta direta da P6

Sim, há diferenças relevantes, mas a mais forte **não é a região**: é o
**modelo de trabalho**. Ele explica 19-21% de diferença salarial no topo da
carreira e 21 pontos de satisfação, e neutraliza a desvantagem geográfica.

---

## Reprodutibilidade

```bash
python glue/gold/job_gold_p1.py    # ... até p6
```

85 tabelas em `gold_dw_p1_*` … `gold_dw_p7_*`, cada uma com `base` explícita.
Séries entre anos usam `serie_comparavel = true`.

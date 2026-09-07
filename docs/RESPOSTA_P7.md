# Pergunta 7: Oportunidades e desafios para investir em Dados e IA

**TC3** · Caio Bosnic · 30/08/2026
Fonte: `gold_dw_p7_*`, sobre a Silver das três edições (14.002 respondentes)

> **Cliente:** instituição financeira de grande porte querendo expandir sua área
> de Dados, Analytics e IA. A pergunta 7 é a síntese: as outras seis descrevem
> o mercado, esta diz o que fazer com essa descrição.

---

## Antes de qualquer número: dois denominadores diferentes

A pesquisa faz perguntas diferentes para públicos diferentes, e misturá-los
inverte conclusões. Verificado na base:

| Bloco | Quem responde | Base |
|---|---|---|
| Uso individual de IA | **quem viu a pergunta de uso pessoal** | 9.494 |
| **Estratégia de IA da empresa** | **só gestores** (100% `eh_gestor=true`) | **2.593** |
| **Maturidade de dados (data lake / DW)** | **só engenheiros de dados** (0% gestores) | **2.396** |

São blocos condicionais do questionário, não amostragem.

⚠️ **Correção de 30/08:** uma versão anterior deste documento dizia que a
maturidade de dados também vinha de gestores. **Está errado**, nenhum gestor
responde esse bloco. Ele é respondido por engenheiros de dados não-gestores
(100% de sobreposição com `atividades_engenheiro_dados`; 66% têm cargo de
Engenheiro de Dados). E a interseção entre os dois blocos de empresa é **zero**:
ninguém responde os dois, então não existe cruzamento possível entre "prioriza
IA" e "tem data lake" nesta base.

**Consequência prática:** "61% das empresas têm IA como prioridade" é uma frase
sobre gestores. Calculada sobre os 14.002 daria 3% e estaria errada. Toda tabela
da Gold carrega a coluna `base` para o denominador ficar visível no slide.

---

## As três oportunidades

### 1. A adoção individual corre 37 pontos à frente da estratégia corporativa

| Ano | Profissionais que usam IA | Empresas em que IA é prioridade alta | Gap |
|---|---|---|---|
| 2023 | 80,3% (n=3.772) | 36,2% (n=896) | **44,1 p.p.** |
| 2024 | 93,5% (n=3.617) | 53,6% (n=1.045) | 39,9 p.p. |
| 2025 | **97,9%** (n=2.105) | **60,6%** (n=652) | 37,3 p.p. |

As duas curvas sobem, mas a de baixo sobe mais rápido, o gap caiu quase 7 pontos
em dois anos. Ainda assim, em 2025 praticamente **todo profissional de dados já usa
IA generativa no trabalho**, enquanto 4 em cada 10 empresas ainda não a tratam
como prioridade.

**A oportunidade:** a capacitação já aconteceu, por conta dos próprios
profissionais. Uma empresa que estruture o uso agora não precisa ensinar
ninguém a usar, precisa dar direção, política de dados e casos de uso. É a
diferença entre um projeto de adoção e um projeto de governança, e o segundo é
mais barato e mais rápido.

### 2. Dois terços do talento está no Sudeste: e o remoto está encolhendo

Distribuição em 2025 (n=3.369):

| Região | Profissionais | % | Salário médio |
|---|---|---|---|
| Sudeste | 2.170 | **64,4%** | R$ 13.387 |
| Sul | 540 | 16,0% | R$ 12.082 |
| Nordeste | 380 | 11,3% | R$ 10.224 |
| Centro-oeste | 231 | 6,9% | R$ 12.632 |
| Norte | 48 | 1,4% | R$ 12.403 |

O Nordeste tem salário médio **24% menor** que o Sudeste com 11% do talento.
Mas o modelo de trabalho anda na direção contrária:

| Modelo | 2023 | 2025 |
|---|---|---|
| 100% remoto | 46,3% | **39,7%** |
| 100% presencial | 16,6% | **20,8%** |

O remoto perdeu 6,6 pontos e o presencial ganhou 4,2 em dois anos.

**A oportunidade:** enquanto o mercado volta ao escritório, quem mantiver
posições remotas acessa uma bolsa de talento que os concorrentes estão
abandonando, a um custo menor. É uma janela que está se fechando, não abrindo.

### 3. O custo por perfil é conhecido e a diferença entre níveis é grande

Salário médio mensal em 2025:

| Nível | Profissionais | Média | Mediana |
|---|---|---|---|
| Júnior | 518 | R$ 4.153 | R$ 3.501 |
| Pleno | 775 | R$ 8.286 | R$ 7.001 |
| Sênior | 858 | R$ 14.319 | R$ 14.001 |
| Especialista/Staff+ | 349 | R$ 19.685 | R$ 18.001 |

Por cargo (média das três edições, cargos com 50+ respondentes):

| Cargo | Profissionais | Salário médio |
|---|---|---|
| Engenheiro de ML / IA | 243 | R$ 14.517 |
| Data Product Manager | 177 | R$ 12.246 |
| Engenheiro de Dados | 1.524 | R$ 12.131 |
| Analytics Engineer | 454 | R$ 11.171 |
| Cientista de Dados | 1.587 | R$ 11.126 |
| Analista de Dados | 2.250 | R$ 7.635 |

Um sênior custa **3,5x** um júnior. O perfil mais caro é justamente o de IA.

**A oportunidade:** formar internamente. A distância júnior → pleno é de
R$ 4.100/mês; contratar um pleno pronto custa isso a mais, mais o tempo de
processo. Com a adoção de IA já em 98%, a capacitação parte de uma base alta.

---

## Os três desafios

### 1. O que trava a IA é falta de gente, não falta de tecnologia

Barreiras apontadas por gestores em 2025 (n=587, múltipla escolha):

| Barreira | % |
|---|---|
| **Falta de expertise ou recurso** | **38,8%** |
| Falta de compreensão do caso de uso | 32,0% |
| Segurança e privacidade dos dados | 27,8% |
| Confiabilidade da saída (alucinação) | 17,0% |
| Incerteza regulatória | 9,9% |
| Propriedade intelectual | 9,2% |
| Alta direção não vê valor | 7,5% |

As duas primeiras somam 71% e são ambas de **capital humano**, saber fazer e
saber onde aplicar. As barreiras que costumam dominar a conversa executiva
(regulação, PI, ceticismo da direção) somam menos de 27% juntas.

**O desafio:** o orçamento tende a ir para ferramenta, e o gargalo é time.

### 2. A pirâmide inverteu: o mercado envelheceu e o júnior sumiu

| Nível | 2023 | 2024 | 2025 |
|---|---|---|---|
| Júnior | 29,7% | 23,0% | **22,3%** |
| Pleno | 36,6% | 36,3% | 36,3% |
| Sênior | 33,7% | 40,7% | **41,4%** |

E a experiência acompanha: profissionais com 7+ anos em dados passaram de
**20,7% para 26,6%** da base.

O júnior caiu 7,3 pontos em dois anos enquanto o sênior subiu 7,6. Não é um
mercado que está formando gente, é um mercado que está envelhecendo.

**O desafio:** contratar sênior fica mais caro e mais disputado a cada ano, e a
base de formação está encolhendo. Quem depender só do mercado para senioridade
vai pagar prêmio crescente.

*(Ressalva: a categoria `Especialista/Staff+` nasceu em 2025 e foi excluída
desta série via `serie_comparavel`, sem isso, pareceria migração de sênior.)*

### 3. A maturidade de dados está estagnada há três anos

| Ano | Base (engenheiros de dados) | Com data lake | Sem data lake nem DW |
|---|---|---|---|
| 2023 | 911 | 82,4% | 6,3% |
| 2024 | 922 | 82,6% | 6,7% |
| 2025 | 563 | 82,1% | 4,4% |

**O desafio:** 82% é um teto que não se move há três edições.

⚠️ **E esse 82% é otimista por construção.** Quem responde o bloco são
engenheiros de dados, que trabalham, por definição, em empresa que já investiu
em infraestrutura de dados. O número descreve "empresas que empregam engenheiro
de dados", não "empresas brasileiras". A fatia real sem data lake no mercado
amplo é maior do que 18%.

Mesmo com o viés a favor, quase **1 em cada 5** não tem data lake, e para
essas, um projeto de IA vira um projeto de engenharia de dados antes de virar
IA. É o item que estoura cronograma sem aparecer no plano inicial.

---

## Retenção: o custo escondido da expansão

O ambiente melhorou, mas a satisfação não acompanhou:

| Indicador | 2023 | 2024 | 2025 |
|---|---|---|---|
| Empresa passou por layoff | 32,2% | 28,6% | **24,9%** |
| Foi pessoalmente afetado | 4,4% | 3,8% | 2,9% |
| Satisfeito com a empresa atual | 72,0% | 68,6% | **69,0%** |

Layoffs caíram 7,3 pontos, mas a satisfação **caiu 3 pontos** no mesmo período.
Menos medo de demissão com menos satisfação é a combinação que antecede
rotatividade: o profissional insatisfeito volta a se sentir seguro para sair.

O que ele valoriza ao avaliar uma oportunidade (2025, n=3.227):

| Fator | % |
|---|---|
| **Remuneração** | **83,2%** |
| Flexibilidade / remoto | 56,6% |
| Plano de carreira | 32,4% |
| Benefícios | 24,5% |
| Oportunidade de aprendizado | 23,6% |
| Ambiente e clima | 21,4% |
| Maturidade em dados da empresa | 10,8% |
| Qualidade da liderança | 8,1% |

Estável nas três edições (remuneração: 81,4% → 81,0% → 83,2%).

Salário e flexibilidade são os dois únicos fatores acima de 50%. E a
flexibilidade está sendo reduzida pelo mercado justamente enquanto continua
sendo o segundo fator mais citado, o que reforça a oportunidade nº 2.

---

## O que isso recomenda ao cliente

1. **Estruturar, não evangelizar.** 97,9% dos profissionais já usam IA. O
   investimento vai para governança, política de dados e casos de uso, não
   para convencer ninguém a adotar.

2. **Tratar o gargalo como sendo de pessoas.** 71% das barreiras à IA são
   expertise e compreensão de caso de uso. Orçamento de ferramenta não resolve.

3. **Contratar remoto fora do Sudeste enquanto a janela existe.** 35% do
   talento está fora do Sudeste, custa menos, e o mercado está reduzindo
   posições remotas, o que diminui a concorrência por esse grupo.

4. **Formar júnior e pleno internamente.** A pirâmide está envelhecendo e o
   sênior custa 3,5x o júnior. Depender do mercado é apostar num estoque que
   está encolhendo.

5. **Auditar a fundação antes de aprovar cronograma de IA.** 1 em 5 empresas não
   tem data lake, e o indicador não se move há três anos. Se for o caso, o
   primeiro ano do projeto é engenharia de dados.

6. **Competir por salário e flexibilidade, nessa ordem.** São os dois únicos
   fatores acima de 50%, e são estáveis há três edições. Maturidade em dados
   (10,8%) e liderança (8,1%) são desempate, não atração.

---

## Reprodutibilidade

```bash
python glue/gold/job_gold_p7.py     # gera as 15 tabelas gold_dw_p7_*
```

Todos os números acima saem dessas tabelas, cada uma com a coluna `base`
explícita. As séries entre anos usam `serie_comparavel = true`.

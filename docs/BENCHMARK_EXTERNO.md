# Benchmark externo: contexto de mercado nas análises

**TC3 Grupo 21** · Caio Bosnic · 30/08/2026
Tabela: `gold_dw_dim_benchmark` (8 referências)
Código: `glue/gold/benchmark_externo.py`

---

## Para que serve

A State of Data descreve **quem respondeu a State of Data**: profissionais de
dados engajados o bastante para responder uma pesquisa da comunidade. É uma
amostra excelente para traçar o perfil do profissional e traiçoeira para falar
do "mercado brasileiro" em geral.

O benchmark externo resolve isso de três formas, e confundi-las é o erro que
transforma contexto em ruído:

| Uso | Pergunta que responde | Onde entra no dashboard |
|---|---|---|
| **VALIDAR** | o nosso número bate com fonte independente? | linha de referência no gráfico |
| **DELIMITAR** | até onde a nossa conclusão vale? | tooltip de página |
| **COMPLEMENTAR** | o que a nossa base não mede? | página de contexto |

---

## As oito referências

Cada uma foi conferida na fonte primária em 30/08/2026: número exato, ano de
referência, metodologia e recorte da população.

### VALIDAR: onde o nosso número se sustenta

| Nosso | Externo | Fonte | Diferença |
|---|---|---|---|
| IA é prioridade alta: **60,6%** (gestores, 2025) | **67%** organizações com IA entre as 5 prioridades | Bain, mai/2025 | −9,6% |
| IA é prioridade alta: **60,6%** | **50%** das grandes empresas (250+) usam IA | Cetic.br, 2025 | +21,2% |
| Salário Eng. de Dados: **R$ 14.083** (2025) | **R$ 14.430,84** | CAGED, jul/25 a jun/26 | **−2,4%** |
| Salário Cientista de Dados: **R$ 12.854** | **R$ 11.019,71** | CAGED, jul/25 a jun/26 | +16,6% |

**O achado mais forte é o salarial.** A Silver estima salário pelo ponto médio
da faixa declarada, o que é uma aproximação. Contra o CAGED, registro
administrativo oficial com 6.409 profissionais, a média do Engenheiro de Dados
difere **2,4%**. É a prova de que a estimativa funciona.

O Cientista de Dados fica 16,6% acima, e a diferença tem explicação: nossa base
é auto-selecionada (quem responde pesquisa da comunidade tende a estar melhor
posicionado) e inclui PJ, enquanto o CAGED cobre só CLT e salário base.

**Sobre a Bain:** ela é co-autora da própria State of Data Brasil. Quando o
nosso 60,6% chega perto do 67% que ela publicou de forma independente, isso
valida a escolha de denominador que a Gold faz (só gestores respondem o bloco).

### DELIMITAR: até onde a conclusão vale

| Nosso | Externo | Fonte |
|---|---|---|
| IA é prioridade alta: **60,6%** | **17%** das empresas brasileiras (10+) usam IA | Cetic.br, 2025 |

Os dois estão certos, e a distância não é contradição: é recorte. A nossa base
descreve **empresas que empregam profissionais de dados**; a do Cetic descreve
o parque empresarial do país, com 4.174 empresas entrevistadas por telefone.

A progressão fecha o raciocínio:

```
17%    todas as empresas com 10+ funcionários
50%    grandes empresas (250+)
60,6%  empresas que empregam profissionais de dados (nossa base)
```

É a mesma ressalva que já estava na resposta da pergunta 7 sobre os 82% com
data lake, agora com número externo sustentando.

### COMPLEMENTAR: o que a nossa base não mede

| Indicador | Valor | Fonte |
|---|---|---|
| Empresas com ROI comprovado em IA generativa | **40,7%** | Peers + MIT Tech Review, ago/2026 |
| **Bancos que superaram o business case de IA** | **72,7%** | idem |
| Déficit de formação em TI (5 anos) | **30,2%** | Brasscom, abr/2025 |

**O dado dos bancos é o mais relevante para o case.** O cliente é uma
instituição financeira de grande porte, e bancos vão muito melhor que a média
em IA generativa: 72,7% superaram o business case inicial, contra 40,7% do
total. Sustenta a recomendação de investir.

**O déficit da Brasscom explica de fora o que a nossa pirâmide mostra por
dentro.** O mercado demandou 665 mil profissionais em cinco anos e a formação
entregou 465 mil. Por isso o júnior caiu de 29,7% para 22,3% na nossa base:
não é que as empresas pararam de contratar júnior, é que ele não está sendo
formado.

---

## Como usar no Power BI

`dim_benchmark` é uma **tabela desconectada**, sem relacionamento com o fato.
Isso é de propósito: ela não descreve respondente, descreve o mercado. O job
valida que toda linha tem fonte e URL, mas não checa integridade referencial
porque não existe chave para ligar.

**1. Linha de referência (uso = VALIDAR)**

No gráfico de prioridade de IA por ano, adicionar uma linha constante em 67%
com o rótulo `Bain 2025`. O leitor vê a nossa barra e a referência no mesmo
eixo, e a proximidade fala por si.

```dax
Ref Bain IA =
CALCULATE(
    MAX(dim_benchmark[valor]),
    dim_benchmark[fonte] = "Bain & Company",
    dim_benchmark[indicador] = "IA entre as 5 prioridades estratégicas"
)
```

**2. Tooltip de página (uso = DELIMITAR)**

Página de tooltip com os três números da progressão (17% / 50% / 60,6%) e a
frase da coluna `leitura`. O leitor passa o mouse no visual de IA e entende o
recorte sem que a tela precise carregar o texto o tempo todo.

**3. Página de Fontes e Contexto (uso = COMPLEMENTAR)**

Uma página no fim com uma `tableEx` de `dim_benchmark`, mostrando indicador,
valor, fonte, ano, população e ressalva. É onde a banca confere de onde veio
cada número externo.

---

## Regras que não podem ser quebradas

**Nunca no mesmo eixo sem rótulo.** Todo valor externo que aparecer junto de um
número nosso precisa de legenda dizendo a fonte e o ano. Metodologias diferentes
produzem números diferentes para a mesma pergunta, e comparar sem ressalva é o
mesmo erro de denominador que a Silver passou a semana corrigindo.

**A coluna `ressalva` não é decorativa.** Duas fontes têm limitação declarada:

- **Bain**: o press release não publica amostra nem perfil do respondente. A
  comparação é indicativa, não rigorosa.
- **Brasscom**: fonte secundária, notícia citando relatório sem título nem data
  exata do estudo original.

Se algum desses números for para o slide principal, a ressalva vai junto.

**`diferenca_pct` só existe para `uso = VALIDAR`.** Calcular diferença
percentual entre o nosso 60,6% e o 17% do Cetic seria matematicamente possível
e conceitualmente errado: eles medem populações diferentes. A coluna vem nula
de propósito nos outros usos.

**Ano de referência não é ano de publicação.** As duas colunas existem separadas
porque o Cetic publicou em jun/2026 dados de 2025, e a diferença importa quando
alguém for atualizar.

---

## Manutenção

Para trocar ou acrescentar referência, mexer só em
`glue/gold/benchmark_externo.py` e rodar `python glue/gold/job_gold.py`. A
tabela é regerada e o dashboard acompanha, sem caixa de texto solta para
atualizar.

Ao acrescentar, preencher **todos** os campos, inclusive `populacao`,
`amostra` e `ressalva`. Referência sem metodologia declarada é opinião com
número, e a banca pergunta.

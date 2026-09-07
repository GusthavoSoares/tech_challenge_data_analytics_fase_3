# Modelo da camada Gold: TC3 Grupo 21

**Uma Gold, um modelo dimensional, sete perguntas.**
Caio Bosnic · 30/08/2026

---

## A decisão

A Gold é **um star schema só**. As sete perguntas de negócio não têm cada uma
a sua Gold, elas viram consulta no Athena ou medida DAX sobre este mesmo
modelo.

Foi assim que ficou registrado em `DECISOES_E_ACHADOS.md`
(`gold_dw_fat_profissionais` + dimensões), e é o que o Power BI precisa: 85
tabelas agregadas soltas não se relacionam entre si, não têm chave em comum e
não permitem um filtro cruzar páginas.

---

## O modelo

```
                          gold_dw_dim_tempo (3)
                                   │
   dim_geografia (27) ─────┐       │       ┌───── dim_cargo (18)
   dim_senioridade (4) ────┤       │       ├───── dim_setor (21)
   dim_faixa_salarial (13)─┤       │       ├───── dim_genero (4)
   dim_modelo_trabalho (4)─┼──  gold_dw_fat_profissionais  ──┼─ dim_formacao (7)
   dim_tempo_experiencia(8)┘      14.002 linhas             └─ dim_area_formacao (9)
                                   │
                                   │  sk_respondente
                                   ▼
                    gold_dw_bridge_respondente_opcao (378.231)
                                   │  sk_opcao
                                   ▼
                        gold_dw_dim_opcao (529)
```

| Tabela | Linhas | Papel |
|---|---|---|
| `gold_dw_fat_profissionais` | **14.002** | fato · 1 respondente por edição |
| `gold_dw_dim_tempo` | 3 | a edição é o grão de tempo |
| `gold_dw_dim_geografia` | 28 | UF, estado, região, país |
| `gold_dw_dim_cargo` | 20 | cargo + família, com os 2 membros de ausência |
| `gold_dw_dim_senioridade` | 6 | com `ordem` |
| `gold_dw_dim_faixa_salarial` | 14 | `ordem`, limites e ponto médio |
| `gold_dw_dim_setor` | 22 | |
| `gold_dw_dim_formacao` | 7 | com `ordem` |
| `gold_dw_dim_area_formacao` | 10 | |
| `gold_dw_dim_modelo_trabalho` | 5 | flags de remoto e autonomia |
| `gold_dw_dim_genero` | 4 | |
| `gold_dw_dim_tempo_experiencia` | 9 | com `ordem` |
| `gold_dw_dim_opcao` | 529 | catálogo das opções de múltipla escolha |
| `gold_dw_bridge_respondente_opcao` | 378.231 | liga o fato às opções marcadas |
| `gold_dw_dim_benchmark` | 8 | referências externas de mercado (desconectada) |
| `gold_dw_dim_recomendacao` | 6 | as decisões recomendadas ao cliente (desconectada) |

**16 tabelas.** Um fato, 12 dimensões, um catálogo, uma bridge e a tabela de
recomendações.

As contagens das dimensões incluem os **membros de ausência nomeados**: em vez
de deixar a FK nula e o Power BI inventar um membro "(Em branco)", a Gold grava
"Gestor, sem cargo técnico", "Fora da área de dados" e "Não declarado". É por
isso que `dim_cargo` tem 20 linhas e não 18.

`dim_benchmark` e `dim_recomendacao` são as únicas **sem relacionamento com o
fato**, de propósito: não descrevem respondente. A primeira traz 8 referências
externas conferidas na fonte primária, para validar, delimitar ou complementar
os nossos números (ver [`BENCHMARK_EXTERNO.md`](BENCHMARK_EXTERNO.md)). A
segunda traz as seis decisões da página de Oportunidades, cada uma com o
indicador, o valor e a base que a sustentam.

---

## Por que a bridge existe

Os 22 grupos de múltipla escolha vivem na Silver como string: `"python, sql, r"`.
Isso é legível e péssimo para relacionar, filtrar "quem usa Python" exigiria
`CONTAINS` dentro de cada medida DAX.

A bridge explode cada opção marcada em uma linha:

| sk_respondente | sk_opcao | ano_pesquisa |
|---|---|---|
| f5b3fbc… | a1b2… (linguagens/python) | 2025 |
| f5b3fbc… | c3d4… (linguagens/sql) | 2025 |
| f5b3fbc… | e5f6… (clouds/aws) | 2025 |

No Power BI vira: `fat_profissionais` 1→N `bridge` N→1 `dim_opcao`. Um slicer
em `dim_opcao[opcao_rotulo]` filtra o fato inteiro.

**Só entram linhas de quem MARCOU.** Quem não respondeu o bloco não aparece. Isso é intencional: a contagem de uma
opção nunca deve incluir quem nunca viu a pergunta.

`dim_opcao` traz `comparavel_entre_anos` (booleano): **5 dos 22 grupos** têm
rótulo que não harmoniza entre edições. Filtre por essa coluna antes de montar
série temporal de múltipla escolha.

### Um grupo que eram três: `uso_ia_generativa`

A Silver agrupa coluna de múltipla escolha por máscara de resposta. Isso resolve
19 dos 20 grupos originais e erra num: `uso_ia_generativa` juntava **três
perguntas** que a pesquisa faz a públicos diferentes. Medido na bridge, opção
por opção, contra `eh_gestor` do fato, a separação é exata:

| grupo | pessoas | quem responde | pergunta |
|---|---|---|---|
| `uso_ia_pessoal` | 9.494 | nenhum gestor | como VOCÊ usa IA generativa |
| `uso_ia_empresa` | 9.494 | os mesmos | como a empresa em que você trabalha usa |
| `uso_ia_gestor` | 2.505 | só gestores | o bloco de estratégia da empresa |

Nenhuma das 30 opções aparece nos dois públicos: as 20 do bloco de não gestor
têm zero gestor marcando, e as 10 do bloco de gestor têm zero não gestor. O job
quebra se isso deixar de valer (guarda de regressão em `validar`).

Enquanto os três eram um grupo só, `% de adoção` dividia tudo por 11.999, a
união dos dois públicos, e os dois gráficos da página de IA mostravam a mesma
lista de opções misturadas. Depois da divisão, "a empresa paga a ferramenta"
sai 19,3% (1.828 de 9.494) em vez de 15,2% (1.828 de 11.999).

**O sufixo `_1` de 2023.** A pergunta sobre a empresa mudou de nome de coluna
entre as edições: em 2023-2024 vem com sufixo `_1`
(`colaboradores_uso_ia_descentra_independ_1`), em 2024-2025 e 2025-2026 vem como
`ia_llm_empresa_*`. Os pares levam o mesmo rótulo em `dim_rotulos`, de propósito,
para as três edições caírem na mesma barra. Rótulo diferente ali não é detalhe
de texto: parte a série em duas.

---

## Por que NÃO há `dim_calendario`

A pesquisa é anual e não tem data de evento, o grão de tempo é a edição. Uma
tabela de datas com 1.095 linhas para 3 valores distintos cria relacionamento
morto e confunde quem for usar. `dim_tempo` tem 3 linhas e é isso.

Decisão registrada em `DECISOES_E_ACHADOS.md`.

---

## O fato

Grão: **1 respondente por edição**, o mesmo da Silver. A Gold aqui **conforma**,
não agrega: as agregações são medidas no Power BI e consultas no Athena.

**Chaves:** `sk_respondente` (PK) + 10 FKs para as dimensões, particionado por
`ano_pesquisa`.

**Métricas:** `idade`, `salario_estimado`.

**Flags** (`boolean`, prontas para `COUNTROWS` em DAX):
`eh_gestor` · `pcd_flag` · `vive_brasil` · `satisfeito_empresa` ·
`empresa_possui_datalake` · `empresa_possui_dw` · `houve_layoff` ·
`fui_afetado_layoff` · `usa_ia_generativa` · `serie_comparavel`

**Flags de denominador**, as mais importantes do modelo:
`respondeu_bloco_ia_empresa` · `respondeu_bloco_maturidade`

**Contagens:** `qtd_linguagens`, `qtd_clouds`, … (uma por grupo).

**Degenerados** (cardinalidade baixa demais para virar dimensão):
`edicao` · `cor_raca_etnia` · `pcd` · `faixa_etaria` · `ia_gen_prioridade` ·
`empresa_passou_layoff` · `llms_bom_resultado`

---

## ⚠️ A armadilha que o modelo não resolve sozinho

As FKs são nulas onde a pergunta não foi feita. Isso é correto, não é erro:

| FK | Preenchida |
|---|---|
| `sk_geografia` | 13.620 de 14.002 |
| `sk_faixa_salarial` · `sk_setor` · `sk_modelo_trabalho` | 12.841 |
| `sk_cargo` · `sk_senioridade` | 10.173 |

E três blocos são condicionais de público:

| Flag ou coluna | Quem responde | n |
|---|---|---|
| `respondeu_bloco_ia_empresa` | **só gestores** | 2.593 |
| `respondeu_bloco_maturidade` | **só engenheiros de dados** | 2.396 |
| `usa_ia_generativa` | **só quem NÃO é gestor** | 9.494 |

**A interseção entre os dois primeiros é ZERO**, ninguém responde os dois.
Não existe cruzamento possível entre "prioriza IA" e "tem data lake".

⚠️ `usa_ia_generativa` deriva **só das opções de uso pessoal**, nunca de "a
coluna do grupo está preenchida". Como `uso_ia_generativa` junta três perguntas
(ver acima), a regra frouxa faz o gestor que respondeu só o bloco da empresa
sair como usuário de IA: **2.547 gestores marcados True e nenhum False**, o que
é impossível numa pergunta de verdade, e a taxa vira 91,5% sobre 12.041 em vez
de **89,2% sobre 9.494**.

Em DAX, toda medida de percentual precisa restringir o denominador:

```dax
-- ERRADO: divide por 14.002
% Prioriza IA = DIVIDE([Gestores com IA prioritária], COUNTROWS(fat_profissionais))

-- CERTO: divide por quem viu a pergunta
% Prioriza IA =
DIVIDE(
    [Gestores com IA prioritária],
    CALCULATE(COUNTROWS(fat_profissionais),
              fat_profissionais[respondeu_bloco_ia_empresa] = TRUE)
)
```

O primeiro devolve 3%. O segundo, 61%. **Um fator de 20.**

---

## Rótulos

A Silver guarda o valor como veio da origem (`pbi`, `Modelo_100%_remoto`).
Cada dimensão carrega os dois:

- `valor`, igual à Silver, é a chave de junção e permite conferência
- `rotulo`, o que aparece no gráfico (`Power BI`, `100% remoto`)
- `ordem`, onde a ordem importa, senão o Power BI ordena alfabeticamente e
  "Júnior" aparece depois de "Especialista"

Os mapas ficam em `glue/gold/dim_rotulos.py`.

---

## As 85 análises continuam existindo: como conferência

`glue/gold/analises/job_gold_p1.py` … `p7.py` produzem as 85 tabelas agregadas
que responderam as sete perguntas. Elas **não fazem parte do modelo**, são a
prova independente.

Se um visual do Power BI não bater com a tabela correspondente, há erro em um
dos dois. Já usei isso: adoção de Python em 2025 dá **1.928 de 2.095 (92,0%)**
pelos dois caminhos, e o salário médio por senioridade bate nos quatro níveis.

---

## Rodar

```bash
python glue/gold/job_gold.py              # o modelo: 14 tabelas
python glue/gold/analises/job_gold_p1.py  # a conferência: 85 tabelas
```

O job valida antes de gravar: contagem do fato, unicidade da chave e
integridade referencial de todas as FKs e da bridge. Se algo não fechar, ele
falha em vez de publicar número errado.

---

## Para o Power BI

Relacionamentos a criar (todos **muitos-para-um**, direção simples):

```
fat_profissionais[ano_pesquisa]        → dim_tempo[ano_pesquisa]
fat_profissionais[sk_geografia]        → dim_geografia[sk_geografia]
fat_profissionais[sk_cargo]            → dim_cargo[sk_cargo]
fat_profissionais[sk_senioridade]      → dim_senioridade[sk_senioridade]
fat_profissionais[sk_setor]            → dim_setor[sk_setor]
fat_profissionais[sk_genero_valor]     → dim_genero[sk_genero_valor]
fat_profissionais[sk_nivel_ensino]     → dim_formacao[sk_nivel_ensino]
fat_profissionais[sk_area_formacao]    → dim_area_formacao[sk_area_formacao]
fat_profissionais[sk_modelo_trabalho]  → dim_modelo_trabalho[sk_modelo_trabalho]
fat_profissionais[sk_tempo_experiencia]→ dim_tempo_experiencia[sk_tempo_experiencia]
fat_profissionais[sk_faixa_salarial]   → dim_faixa_salarial[sk_faixa_salarial]

fat_profissionais[sk_respondente] 1→N  bridge[sk_respondente]
bridge[sk_opcao]                  N→1  dim_opcao[sk_opcao]
```

A bridge é o único relacionamento **bidirecional**, sem isso, o slicer de
tecnologia não filtra o fato.

`SortByColumn`: `dim_senioridade[rotulo]` por `[ordem]`, e o mesmo em
`dim_faixa_salarial`, `dim_formacao` e `dim_tempo_experiencia`.

Mapa: use `dim_geografia[uf]` com Categoria de Dados = **Estado ou Província**.
O Power BI **não geocodifica** macrorregião brasileira (`regiao`): mapa por
região só sai agregando os estados.

# Medidas DAX: TC3 Grupo 21

Todas as medidas ficam em uma tabela vazia chamada `_Medidas`
(Inserir dados, tabela sem coluna, Ocultar a coluna). Assim elas não se misturam
com os campos do modelo no painel.

Ordem de leitura: **§1 base**, depois **§2 denominadores**. As demais seções são
por página, e quase toda medida de página é uma variação de §2. Se você entender
a §2, o resto sai sozinho.

---

As medidas estão criadas no modelo do dashboard. Este documento é o dicionário
delas: o que cada uma calcula, sobre qual denominador, e por que o denominador é
aquele. É a referência para auditar qualquer número da apresentação.

---

## §1 Medidas de base

```dax
Respondentes = COUNTROWS(fat_profissionais)

Salário médio = AVERAGE(fat_profissionais[salario_estimado])

Salário mediano = MEDIAN(fat_profissionais[salario_estimado])

Idade média = AVERAGE(fat_profissionais[idade])

Gestores = CALCULATE([Respondentes], fat_profissionais[eh_gestor] = TRUE)
```

`salario_estimado` é o **ponto médio da faixa declarada**, não salário informado.
Todo visual de salário leva no título ou na dica de ferramenta a palavra
"estimado". Contra o CAGED, a média do Engenheiro de Dados difere 2,4%
(ver `docs/BENCHMARK_EXTERNO.md`).

---

## §2 Os denominadores: a parte que decide se o número está certo

Vários blocos da pesquisa são **condicionais**: a pessoa só vê a pergunta se se
encaixa no perfil. Dividir por 14.002 nesses casos não devolve um número
aproximado, devolve um número errado por um fator de 20.

```dax
Base bloco IA empresa =
CALCULATE([Respondentes], fat_profissionais[respondeu_bloco_ia_empresa] = TRUE)
-- 2.593 no total das 3 edições, SÓ GESTORES

Base bloco maturidade =
CALCULATE([Respondentes], fat_profissionais[respondeu_bloco_maturidade] = TRUE)
-- 2.396, SÓ ENGENHEIROS DE DADOS

Base empregados =
CALCULATE([Respondentes], NOT ISBLANK(fat_profissionais[sk_cargo]))
-- 10.173: cargo e senioridade só existem para quem está empregado na área

Base uso de IA =
CALCULATE([Respondentes], NOT ISBLANK(fat_profissionais[usa_ia_generativa]))
-- 9.494, SÓ QUEM NÃO É GESTOR: gestor não vê a pergunta de uso pessoal
```

O padrão de toda medida percentual é o mesmo:

```dax
% IA é prioridade alta =
DIVIDE(
    CALCULATE([Respondentes], fat_profissionais[ia_prioridade_alta] = TRUE),
    [Base bloco IA empresa]
)
```

`ia_prioridade_alta` já vem calculada da Gold: são as duas respostas que
começam com "Sim,". A regra fica no código do job, e não espalhada em medida,
para o dashboard e as tabelas de conferência contarem a mesma coisa por
construção. A frase crua da pesquisa continua em `ia_gen_prioridade`, e a versão
legível para eixo de gráfico em `ia_gen_prioridade_rotulo`.

Sobre 14.002 isso dá 3%. Sobre a base certa, 61%.

**Nunca escreva `DIVIDE(x, [Respondentes])` sem antes perguntar quem viu a
pergunta.** Se a resposta não for "todo mundo", a medida está errada.

A interseção entre `respondeu_bloco_ia_empresa` e `respondeu_bloco_maturidade`
é **zero**: não existe medida que cruze prioridade de IA com data lake.

### O terceiro denominador

`Base uso de IA` vale **9.494**, não 12.041. A pergunta de uso pessoal ("como
você usa IA generativa") **não é feita a gestor**, e a coluna
`uso_ia_generativa` junta três perguntas: gestor que respondeu só o bloco da
empresa tem a coluna preenchida sem nunca ter sido perguntado sobre uso
próprio. São 2.547 pessoas.

| denominador | base | % usa IA |
|---|---|---|
| coluna preenchida | 12.041 | 91,5% |
| **quem viu a pergunta** | **9.494** | **89,2%** |

A correção é na Gold, não em DAX: ver `SUBGRUPO` e `_IA_PESSOAL` em
`glue/gold/job_gold.py`. A medida não mudou de fórmula, mudou de base porque a
coluna passou a ser nula para quem não viu a pergunta, que é o comportamento
correto de toda FK deste modelo.

---

## §3 Múltipla escolha, via bridge

Tecnologia, barreiras e fatores de emprego vivem em
`bridge_respondente_opcao` → `dim_opcao`. A bridge só tem linha de quem
**marcou**, então a contagem já exclui quem não viu a pergunta.

```dax
Pessoas que marcaram =
CALCULATE(DISTINCTCOUNT(bridge_respondente_opcao[sk_respondente]))

Base do grupo =
-- quem respondeu QUALQUER opção do grupo selecionado
VAR _Grupo = SELECTEDVALUE(dim_opcao[grupo])
RETURN
CALCULATE(
    DISTINCTCOUNT(bridge_respondente_opcao[sk_respondente]),
    REMOVEFILTERS(dim_opcao[opcao_rotulo]),
    dim_opcao[grupo] = _Grupo
)

% de adoção = DIVIDE([Pessoas que marcaram], [Base do grupo])
```

Em 2025, Python dá **1.928 de 2.095 (92,0%)**, e é o mesmo número que a tabela
de conferência `glue/gold/analises/job_gold_p4.py` produz. Se der diferente, um
dos dois está errado: confira antes de publicar.

⚠️ **`Base do grupo` só é honesta se o grupo for UMA pergunta.** Foi por isso
que `uso_ia_generativa` teve de ser dividido em `uso_ia_pessoal`,
`uso_ia_empresa` e `uso_ia_gestor` (ver `docs/MODELO_GOLD.md`): enquanto os três
eram um grupo só, o denominador somava 9.494 não gestores com 2.505 gestores e
devolvia 11.999, uma base que nenhuma das perguntas tem.

**Série temporal de múltipla escolha exige filtro extra.** Cinco dos vinte e dois
grupos têm rótulo que não harmoniza entre edições:

```dax
% de adoção (comparável) =
CALCULATE([% de adoção], dim_opcao[comparavel_entre_anos] = TRUE)
```

Use esta variante em qualquer visual com o ano no eixo. Na foto de um ano só,
use a versão normal.

---

## §4 Diversidade

Comparação bruta de salário entre gêneros mistura duas coisas: diferença de
remuneração e diferença de composição (a pirâmide feminina é mais jovem). O gap
sai **controlado por senioridade**, sempre.

```dax
Salário médio homens =
CALCULATE([Salário médio], dim_genero[rotulo] = "Masculino")

Salário médio mulheres =
CALCULATE([Salário médio], dim_genero[rotulo] = "Feminino")

Gap salarial % =
DIVIDE([Salário médio homens] - [Salário médio mulheres], [Salário médio homens])
```

Com `dim_senioridade[rotulo]` no eixo, `Gap salarial %` responde a pergunta
certa. Sem ele, responde outra pergunta e parece a mesma.

```dax
% mulheres =
DIVIDE(
    CALCULATE([Respondentes], dim_genero[rotulo] = "Feminino"),
    CALCULATE([Respondentes], REMOVEFILTERS(dim_genero))
)

% que é gestor =
DIVIDE([Gestores], [Respondentes])
```

`% que é gestor` com gênero no eixo mede **acesso à liderança**, e é diferente de
"quantos gestores são mulheres". A primeira compara dentro de cada grupo, a
segunda compara a composição do topo. As duas são válidas e dizem coisas
diferentes: escreva no título qual delas está no gráfico.

---

## §5 Recortes: região, senioridade e modelo

```dax
% remoto =
DIVIDE(
    CALCULATE([Respondentes], dim_modelo_trabalho[eh_remoto] = TRUE),
    CALCULATE([Respondentes], NOT ISBLANK(fat_profissionais[sk_modelo_trabalho]))
)

Salário médio nacional =
CALCULATE([Salário médio], REMOVEFILTERS(dim_geografia))

Índice vs nacional = DIVIDE([Salário médio], [Salário médio nacional]) - 1
```

`Índice vs nacional` com formatação percentual e cores divergentes resolve o mapa
sem precisar de escala absoluta, que sempre esconde a diferença entre estados
pequenos.

Mapa: `dim_geografia[uf]`, Categoria de Dados = **Estado ou Província**. O Power
BI **não geocodifica** macrorregião (`regiao`), use a sigla.

---

## §6 Benchmark externo

`dim_benchmark` é **desconectada** de propósito: ela descreve o mercado, não o
respondente. Nenhum filtro do modelo a atinge, e é isso que se quer de uma linha
de referência.

```dax
Ref Bain IA =
CALCULATE(
    MAX(dim_benchmark[valor]),
    dim_benchmark[fonte] = "Bain & Company",
    dim_benchmark[indicador] = "IA entre as 5 prioridades estratégicas"
)

Rótulo da referência =
VAR _F = CALCULATE(MAX(dim_benchmark[fonte]), dim_benchmark[uso] = "VALIDAR")
VAR _A = CALCULATE(MAX(dim_benchmark[ano_referencia]), dim_benchmark[uso] = "VALIDAR")
RETURN _F & " " & _A
```

Linha constante no gráfico: Analytics, Linha constante, valor = `Ref Bain IA`,
rótulo = `Rótulo da referência`. **Valor externo sem legenda de fonte e ano não
entra no eixo**, é a mesma regra do arquivo de benchmark.

---

## §7 Medidas de texto para os tooltips

O tooltip de denominador existe para o número não precisar carregar a ressalva no
próprio título.

```dax
Texto da base =
VAR _B = [Base bloco IA empresa]
VAR _T = [Respondentes]
RETURN
    FORMAT(_B, "#.##0") & " de " & FORMAT(_T, "#.##0") &
    " (" & FORMAT(DIVIDE(_B, _T), "0,0%") & " da seleção)"

Quem responde este bloco = "Só gestores. Quem não é gestor não vê a pergunta."
```

---

## §8 Formatação e ordenação, o que sempre esquece

`SortByColumn` obrigatório, senão o Power BI ordena alfabeticamente e Júnior
aparece depois de Especialista:

| Tabela | Coluna | Ordenar por |
|---|---|---|
| `dim_senioridade` | `rotulo` | `ordem` |
| `dim_faixa_salarial` | `rotulo` | `ordem` |
| `dim_formacao` | `rotulo` | `ordem` |
| `dim_tempo_experiencia` | `rotulo` | `ordem` |

Formato das medidas: salário em `R$ #.##0`, percentual em `0,0%`, contagem em
`#.##0`. Definir no campo da medida, não no visual: assim vale em todo lugar,
inclusive na dica de ferramenta.

# Material executivo

`material_executivo_tc3.pptx` e `material_executivo_tc3.pdf`: o mesmo conteúdo
nos dois formatos, 25 slides. É o **entregável 1** do enunciado.

O `.pptx` é para editar antes de apresentar. O `.pdf` é para enviar, porque não
depende de fonte instalada na outra máquina.

## Como está organizado

| Slides | O quê |
|---|---|
| 1 a 3 | capa, o problema de negócio e a tese que o trabalho sustenta |
| 4 a 6 | a arquitetura na AWS, o que o pipeline processou e o método dos denominadores |
| 7 a 21 | as sete perguntas, duas a três telas cada |
| 22 | as seis recomendações ao cliente, com o indicador e a base de cada uma |
| 23 a 25 | validação contra fonte externa, limitações e fechamento |

O desenho da arquitetura está no slide 4, dentro do material, como o enunciado
pede. A fonte editável dele é [`../docs/arquitetura_tc3.drawio`](../docs/arquitetura_tc3.drawio).

## De onde vêm os gráficos

Os 16 gráficos saem de
[`../notebooks/04_analises_e_graficos.ipynb`](../notebooks/04_analises_e_graficos.ipynb),
que lê a Gold e grava os PNG em `../results/graficos/`. Rodar o notebook de novo
regenera todos, então apresentação e código não têm como divergir.

Os números batem com os CSV de `../results/`, que saíram do Athena pelas
consultas de `../sql/perguntas/`. São dois motores diferentes chegando ao mesmo
lugar.

## Para regerar a apresentação

O gerador é `gerar_apresentacao/`, fora do repositório por ser ferramenta de
construção. O que vale versionar é o resultado.

# O que falta

Entregáveis e decisões ainda abertos. Ordem de prioridade.

---

## Entregáveis

| O que | Onde começa |
|---|---|
| Apresentação executiva (PPT) | a partir dos prints do dashboard e dos números de `results/` |
| Desenho da arquitetura no draw.io | conferir se `docs/arquitetura_tc3.png` atende ou refazer com as três camadas e o Data Catalog transversal |
| Notebooks `03_gold.ipynb` e `04_analises_e_graficos.ipynb` | `notebooks/` hoje tem Bronze, Silver e a validação da Silver |

## Aberto com o grupo

**Contagem de 2023.** O SQL do Gusthavo comenta 5.923 respostas, e a Silver tem
5.293. Os dígitos são os mesmos em ordem diferente, o que sugere digitação, mas
vale confirmar antes de assumir.

## Ajuste cosmético no catálogo

A tabela da Silver aparece no Glue Data Catalog como `state_data`, porque o
crawler nomeia pela última pasta do caminho (`silver/state_data/`). Destoa de
`bronze_dw_*` e `gold_dw_*`. Resolve com uma `CREATE VIEW` no Athena, ou
apontando o crawler para um caminho com o nome desejado.

## Git

Existe um repositório em `techchallenge/` cobrindo os três Tech Challenges, então
`git init` dentro desta pasta criaria um repositório aninhado. Conferir
`git remote -v` antes de decidir os comandos de push.

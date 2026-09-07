"""
As seis decisões que a análise recomenda ao cliente, cada uma com o indicador
que a sustenta.

POR QUE ISSO É UMA TABELA E NÃO UM TEXTO NA IMAGEM

O card "O que isso recomenda ao cliente" fecha a página de Oportunidades e é a
única parte do dashboard que sai do descritivo e vira decisão. Escrever isso no
plano de fundo deixaria a recomendação separada do número que a sustenta: se o
filtro mudar, o número muda e a frase não. Aqui cada linha carrega o indicador,
o valor e a página onde ele pode ser conferido.

⚠️ TODO VALOR DESTA TABELA FOI CONFERIDO CONTRA A GOLD

Nenhum número aqui é estimativa ou memória. Cada um foi calculado sobre
`gold_dw_fat_profissionais` e `gold_dw_bridge_respondente_opcao`,
com a base explícita ao lado. Quando o valor depende de um recorte, o recorte
está escrito: percentual sem denominador declarado é o erro que este trabalho
inteiro existe para não cometer.

⚠️ A COLUNA CHAMA `valor_indicador`, E NÃO `valor`, DE PROPÓSITO

⚠️ A coluna se chama `valor_indicador`, e não `valor`, de propósito: `valor` é
o nome da coluna NUMÉRICA de `dim_benchmark`. Ferramenta que tipa por nome de
coluna lê este texto como número, e "82,4%" vira 8,24 em cultura en-US, que
interpreta a vírgula como separador de milhar. Nome de coluna não é tipo.
"""

RECOMENDACOES = [
    {
        "ordem": 1,
        "decisao": "Investir em governança de IA, não em treinamento de IA",
        "por_que": "A capacitação individual já aconteceu sozinha. O que não "
                   "existe é decisão corporativa: quase 4 em cada 10 pontos "
                   "separam o que a pessoa faz do que a empresa prioriza.",
        "indicador": "Gap entre adoção pessoal e prioridade da empresa",
        "valor_indicador": "89,2% x 49,3%, distância de 39,9 pontos",
        "base": "9.494 não gestores e 2.593 gestores",
        "onde_ver": "Adoção de IA",
    },
    {
        "ordem": 2,
        "decisao": "Abrir vaga fora do eixo Sudeste antes de disputar preço nele",
        "por_que": "Mais de um terço do mercado está fora do Sudeste e o "
                   "salário médio no Nordeste é 25% menor que o do Sudeste, "
                   "para o mesmo tipo de cargo.",
        "indicador": "Profissionais fora do Sudeste",
        "valor_indicador": "37,8%, com média de R$ 9.159 no Nordeste contra R$ 12.176",
        "base": "13.620 que declararam o estado",
        "onde_ver": "Região e modelo",
    },
    {
        "ordem": 3,
        "decisao": "Formar pleno a partir do júnior em vez de contratar sênior",
        "por_que": "O sênior custa três vezes e meia o júnior. O degrau de "
                   "júnior para pleno quase dobra o salário e é o único salto "
                   "que a empresa consegue provocar em menos de dois anos.",
        "indicador": "Salário médio por senioridade",
        "valor_indicador": "júnior R$ 4.048, pleno R$ 7.898 (+95,1%), sênior R$ 14.117",
        "base": "9.824 com senioridade declarada",
        "onde_ver": "Perfis e remuneração",
    },
    {
        "ordem": 4,
        "decisao": "Tratar o gargalo de IA como falta de gente, não de ferramenta",
        "por_que": "Nenhuma das barreiras que os gestores citam é de "
                   "tecnologia. As duas primeiras são expertise e não saber "
                   "onde aplicar.",
        "indicador": "Barreiras à adoção de IA, na visão do gestor",
        "valor_indicador": "40,3% falta de expertise, 39,5% falta de caso de uso",
        "base": "2.090 gestores que marcaram ao menos uma barreira",
        "onde_ver": "Adoção de IA",
    },
    {
        "ordem": 5,
        "decisao": "Recompor a base da pirâmide agora, não quando faltar sênior",
        "por_que": "A fatia de júnior encolheu sete pontos em três edições. "
                   "Quem não forma hoje disputa sênior no mercado daqui a "
                   "dois anos, no preço de sênior.",
        "indicador": "Participação de júnior por edição",
        "valor_indicador": "29,7% em 2023-24, 23,0% em 2024-25, 22,3% em 2025-26",
        "base": "9.143 nos três níveis comparáveis entre as edições",
        "onde_ver": "Oportunidades e desafios",
    },
    {
        "ordem": 6,
        "decisao": "Cobrar o próximo degrau da fundação de dados, que já está paga",
        "por_que": "Data lake deixou de ser diferencial: oito em cada dez "
                   "empresas já têm. O que separa as empresas agora é o que "
                   "foi construído em cima dele.",
        "indicador": "Empresas com data lake",
        "valor_indicador": "82,4%",
        "base": "2.396 que responderam o bloco de maturidade",
        "onde_ver": "Oportunidades e desafios",
    },
]

CAMPOS = ["ordem", "decisao", "por_que", "indicador", "valor_indicador",
          "base", "onde_ver"]


def como_tabela():
    """Lista pronta para virar DataFrame, com os campos na ordem do esquema."""
    return [{c: r[c] for c in CAMPOS} for r in RECOMENDACOES]

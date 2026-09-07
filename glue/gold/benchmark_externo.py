"""
Referências externas de mercado, para contextualizar os números da pesquisa.

Cada linha aqui foi conferida na fonte primária em 30/08/2026: número exato,
ano de referência, metodologia e recorte da população. O que não deu para
confirmar está declarado em `ressalva`, e não escondido.

POR QUE ISSO EXISTE

A State of Data descreve **quem respondeu a State of Data**: profissionais de
dados engajados o bastante para responder uma pesquisa da comunidade. É uma
amostra excelente para o perfil do profissional e traiçoeira para falar do
"mercado brasileiro" em geral.

O benchmark externo serve para três coisas, e é importante não confundi-las:

  1. VALIDAR    o nosso número bate com fonte independente?
  2. DELIMITAR  até onde a nossa conclusão vale?
  3. COMPLEMENTAR o que a nossa base não mede?

⚠️ REGRA DE USO

Nenhum valor daqui entra no mesmo eixo de um número nosso sem rótulo dizendo
que é de outra pesquisa. Metodologias diferentes produzem números diferentes
para a mesma pergunta, e comparar sem ressalva é o mesmo erro de denominador
que a Silver passou a semana corrigindo.
"""

# Cada referência: o que mede, o valor, quem publicou, quando, sobre quem, e
# como se relaciona com o nosso número.
BENCHMARKS = [
    # ---------------------------------------------------------------- IA
    {
        "indicador": "IA entre as 5 prioridades estratégicas",
        "valor": 67.0,
        "unidade": "%",
        "fonte": "Bain & Company",
        "ano_referencia": 2025,
        "publicado_em": "2025-05",
        "populacao": "organizações no Brasil",
        "amostra": None,
        "url": "https://www.bain.com/pt-br/about/media-center/press-releases/"
               "south-america/2023/67-das-empresas-brasileiras-consideram-a-"
               "inteligencia-artificial-como-prioridade-estrategica-para-2025-revela-bain/",
        "uso": "VALIDAR",
        "nosso_indicador": "IA é prioridade alta na empresa (gestores, 2025)",
        "nosso_valor": 60.6,
        "leitura": "Nosso 60,6% e o 67% da Bain medem quase a mesma coisa e "
                   "chegam perto. A Bain é co-autora da State of Data, o que "
                   "torna a convergência ainda mais relevante.",
        "ressalva": "O press release não publica amostra nem perfil do "
                    "respondente. Comparação indicativa, não rigorosa.",
        # curta para caber na dica de ferramenta, que tem 368px
        "ressalva_curta": "Press release sem amostra publicada.",
    },
    {
        "indicador": "Empresas que usam IA",
        "valor": 17.0,
        "unidade": "%",
        "fonte": "Cetic.br / NIC.br, TIC Empresas 2025",
        "ano_referencia": 2025,
        "publicado_em": "2026-06",
        "populacao": "empresas brasileiras com 10 ou mais funcionários",
        "amostra": 4174,
        "url": "https://www.cgi.br/noticia/releases/uso-de-inteligencia-artificial-"
               "por-empresas-brasileiras-avanca-e-atinge-17-aponta-pesquisa-do-cetic-br/",
        "uso": "DELIMITAR",
        "nosso_indicador": "IA é prioridade alta na empresa (gestores, 2025)",
        "nosso_valor": 60.6,
        "leitura": "A distância (17% x 60,6%) NÃO é contradição, é recorte. "
                   "A nossa base descreve empresas que empregam profissionais "
                   "de dados; a do Cetic descreve o parque empresarial do país.",
        "ressalva": "Metodologia por telefone, fev/2025 a jan/2026. Mede USO "
                    "de IA, enquanto o nosso mede PRIORIDADE estratégica.",
        # curta para caber na dica de ferramenta, que tem 368px
        "ressalva_curta": "Mede uso de IA, não prioridade.",
    },
    {
        "indicador": "Grandes empresas (250+) que usam IA",
        "valor": 50.0,
        "unidade": "%",
        "fonte": "Cetic.br / NIC.br, TIC Empresas 2025",
        "ano_referencia": 2025,
        "publicado_em": "2026-06",
        "populacao": "empresas brasileiras com 250 ou mais funcionários",
        "amostra": 4174,
        "url": "https://www.cgi.br/noticia/releases/uso-de-inteligencia-artificial-"
               "por-empresas-brasileiras-avanca-e-atinge-17-aponta-pesquisa-do-cetic-br/",
        "uso": "VALIDAR",
        "nosso_indicador": "IA é prioridade alta na empresa (gestores, 2025)",
        "nosso_valor": 60.6,
        "leitura": "Este é o recorte que interessa ao cliente do case, uma "
                   "instituição de grande porte. 50% nas grandes contra 17% "
                   "no geral, e 60,6% na nossa base: a progressão explica o "
                   "viés e aproxima os números.",
        "ressalva": "Subiu de 38% (2024) para 50% (2025), crescimento de 12 "
                    "pontos em um ano.",
        # curta para caber na dica de ferramenta, que tem 368px
        "ressalva_curta": "Subiu 12 pontos em um ano.",
    },
    {
        "indicador": "Empresas com ROI comprovado em IA generativa",
        "valor": 40.7,
        "unidade": "%",
        "fonte": "TEC.Institute, Peers Consulting e MIT Technology Review Brasil",
        "ano_referencia": 2026,
        "publicado_em": "2026-08",
        "populacao": "empresas brasileiras que investiram em IA generativa",
        "amostra": None,
        "url": "https://www.cnnbrasil.com.br/economia/money/tecnologia/"
               "ia-generativa-ainda-nao-gera-retorno-para-maioria-das-empresas-diz-estudo/",
        "uso": "COMPLEMENTAR",
        "nosso_indicador": None,
        "nosso_valor": None,
        "leitura": "A nossa base mede adoção e prioridade, não retorno. "
                   "Este número fecha a lacuna: priorizar não é o mesmo que "
                   "colher resultado.",
        "ressalva": "Amostra não divulgada na cobertura consultada.",
        # curta para caber na dica de ferramenta, que tem 368px
        "ressalva_curta": "Amostra não divulgada.",
    },
    {
        "indicador": "Bancos que superaram o business case de IA generativa",
        "valor": 72.7,
        "unidade": "%",
        "fonte": "TEC.Institute, Peers Consulting e MIT Technology Review Brasil",
        "ano_referencia": 2026,
        "publicado_em": "2026-08",
        "populacao": "bancos brasileiros com iniciativas de IA generativa",
        "amostra": None,
        "url": "https://www.cnnbrasil.com.br/economia/money/tecnologia/"
               "ia-generativa-ainda-nao-gera-retorno-para-maioria-das-empresas-diz-estudo/",
        "uso": "COMPLEMENTAR",
        "nosso_indicador": None,
        "nosso_valor": None,
        "leitura": "Diretamente aplicável ao cliente do case. Bancos vão muito "
                   "melhor que a média (72,7% contra 40,7%), o que sustenta a "
                   "recomendação de investir.",
        "ressalva": "O mesmo estudo aponta governança de dados como principal "
                    "obstáculo citado por bancos.",
        # curta para caber na dica de ferramenta, que tem 368px
        "ressalva_curta": "Governança é o principal obstáculo.",
    },
    # ------------------------------------------------------------ TALENTO
    {
        "indicador": "Déficit de formação em TI (demanda x oferta)",
        "valor": 30.2,
        "unidade": "%",
        "fonte": "Brasscom (via O Globo)",
        "ano_referencia": 2025,
        "publicado_em": "2025-04",
        "populacao": "mercado de TI brasileiro, acumulado de 5 anos",
        "amostra": None,
        "url": "https://www.abruc.org.br/deficit-de-profissionais-de-tecnologia-"
               "reduz-mas-setor-enfrenta-pejotizacao-e-fuga-das-universidades/",
        "uso": "COMPLEMENTAR",
        "nosso_indicador": "Júnior na pirâmide de senioridade (2025)",
        # 20,7% sobre as 2.500 pessoas que declararam senioridade em 2025.
        # O 22,3% anterior vinha de outra base e não fechava com o dashboard.
        "nosso_valor": 20.7,
        "leitura": "O mercado demandou 665 mil profissionais em 5 anos e a "
                   "formação entregou 465 mil. Explica de fora o que a nossa "
                   "pirâmide mostra por dentro: o júnior caiu de 27,1% para "
                   "20,7% porque não está sendo formado.",
        "ressalva": "Fonte secundária: notícia citando relatório da Brasscom, "
                    "sem título nem data exata do estudo original.",
        # curta para caber na dica de ferramenta, que tem 368px
        "ressalva_curta": "Fonte secundária, sem o estudo original.",
    },
    # ----------------------------------------------------------- SALÁRIO
    {
        "indicador": "Salário médio, Engenheiro de Dados",
        "valor": 14430.84,
        "unidade": "R$/mês",
        "fonte": "CAGED / MTE (via salario.com.br)",
        "ano_referencia": 2026,
        "publicado_em": "2026-07",
        "populacao": "contratos CLT formais no Brasil, jul/2025 a jun/2026",
        "amostra": 6409,
        "url": "https://www.salario.com.br/profissao/engenheiro-de-dados-cbo-212205/",
        "uso": "VALIDAR",
        "nosso_indicador": "Salário estimado, Engenheiro de Dados (2025)",
        "nosso_valor": 14083.0,
        "leitura": "Diferença de 2,4% contra registro administrativo oficial. "
                   "É a melhor prova de que o ponto médio de faixa, que a "
                   "Silver usa para estimar salário, produz número confiável.",
        "ressalva": "CAGED cobre só CLT e salário base, sem bônus nem PJ. A "
                    "nossa base inclui PJ, que costuma ter bruto maior.",
        # curta para caber na dica de ferramenta, que tem 368px
        "ressalva_curta": "CAGED: só CLT, sem bônus nem PJ.",
    },
    {
        "indicador": "Salário médio, Cientista de Dados",
        "valor": 11019.71,
        "unidade": "R$/mês",
        "fonte": "CAGED / MTE (via salario.com.br)",
        "ano_referencia": 2026,
        "publicado_em": "2026-07",
        "populacao": "contratos CLT formais no Brasil, jul/2025 a jun/2026",
        "amostra": 1683,
        "url": "https://www.salario.com.br/profissao/cientista-de-dados-data-scientist/",
        "uso": "VALIDAR",
        "nosso_indicador": "Salário estimado, Cientista de Dados (2025)",
        "nosso_valor": 12854.0,
        "leitura": "Nosso número fica 16,6% acima. A diferença é coerente com "
                   "auto-seleção da amostra (quem responde pesquisa da "
                   "comunidade tende a estar melhor posicionado) e com a "
                   "presença de PJ na nossa base.",
        "ressalva": "Mesma limitação do anterior: CLT e salário base apenas.",
        # curta para caber na dica de ferramenta, que tem 368px
        "ressalva_curta": "CAGED: só CLT, sem bônus nem PJ.",
    },
]


def _formatar(valor, unidade):
    """Número no padrão brasileiro, com a unidade da própria referência."""
    if valor is None:
        return "sem par direto"
    if unidade == "%":
        return f"{valor:.1f}".replace(".", ",") + "%"
    inteiro = f"{valor:,.0f}".replace(",", ".")
    return f"R$ {inteiro}" if unidade and unidade.startswith("R$") else inteiro


# Por que a linha não tem diferença, dito na própria célula. A coluna Uso da
# tabela mostra o rótulo, e aqui vai o motivo em uma linha.
SEM_DIFERENCA = {
    "DELIMITAR": "não compara: outro recorte",
    "COMPLEMENTAR": "não compara: outra medida",
}


def _diferenca(relativa, nosso, externo, unidade, uso):
    """
    Texto da coluna Diferença.

    Percentual sai nas duas leituras, "+10,6 p.p. (+21,2%)". Dinheiro sai só na
    relativa: ninguém lê salário em pontos percentuais.
    """
    if relativa is None:
        return SEM_DIFERENCA.get(uso, "sem par direto")
    rel = f"{relativa:+.1f}%".replace(".", ",")
    if unidade == "%":
        pontos = f"{nosso - externo:+.1f}".replace(".", ",")
        return f"{pontos} p.p. ({rel})"
    return rel


def como_tabela():
    """Devolve a lista pronta para virar DataFrame, com os campos ordenados."""
    campos = ["indicador", "valor", "unidade", "fonte", "ano_referencia",
              "publicado_em", "populacao", "amostra", "uso", "nosso_indicador",
              "nosso_valor", "leitura", "ressalva", "ressalva_curta", "url"]
    linhas = []
    for b in BENCHMARKS:
        linha = {c: b.get(c) for c in campos}
        # Célula vazia numa tabela de fontes lê como descuido. Quando a fonte
        # não publicou a amostra, o texto diz isso.
        linha["amostra_texto"] = (f'{b["amostra"]:,}'.replace(",", ".")
                                  if b.get("amostra") else "não divulgada")
        linha["nosso_indicador"] = b.get("nosso_indicador") or "não se aplica"
        linha["comparacao"] = _formatar(b.get("nosso_valor"), b.get("unidade"))
        linha["valor_texto"] = _formatar(b.get("valor"), b.get("unidade"))
        nosso, externo = b.get("nosso_valor"), b.get("valor")
        # Diferença relativa só faz sentido quando os dois medem a mesma coisa
        # na mesma unidade. Em "DELIMITAR" e "COMPLEMENTAR" ela seria enganosa.
        linha["diferenca_pct"] = (
            round(100 * (nosso / externo - 1), 1)
            if b.get("uso") == "VALIDAR" and nosso and externo else None
        )
        # ⚠️ PERCENTUAL PRECISA DAS DUAS LEITURAS.
        # 60,6% contra 50,0% é +21,2% em termos relativos e +10,6 pontos em
        # termos absolutos. As duas estão certas, e quem lê "60,6 x 50,0"
        # calcula de cabeça a segunda. Mostrar só a relativa faz o número
        # parecer errado. Em reais a relativa basta, ninguém lê salário em
        # pontos percentuais.
        linha["diferenca_texto"] = _diferenca(
            linha["diferenca_pct"], nosso, externo, b.get("unidade"), b.get("uso"))
        linhas.append(linha)
    return linhas

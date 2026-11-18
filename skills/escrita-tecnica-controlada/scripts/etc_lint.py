#!/usr/bin/env python3
"""Linter da skill escrita-tecnica-controlada (pt-BR e en).

Confere estrutura, não sentido. Só usa a biblioteca padrão.

Uso:
    python etc_lint.py [--lang pt|en|auto] [--nivel estrito|descritivo|leve]
                       [--linhas INICIO-FIM] [--json] [--ler-citacoes]
                       [--desativar regra,regra] [--baseline N] [arquivo ...]
    python etc_lint.py --selftest

Sem arquivo, lê UTF-8 da entrada padrão.
Saída: 0 = sem achado obrigatório acima do baseline, 1 = com achado,
2 = argumento inválido, arquivo ilegível, faixa fora do arquivo ou idioma não reconhecido.

Achado obrigatório: o linter decide sem interpretar o texto.
Achado consultivo: depende do sentido; nunca falha a execução.
"""
from __future__ import annotations

import argparse
import bisect
import json
import re
import sys

LIMITES = {
    "pt": {"estrito": 25, "descritivo": 30, "leve": 35},
    "en": {"estrito": 20, "descritivo": 25, "leve": 30},
}
MAX_FRASES_PARAGRAFO = 6
# Unidades depois de um decimal com ponto (pt-BR pede vírgula).
UNIDADES_DECIMAIS = r"(GB|MB|KB|TB|ms|s|min|h|kg|km|m|%)"
# Unidades que não podem vir coladas no número. "h" fica de fora: "14h30" e "14h" são hora válida em pt-BR.
UNIDADES_COLADAS = r"(GB|MB|KB|TB|ms|min|kg|km|s)"
ANTES_DE_NUMERO = r"(?<![\w./:,])"

NOMES_PT = (r"(validaç(ão|ões)|verificaç(ão|ões)|análises?|envios?|instalaç(ão|ões)|configuraç(ão|ões)|"
            r"atualizaç(ão|ões)|testes?|backups?|pagamentos?|cadastros?|consultas?|alteraç(ão|ões)|exclus(ão|ões)|"
            r"criaç(ão|ões)|leituras?|cópias?|migraç(ão|ões)|monitoramento|processamento|implantaç(ão|ões))")
NOMES_EN = (r"(validation|verification|analysis|installation|configuration|update|test|backup|removal|migration|"
            r"check|review|deletion|creation)")

# Cada regra: (nome, padrão, mensagem). Se o padrão tem o grupo nomeado "alvo", o achado aponta para ele.
SENSIVEIS = {"plural-apostrofo"}          # regras que diferenciam maiúsculas
SO_EM_ESTRITO = {"verbo-suporte", "support-verb"}   # obrigatórias só no nível estrito (matriz, seção 12)
RELAXAM_EM_LEVE = {"palavra-longa", "enchimento", "giria", "burocrates", "long-word", "filler"}

PT_OBRIGATORIAS = [
    ("verbo-suporte",
     r"\b(realiz\w+|efetu\w+|proced\w+ (a|à|ao))\s+((a|o|uma|um|as|os)\s+)?" + NOMES_PT + r"\b",
     "use o verbo pleno (ex.: 'validar' em vez de 'realizar a validação')"),
    ("verbo-suporte",
     r"\b(faz\w* uso d[eoa]|d(ar|á|ê|eu) início (a|à|ao)|lev\w+ em consideração|ter conhecimento de|"
     r"t[eê]m? como objetivo)\b",
     "use o verbo pleno (usar, iniciar, considerar, saber, servir para)"),
    ("palavra-longa", r"\butiliz(ar|a|e|ou|am|ando|ado|ada|ação)\b", "use 'usar'"),
    ("burocrates",
     r"\b(vimos por meio desta|venho por meio deste|segue(m)? (em )?anexo|conforme (alinhado|conversado|combinado)|"
     r"para (conhecimento|ciência)\b|no que tange|no tocante a|no âmbito d[eoa]|tendo em vista|haja vista|"
     r"a partir do momento em que|de (forma|modo) a\b|no sentido de|sendo que|devido ao fato de)",
     "troque pela forma curta (ver ptbr-lexicon.md, seção 2)"),
    ("giria",
     r"\b(startar|starta|setar|seta(do|da)|deployar|deployou|deploya|resetar|resetou|deletar|deletou|checar|checou|"
     r"bugad[oa]|zoad[oa]|gambiarra|"
     r"(derrub(ar|ou|e)|subir|subiu|suba) (o|a) (serviço|aplicação|servidor|ambiente|container|pod|banco|api)|"
     r"(serviço|servidor|sistema|aplicação|banco|api) (caiu|cai|caindo|quebrou|travou|estourou))\b",
     "troque a gíria pelo verbo exato (ver ptbr-lexicon.md, seção 3)"),
    ("ruido-chatbot",
     r"(^|[.!?]\s+)(?P<alvo>claro!|com certeza!|perfeito!|ótima pergunta|excelente (pergunta|observação)|vamos lá\b|"
     r"vamos (explorar|entender|mergulhar)|espero (ter ajudado|que (isso|isto) ajude)|fique à vontade para|"
     r"qualquer dúvida,? estou à disposição|neste (documento|relatório|texto),? (vamos|iremos|vou)|a seguir,? veremos)",
     "corte o artefato de chatbot"),
    ("enchimento",
     r"\b(vale (ressaltar|destacar|lembrar|notar|mencionar)|cabe (ressaltar|destacar|mencionar)|"
     r"é importante (notar|destacar|ressaltar|mencionar|frisar)|em suma\b|em síntese\b|outrossim|"
     r"nos dias de hoje|no cenário atual|em um mundo cada vez mais|quando se trata de|sem (sombra de )?dúvida)",
     "corte a expressão e diga o fato"),
    ("e-ou", r"\be/ou\b", "escolha 'e' ou 'ou'; se inclusivo: 'A, B ou os dois'"),
    ("data-ambigua", r"\b\d{1,2}/\d{1,2}/\d{2,4}\b", "use data ISO 8601 (AAAA-MM-DD)"),
    ("plural-apostrofo", r"\b[A-Z]{2,}'s\b", "plural de sigla sem apóstrofo (APIs)"),
    # "1.000 GB" é milhar em pt-BR e passa: o ponto seguido de exatamente três dígitos não é acusado.
    ("decimal-ponto", ANTES_DE_NUMERO + r"\d+\.(?!\d{3}(?!\d))\d+ ?" + UNIDADES_DECIMAIS + r"(?!\w)",
     "em pt-BR o decimal usa vírgula (1,5 GB); valor de código fica em crase"),
    ("numero-unidade", ANTES_DE_NUMERO + r"\d+(,\d+)?" + UNIDADES_COLADAS + r"(?!\w)",
     "ponha um espaço entre o número e a unidade (300 ms)"),
]

PT_CONSULTIVAS = [
    ("gerundismo", r"\b(vou|vai|vamos|vão|irá|iremos|irão) estar \w+ndo\b",
     "use o futuro simples, salvo se a forma marca ação em andamento em um momento"),
    ("inflacao",
     r"\b(robust[oa]s?|de ponta|de última geração|estado da arte|revolucionári[oa]s?|divisor de águas|"
     r"alavanc\w+|potencializ\w+|crucia(l|is)|primordia(l|is)|sem atrito|inovador(a|es|as)?|"
     r"altamente (escalável|performático|eficiente))\b",
     "adjetivo de avaliação: diga o critério medido, salvo se for termo técnico do domínio"),
    ("atribuicao-vaga", r"\b(estudos (mostram|indicam|apontam)|especialistas (apontam|afirmam)|é sabido que)\b",
     "atribuição: confira se a fonte está nomeada"),
    ("voz-passiva", r"\b(foi|foram|é|são|será|serão|era|eram|sendo|sido)\s+\w+(ad|id)[oa]s?\b",
     "voz passiva: nomeie quem faz, se a fonte informa o ator"),
    ("se-apassivador", r"\b\w+(a|e|am|em|ou|ará|erá)-se\b", "'-se' pode esconder o ator: confira"),
    ("gerundio-conector", r",\s+\w+(ando|endo|indo)\b", "gerúndio ligando orações: diga a relação, se a fonte confirma"),
    ("o-mesmo", r"\b(d?[oa]s? mesm[oa]s?)\s+(é|foi|deve|pode|está|será|não|para|em|com|[,.])", "repita o substantivo"),
    ("conector-ambiguo", r"\b(uma vez que|desde que|na medida em que|à medida que)\b",
     "conector com duas leituras: use porque / quando / se"),
    ("modal-deve", r"\bdeve(m|rá|rão|ria|riam)?\s+(ser|estar|ter|terminar|funcionar|ocorrer|levar|demorar)\b",
     "'deve': obrigação ou estimativa? confirme com a fonte"),
    ("quantificador-vago", r"\b(vári[oa]s|algu(ns|mas)|muit[oa]s|divers[oa]s|a maioria|em breve|recentemente|"
     r"bem mais|muito mais|significativamente)\b", "acrescente o número ou a data, ou o marcador [a confirmar: …]"),
    ("cadeia-de", r"\b\w+ d[eoa]s? \w+ d[eoa]s? \w+ d[eoa]s? \w+", "cadeia de 'de': confira o limite do nível"),
    ("falso-amigo", r"\b(assum(ir|e|imos|indo) que|endereçar (o|a|os|as) (problema|questão|ponto)|"
     r"suporta (o formato|arquivos|requisições))\b",
     "possível falso amigo do inglês (ver ptbr-lexicon.md, seção 5)"),
]

EN_OBRIGATORIAS = [
    ("support-verb",
     r"\b(perform|performs|performed|carry out|carries out|carried out|conduct|conducts|conducted)\s+"
     r"((a|an|the)\s+)?" + NOMES_EN + r"\b", "use the verb (validate, analyze, remove)"),
    ("long-word", r"\b(utiliz(e|es|ed|ing)|leverag(e|es|ed|ing)|in order to|due to the fact that|prior to|"
     r"in the event that|at this point in time)\b", "use the short form (use, to, because, before, if, now)"),
    ("chatbot-noise",
     r"(^|[.!?]\s+)(?P<alvo>great question|certainly!|absolutely!|sure!|i hope this helps|feel free to|let's dive in|"
     r"let me know if|in this (document|report),? (we|i) will)", "delete the chatbot artifact"),
    ("filler", r"\b(it is worth noting that|it's worth noting|it is important to note that|please note that|"
     r"in today's (world|landscape)|needless to say|at the end of the day)\b", "delete the phrase and give the fact"),
    ("and-or", r"\band/or\b", "write 'and', 'or', or 'A, B, or both'"),
    ("ambiguous-date", r"\b\d{1,2}/\d{1,2}/\d{2,4}\b", "use an ISO 8601 date (YYYY-MM-DD)"),
    ("number-unit", ANTES_DE_NUMERO + r"\d+(\.\d+)?" + UNIDADES_COLADAS + r"(?!\w)",
     "put a space between the number and the unit (300 ms)"),
]

EN_CONSULTIVAS = [
    ("inflation", r"\b(robust|seamless(ly)?|cutting-edge|state-of-the-art|world-class|game-chang(er|ing)|"
     r"revolutionary|powerful|delve|tapestry|crucial)\b",
     "evaluation word: give the measured property, unless it is a technical term of the domain"),
    ("vague-attribution", r"\b(studies show|experts say|research shows)\b", "attribution: check that the source is named"),
    ("passive-voice", r"\b(is|are|was|were|be|been|being)\s+\w+(ed|en)\b",
     "passive voice: name the actor if the source gives it"),
    ("modal-should", r"\bshould\b", "'should': recommendation, estimate, or obligation? confirm with the source"),
    ("vague-quantifier",
     r"\b(several|various|a number of|many|some|soon|recently|significantly|much (faster|slower))\b",
     "add the number or the date, or the marker [to confirm: …]"),
    ("compound-tense", r"\b(has|have|had) been \w+", "use a simple tense if the meaning is the same"),
]

REGRAS = {"pt": (PT_OBRIGATORIAS, PT_CONSULTIVAS), "en": (EN_OBRIGATORIAS, EN_CONSULTIVAS)}
NOMES_DE_REGRA = {r[0] for grupo in (PT_OBRIGATORIAS, PT_CONSULTIVAS, EN_OBRIGATORIAS, EN_CONSULTIVAS) for r in grupo} | {
    "ponto-e-virgula", "semicolon", "frase-longa", "long-sentence", "paragrafo-longo", "long-paragraph"}

RE_PALAVRA = re.compile(r"[A-Za-zÀ-ÿ0-9_]+(?:[-'][A-Za-zÀ-ÿ0-9_]+)*")
RE_LIMITE_FRASE = re.compile(r"[.!?]+[\"”')\]]*\s+")
ABREVIATURAS = {"ex", "p", "pág", "sr", "sra", "dr", "dra", "n", "nº", "art", "cap", "fig", "vs", "cf", "obs", "tel",
                "e.g", "i.e", "mr", "mrs", "approx"}
RE_CERCA = re.compile(r"^\s{0,3}(`{3,}|~{3,})(.*)$")
RE_DIRETIVA = re.compile(r"^<!--\s*etc-lint:\s*(off|on)\s*-->$")
RE_UNIDADE = re.compile(r"^(#{1,6}\s|[-*+]\s|\d+[.)]\s|\|)")
RE_CITACAO_BLOCO = re.compile(r"^(>\s?)+")
RE_ITEM = re.compile(r"^\s*([-*+]|\d+[.)])\s")
PT_MARCAS = re.compile(r"\b(não|que|para|com|uma|são|está|você|como|mais|pelo|pela|então|também|os|as|do|da|em)\b", re.I)
EN_MARCAS = re.compile(r"\b(the|and|that|with|this|from|have|which|when|then|does|not|are|was|is|of|to|in)\b", re.I)


class IdiomaIndefinido(ValueError):
    pass


def limpar(texto: str) -> tuple[list[tuple[int, str]], int, bool, int]:
    """Devolve as linhas de prosa (número, texto), o total de linhas suprimidas por diretiva,
    se uma diretiva 'off' ficou sem 'on' e o total de linhas do arquivo.
    Cada bloco removido deixa uma linha vazia, para não unir a prosa de antes com a de depois."""
    linhas = texto.splitlines()
    inicio = 0
    if linhas and linhas[0].strip() == "---":
        for i in range(1, len(linhas)):
            if linhas[i].strip() == "---":
                inicio = i + 1  # front matter só existe com fechamento
                break

    saida: list[tuple[int, str]] = []
    cerca: tuple[str, int] | None = None
    indentado = False
    anterior_vazia = True
    pilha_listas: list[int] = []  # coluna do conteúdo de cada item de lista aberto, do externo ao interno
    desligado = False
    suprimidas = 0
    for n in range(inicio + 1, len(linhas) + 1):
        linha = linhas[n - 1]
        bruto = linha.strip()
        m = RE_CERCA.match(linha)
        if cerca is None and m:
            cerca = (m.group(1)[0], len(m.group(1)))
            saida.append((n, ""))
            continue
        if cerca is not None:
            if m and m.group(1)[0] == cerca[0] and len(m.group(1)) >= cerca[1] and not m.group(2).strip():
                cerca = None
            continue  # dentro de bloco cercado nada é analisado, nem diretivas
        if not bruto:
            anterior_vazia = True
            saida.append((n, ""))
            continue
        item = re.match(r"^(\s*)([-*+]|\d+[.)])(\s+)", linha)
        recuo = len(linha) - len(linha.lstrip(" \t")) + 3 * linha[:len(linha) - len(linha.lstrip(" \t"))].count("\t")
        # Código indentado: 4 colunas além do contêiner (a margem, ou o conteúdo do item de lista aberto).
        recuada = not item and recuo >= (pilha_listas[-1] if pilha_listas else 0) + 4
        if recuada and (indentado or anterior_vazia):
            indentado = True  # bloco de código indentado: começa depois de linha vazia
            saida.append((n, ""))
            continue
        # A linha é prosa ou item: fecha os itens de lista que ficaram mais à direita que ela.
        while pilha_listas and pilha_listas[-1] > recuo:
            pilha_listas.pop()
        if item:
            pilha_listas.append(len(item.group(0).expandtabs(4)))
        indentado = False
        anterior_vazia = False
        d = RE_DIRETIVA.match(bruto)
        if d:
            desligado = d.group(1) == "off"
            saida.append((n, ""))
            continue
        if desligado:
            suprimidas += 1
            saida.append((n, ""))
            continue
        linha = re.sub(r"(`+)(?:(?!\1).)+\1", " COD ", linha)
        linha = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", linha)
        linha = re.sub(r"<?https?://[^\s>]+>?", " URL ", linha)
        linha = re.sub(r"\[(a confirmar|to confirm):[^\]]*\]", " MARCADOR ", linha, flags=re.I)
        linha = re.sub(r"<!--.*?-->", " ", linha)
        linha = linha.replace("**", "")
        saida.append((n, linha))
    return saida, suprimidas, desligado, len(linhas)


def detectar_idioma(linhas: list[tuple[int, str]]) -> str:
    texto = " ".join(l for _, l in linhas)
    pt, en = len(PT_MARCAS.findall(texto)), len(EN_MARCAS.findall(texto))
    if pt == en:
        raise IdiomaIndefinido("não reconheci o idioma do texto: informe --lang pt ou --lang en")
    return "pt" if pt > en else "en"


class Unidade:
    """Um parágrafo, item de lista, linha de tabela ou título, com quebras suaves unidas."""

    def __init__(self, tipo: str):
        self.tipo = tipo
        self.texto = ""
        self._inicios: list[int] = []
        self._linhas: list[int] = []

    def juntar(self, n: int, trecho: str) -> None:
        if self.texto:
            self.texto += " "
        self._inicios.append(len(self.texto))
        self._linhas.append(n)
        self.texto += trecho

    def linha_de(self, pos: int) -> int:
        return self._linhas[max(0, bisect.bisect_right(self._inicios, pos) - 1)]


def unidades(linhas: list[tuple[int, str]]):
    atual: Unidade | None = None
    for n, linha in linhas:
        s = RE_CITACAO_BLOCO.sub("", linha.strip()).strip()  # "> texto" segue o parágrafo da citação
        if not s:
            if atual:
                yield atual
                atual = None
            continue
        if RE_UNIDADE.match(s):
            if atual:
                yield atual
            tipo = "tabela" if s.startswith("|") else "titulo" if s.startswith("#") else "item"
            atual = Unidade(tipo)
            atual.juntar(n, re.sub(r"^(#{1,6}|[-*+]|\d+[.)])\s+", "", s))
            if tipo in ("tabela", "titulo"):
                yield atual
                atual = None
            continue
        if atual is None:
            atual = Unidade("paragrafo")
        atual.juntar(n, s)  # quebra suave: continua a mesma frase
    if atual:
        yield atual


def _apagar_citacoes(texto: str) -> str:
    """Troca o conteúdo entre aspas duplas (retas ou curvas) por espaços, mantendo o comprimento.
    Vale dentro de um parágrafo; aspa sem par fica como está."""
    return re.sub(r"\"[^\"]+\"|“[^”]+”", lambda m: m.group(0)[0] + " " * (len(m.group(0)) - 2) + m.group(0)[-1], texto)


def frases(texto: str) -> list[tuple[int, str]]:
    """Divide em frases e devolve (posição inicial, frase). Abreviatura não encerra frase."""
    saida = []
    ini = 0
    for m in RE_LIMITE_FRASE.finditer(texto):
        antes = re.search(r"([\w.º]+)$", texto[ini:m.start()])
        if antes and antes.group(1).lower().rstrip(".") in ABREVIATURAS and not re.search(
                r"\d\s*$", texto[ini:m.start()][:-len(antes.group(1))]):
            continue  # abreviatura; depois de número é unidade ("300 ms.") e encerra a frase
        if m.end() < len(texto) and texto[m.end()].isdigit() and texto[m.start() - 1:m.start()].isdigit():
            continue  # "v1. 2" ou lista numérica no meio da frase
        trecho = texto[ini:m.end()].strip()
        if trecho:
            saida.append((ini + (len(texto[ini:m.end()]) - len(texto[ini:m.end()].lstrip())), trecho))
        ini = m.end()
    resto = texto[ini:].strip()
    if resto:
        saida.append((ini + (len(texto[ini:]) - len(texto[ini:].lstrip())), resto))
    return saida


def analisar(texto: str, lang: str = "auto", nivel: str = "descritivo", desativar: set[str] | None = None,
             ler_citacoes: bool = False, faixa: tuple[int, int] | None = None) -> dict:
    desativar = desativar or set()
    linhas, suprimidas, sem_fecho, total_linhas = limpar(texto)
    if faixa and faixa[0] > total_linhas:
        raise ValueError(f"a faixa {faixa[0]}-{faixa[1]} começa depois do fim do arquivo ({total_linhas} linhas)")

    def na_faixa(n: int) -> bool:
        return not faixa or faixa[0] <= n <= faixa[1]

    if lang == "auto":
        lang = detectar_idioma([(n, l) for n, l in linhas if na_faixa(n)])
    obrig, consult = REGRAS[lang]
    limite = LIMITES[lang][nivel]
    pt = lang == "pt"
    achados = []

    def add(linha, regra, tipo, trecho, msg):
        if regra not in desativar and na_faixa(linha):
            achados.append({"linha": linha, "regra": regra, "tipo": tipo,
                            "trecho": " ".join(trecho.split())[:90], "mensagem": msg})

    # O documento inteiro vira unidades antes do recorte por faixa: uma citação ou um parágrafo
    # que começa fora da faixa continua sendo tratado como um todo.
    for u in unidades(linhas):
        alvo = u.texto if ler_citacoes else _apagar_citacoes(u.texto)
        for m in re.finditer(r";", re.sub(r"&\w+;", lambda e: " " * len(e.group(0)), alvo)):
            add(u.linha_de(m.start()), "ponto-e-virgula" if pt else "semicolon", "obrigatorio",
                alvo[max(0, m.start() - 40):m.start() + 1], "quebre em duas frases" if pt else "split the sentence")
        for grupo, tipo_base in ((obrig, "obrigatorio"), (consult, "consultivo")):
            for regra, padrao, msg in grupo:
                tipo = tipo_base
                if regra in SO_EM_ESTRITO and nivel != "estrito":
                    tipo = "consultivo"
                if regra in RELAXAM_EM_LEVE and nivel == "leve":
                    tipo = "consultivo"
                flags = 0 if regra in SENSIVEIS else re.I
                for m in re.finditer(padrao, alvo, flags=flags):
                    grupo_alvo = "alvo" if "alvo" in m.re.groupindex else 0
                    add(u.linha_de(m.start(grupo_alvo)), regra, tipo, m.group(grupo_alvo), msg)
        if u.tipo in ("paragrafo", "item"):
            lista = frases(alvo)
            for ini, f in lista:
                qtd = len(RE_PALAVRA.findall(f))
                if qtd > limite:
                    add(u.linha_de(ini), "frase-longa" if pt else "long-sentence", "obrigatorio", f,
                        f"{qtd} palavras (limite {limite})" if pt else f"{qtd} words (limit {limite})")
            if u.tipo == "paragrafo" and len(lista) > MAX_FRASES_PARAGRAFO:
                add(u.linha_de(0), "paragrafo-longo" if pt else "long-paragraph", "consultivo", alvo,
                    f"{len(lista)} frases (limite {MAX_FRASES_PARAGRAFO})" if pt
                    else f"{len(lista)} sentences (limit {MAX_FRASES_PARAGRAFO})")

    achados.sort(key=lambda a: (a["linha"], a["tipo"] != "obrigatorio"))
    return {
        "idioma": lang,
        "nivel": nivel,
        "obrigatorios": sum(a["tipo"] == "obrigatorio" for a in achados),
        "consultivos": sum(a["tipo"] == "consultivo" for a in achados),
        "linhas_suprimidas": suprimidas,
        "diretiva_sem_fecho": sem_fecho,
        "achados": achados,
    }


def selftest() -> int:
    C = "```"
    casos = [
        ("pt", "estrito", "Realize a validação dos dados; depois envie.", {"verbo-suporte", "ponto-e-virgula"}),
        # verbo-suporte é obrigatório só em estrito
        ("pt", "descritivo", "O serviço realiza a validação dos dados.", set()),
        ("pt", "descritivo", "Vale ressaltar que a solução usa cache e/ou fila.", {"enchimento", "e-ou"}),
        ("pt", "descritivo", "O deploy ocorreu em 14/03/2026 e as API's falharam.", {"data-ambigua", "plural-apostrofo"}),
        ("pt", "descritivo", "Ótima pergunta! O serviço caiu e precisamos utilizar o backup.",
         {"ruido-chatbot", "giria", "palavra-longa"}),
        ("pt", "descritivo", "O disco tem 1.5 GB livres.", {"decimal-ponto"}),
        ("pt", "descritivo", "A taxa foi de 1.5 % e o volume de 1.2345 GB.", {"decimal-ponto"}),
        # ponto de milhar é válido em pt-BR
        ("pt", "descritivo", "O volume é de 1.000 GB e a fila tem 10.000 mensagens.", set()),
        ("pt", "descritivo", "O tempo limite é de 300ms.", {"numero-unidade"}),
        ("pt", "descritivo", "Espere 5s. O desvio foi de -300ms.", {"numero-unidade"}),
        ("pt", "descritivo", "Execute o script para gerar o relatório. O serviço valida o token em `1.5 s`.", set()),
        ("pt", "descritivo", "Execute a migração às 14h30 e aguarde 300 ms. A versão 4.18.0 fica bloqueada às 14h.", set()),
        ("pt", "descritivo", f"{C}\nrealizar a validação; 14/03/2026\n{C}\nO job terminou.", set()),
        ("pt", "descritivo", "Vale\nressaltar que o cache funciona.", {"enchimento"}),
        ("pt", "descritivo", f"{C}text\n<!-- etc-lint: off -->\n{C}\nPrecisamos utilizar e/ou trocar.",
         {"palavra-longa", "e-ou"}),
        # diretiva dentro de código indentado não desliga o linter
        ("pt", "descritivo", "Exemplo:\n\n    <!-- etc-lint: off -->\n\nPrecisamos utilizar e/ou trocar.",
         {"palavra-longa", "e-ou"}),
        ("pt", "descritivo", "Exemplo:\n\n\tutilizar e/ou\n\nO job terminou.", set()),
        ("pt", "descritivo", "etc-lint: off\n\nPrecisamos utilizar o cache.", {"palavra-longa"}),
        ("pt", "descritivo", "---\nPrecisamos utilizar e/ou trocar.", {"palavra-longa", "e-ou"}),
        ("pt", "descritivo", f"````\n{C}\nutilizar e/ou\n{C}\n````\nO job terminou.", set()),
        # palavras que só são erro em um dos sentidos ficam fora das regras obrigatórias
        ("pt", "estrito", "O estimador robusto reduz a influência dos valores extremos.", set()),
        ("pt", "estrito", "O comitê promoveu a independência do time.", set()),
        ("pt", "estrito", "A colisão pode derrubar a antena.", set()),
        ("pt", "estrito", "Estudos mostram a redução (Silva, 2024).", set()),
        # futuro progressivo pode marcar ação em andamento: só aviso
        ("pt", "estrito", "Amanhã, às 14h, o serviço vai estar processando a fila.", set()),
        # citação em bloco com aspas que atravessam linhas continua protegida
        ("pt", "descritivo", 'O manual diz:\n\n> "Utilize o cache\n> e/ou a fila."', set()),
        # parágrafo de continuação de item de lista é prosa
        ("pt", "descritivo", "1. Confira o painel.\n\n    Precisamos utilizar e/ou trocar.", {"palavra-longa", "e-ou"}),
        # código dentro de item de lista continua ignorado
        ("pt", "descritivo", "1. Confira o painel.\n\n        utilizar e/ou\n\nO job terminou.", set()),
        # depois de voltar ao item externo, o código é medido a partir do item externo
        ("pt", "descritivo", "- Etapa externa.\n  - Consulte o painel.\n\n  Continue a etapa externa.\n\n      utilizar e/ou",
         set()),
        ("pt", "descritivo", "- Etapa externa.\n  - Consulte o painel.\n\n    Precisamos utilizar o cache.", {"palavra-longa"}),
        # "ms." depois de número é unidade e encerra a frase
        ("pt", "descritivo", "O gateway responde em 300 ms. " + " ".join(["palavra"] * 25) + ".", set()),
        ("en", "estrito", "We utilize a cache; it is fast.", {"long-word", "semicolon"}),
        ("en", "estrito", "Great question! Perform a validation of the input and/or the output.",
         {"chatbot-noise", "support-verb", "and-or"}),
        ("en", "descritivo", "Validate the token. Send the packet to the server.", set()),
        ("en", "descritivo", "We need to restart the service after 300 ms. Studies show a decrease (Lee, 2024).", set()),
    ]
    falhas = 0
    total = len(casos)
    for lang, nivel, texto, esperado in casos:
        r = analisar(texto, lang, nivel)
        obtido = {a["regra"] for a in r["achados"] if a["tipo"] == "obrigatorio"}
        if obtido != esperado:
            falhas += 1
            print(f"FALHA [{lang}/{nivel}] {texto!r}\n  esperado: {sorted(esperado)}\n  obtido:   {sorted(obtido)}")

    def conferir(nome: str, ok) -> None:
        nonlocal falhas, total
        total += 1
        if not ok:
            falhas += 1
            print(f"FALHA {nome}")

    longa = " ".join(["palavra"] * 31) + "."
    conferir("frase-longa", any(a["regra"] == "frase-longa" for a in analisar(longa, "pt")["achados"]))
    duas = " ".join(["palavra"] * 16) + ". nginx " + " ".join(["palavra"] * 16) + "."
    conferir("frase iniciada em minúscula é separada",
             not any(a["regra"] == "frase-longa" for a in analisar(duas, "pt")["achados"]))
    conferir("abreviatura não encerra frase", len(frases("Veja a pág. 3 do manual. Depois execute.")) == 2)
    conferir("inflação consultiva", any(a["regra"] == "inflacao" and a["tipo"] == "consultivo"
                                         for a in analisar("O estimador robusto.", "pt")["achados"]))
    conferir("detecção pt", analisar("o texto não tem que ser longo", "auto")["idioma"] == "pt")
    conferir("detecção en", analisar("the service is not in the list", "auto")["idioma"] == "en")
    try:
        analisar("Kubernetes", "auto")
        conferir("idioma indefinido", False)
    except IdiomaIndefinido:
        conferir("idioma indefinido", True)
    r = analisar("Linha boa.\n\n<!-- etc-lint: off -->\nutilizar e/ou\n<!-- etc-lint: on -->\n\nOutra linha.", "pt")
    conferir("diretiva em comentário", r["obrigatorios"] == 0 and r["linhas_suprimidas"] == 1)
    r = analisar("Primeira linha.\nSegunda linha com e/ou aqui.", "pt")
    conferir("linha do achado em parágrafo de várias linhas", r["achados"] and r["achados"][0]["linha"] == 2)
    r = analisar("O serviço respondeu.\nClaro! Continue.", "pt")
    conferir("linha do artefato de chatbot", r["achados"] and r["achados"][0]["linha"] == 2)
    r = analisar("Texto em português.\n\nWe utilize it.", "en", faixa=(3, 3))
    conferir("faixa de linhas", r["obrigatorios"] == 1)
    r = analisar('Ele disse "vamos\nutilizar e/ou\ntrocar" ontem.', "pt", faixa=(2, 2))
    conferir("citação que atravessa a faixa", r["obrigatorios"] == 0)
    try:
        analisar("Uma linha.", "pt", faixa=(40, 50))
        conferir("faixa fora do arquivo", False)
    except ValueError:
        conferir("faixa fora do arquivo", True)
    conferir("citação ignorada", analisar('Ele disse "vamos utilizar e/ou trocar" ontem.', "pt")["obrigatorios"] == 0)
    conferir("citação lida com a opção",
             analisar('Ele disse "vamos utilizar e/ou trocar" ontem.', "pt", ler_citacoes=True)["obrigatorios"] == 2)
    conferir("argumento inválido: baseline negativo", main(["--baseline", "-1", "--lang", "pt", __file__]) == 2)
    conferir("argumento inválido: regra desconhecida", main(["--desativar", "nao-existe", __file__]) == 2)
    print(f"selftest: {total - falhas} de {total} casos passam")
    return 1 if falhas else 0


def _faixa(valor: str) -> tuple[int, int]:
    m = re.fullmatch(r"(\d+)-(\d+)", valor)
    if not m or int(m.group(1)) < 1 or int(m.group(1)) > int(m.group(2)):
        raise argparse.ArgumentTypeError("use INICIO-FIM, por exemplo 40-80")
    return int(m.group(1)), int(m.group(2))


def main(argv=None) -> int:
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8")
        except Exception:
            pass
    p = argparse.ArgumentParser(description="Linter de escrita técnica controlada (pt-BR e en).")
    p.add_argument("arquivos", nargs="*")
    p.add_argument("--lang", choices=["pt", "en", "auto"], default="auto")
    p.add_argument("--nivel", "--level", choices=["estrito", "descritivo", "leve"], default="descritivo")
    p.add_argument("--linhas", type=_faixa, metavar="INICIO-FIM", help="relata só os achados dessa faixa de linhas")
    p.add_argument("--json", action="store_true")
    p.add_argument("--desativar", "--disable", default="", help="regras separadas por vírgula")
    p.add_argument("--baseline", type=int, default=0, help="achados obrigatórios tolerados (0 ou mais)")
    p.add_argument("--ler-citacoes", action="store_true", help="analisa também o texto entre aspas duplas")
    p.add_argument("--selftest", action="store_true")
    try:
        args = p.parse_args(argv)
    except SystemExit as e:
        return 2 if e.code else 0
    if args.selftest:
        return selftest()

    if args.baseline < 0:
        print("erro: --baseline aceita 0 ou um número positivo", file=sys.stderr)
        return 2
    desativar = {r.strip() for r in args.desativar.split(",") if r.strip()}
    desconhecidas = sorted(desativar - NOMES_DE_REGRA)
    if desconhecidas:
        print(f"erro: regra desconhecida em --desativar: {', '.join(desconhecidas)}", file=sys.stderr)
        return 2

    entradas = []
    caminho = "<stdin>"
    try:
        if args.arquivos:
            for caminho in args.arquivos:
                with open(caminho, "rb") as f:
                    entradas.append((caminho, f.read().decode("utf-8-sig")))
        else:
            entradas.append((caminho, sys.stdin.buffer.read().decode("utf-8-sig")))
    except UnicodeDecodeError as e:
        print(f"erro: {caminho} não está em UTF-8 (byte inválido na posição {e.start})", file=sys.stderr)
        return 2
    except OSError as e:
        print(f"erro: não consegui ler {caminho}: {e.strerror or e}", file=sys.stderr)
        return 2

    total = 0
    resultados = []
    for nome, texto in entradas:
        try:
            r = analisar(texto, args.lang, args.nivel, desativar, args.ler_citacoes, args.linhas)
        except ValueError as e:  # idioma indefinido ou faixa fora do arquivo
            print(f"erro: {nome}: {e}", file=sys.stderr)
            return 2
        r["arquivo"] = nome
        total += r["obrigatorios"]
        resultados.append(r)

    if args.json:
        print(json.dumps(resultados, ensure_ascii=False, indent=2))
    else:
        for r in resultados:
            for a in r["achados"]:
                marca = "ERRO " if a["tipo"] == "obrigatorio" else "aviso"
                print(f"{r['arquivo']}:{a['linha']}: {marca} [{a['regra']}] {a['mensagem']} — \"{a['trecho']}\"")
            if r["diretiva_sem_fecho"]:
                print(f"{r['arquivo']}: aviso: '<!-- etc-lint: off -->' sem '<!-- etc-lint: on -->'")
            print(f"{r['arquivo']}: idioma={r['idioma']} nível={r['nivel']} obrigatórios={r['obrigatorios']} "
                  f"consultivos={r['consultivos']} linhas suprimidas={r['linhas_suprimidas']}")
    return 1 if total > args.baseline else 0


if __name__ == "__main__":
    sys.exit(main())

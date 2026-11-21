#!/usr/bin/env python3
"""Lint a prompt contract written in English or Brazilian Portuguese.

The linter checks the structure that makes a contract verifiable: required
sections, ordered priorities, runnable gate commands, the isolated-reviewer
clause, the severity scale, the failing-gate rule, and the evidence list.
It also flags leftover template placeholders, role-play, motivational
adjectives, performance adjectives without numbers, semicolons, and very long
sentences. It does not judge whether the content is right.

Usage:
    python scripts/lint_contract.py CONTRACT.md            # language auto-detected
    python scripts/lint_contract.py --lang pt CONTRACT.md  # force pt-BR
    python scripts/lint_contract.py --lang en CONTRACT.md  # force English
    python scripts/lint_contract.py --json CONTRACT.md     # machine-readable output
    python scripts/lint_contract.py --selftest             # lint the bundled examples

Exit codes: 0 = no ERROR, 1 = at least one ERROR, 2 = bad argument or unreadable file.
Uses only the Python standard library (3.8+).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

SECTIONS = {
    # key: (English heading, Portuguese heading, required)
    "priorities": ("PRIORITIES", "PRIORIDADES", True),
    "context": ("CONTEXT", "CONTEXTO", False),
    "constraints": ("CONSTRAINTS", "RESTRICOES", True),
    "target": ("TARGET", "ALVO", False),
    "environment": ("ENVIRONMENT", "AMBIENTE", False),
    "requirements": ("REQUIREMENTS", "REQUISITOS", True),
    "interface": ("INTERFACE", "INTERFACE", False),
    "verification": ("VERIFICATION", "VERIFICACAO", True),
    "failing": ("IF A GATE DOES NOT PASS", "SE UM GATE NAO PASSAR", True),
    "done": ("DONE WHEN", "PRONTO QUANDO", True),
}

# Phrases are matched on accent-free, lower-case prose (code removed).
# Role-play only counts at the start of a sentence or list item, so that
# "the proxy must act as a reverse proxy" is not flagged.
SENTENCE_START = r"(?:^|[.!?:]\s+|^[-*]\s+)"
ROLE_PLAY = {
    "en": [r"\byou are an? (expert|senior|world[- ]class|experienced|seasoned|professional|specialist)\b",
           SENTENCE_START + r"(act as|pretend to be|roleplay as)\b"],
    "pt": [r"\bvoce e um(a)? (especialista|expert|senior|engenheir\w*|desenvolvedor\w*)\b",
           SENTENCE_START + r"(atue como|aja como|finja ser)\b"],
}
HYPE = {
    "en": [r"\bamazing\b", r"\bincredible\b", r"\bstunning\b", r"\bstate[- ]of[- ]the[- ]art\b", r"\bworld[- ]class\b",
           r"\bbest practices\b", r"\bbeautiful code\b", r"\bperfect\b", r"\bawesome\b"],
    "pt": [r"\bincrivel\b", r"\bde ponta\b", r"\bboas praticas\b", r"\bexcelente\b", r"\bperfeit[oa]\b",
           r"\bmaravilhos[oa]\b", r"\bfantastic[oa]\b"],
}
VAGUE_PERF = {
    "en": [r"\bfast\b", r"\bquick(ly)?\b", r"\bperformant\b", r"\bscalable\b", r"\blightweight\b", r"\bresponsive\b", r"\blow latency\b"],
    "pt": [r"\brapid[oa]s?\b", r"\bperformatic[oa]s?\b", r"\bescalave(l|is)\b", r"\bleve(s)?\b", r"\bagil\b", r"\bbaixa latencia\b"],
}
REVIEWER = {
    "en": {"present": r"\b(reviewer|critic)\b", "new": r"\bnew subagent\b|\bfresh subagent\b|\bnew (reviewer|critic)\b",
           "every_round": r"\bevery round\b|\beach round\b", "only": r"\bonly\b",
           "no_other_file": r"\b(read|open) no other file\b|\bno other file\b|\bnothing else\b",
           "no_justification": r"\bintentional\b|\bon purpose\b|\bjustification"},
    "pt": {"present": r"\b(revisor|critico)\b", "new": r"\bsubagente novo\b|\bnovo subagente\b|\b(revisor|critico) novo\b",
           "every_round": r"\ba cada rodada\b|\bcada rodada\b", "only": r"\bsomente\b|\bso\b|\bapenas\b",
           "no_other_file": r"\bnenhum outro arquivo\b|\bmais nada\b",
           "no_justification": r"\bde proposito\b|\bjustificativa"},
}
SEVERITY = {
    "en": [r"\bblocker\b|\bsevere\b|\bcritical\b", r"\bmajor\b|\bmedium\b", r"\bminor\b"],
    "pt": [r"\bbloqueante\b|\bgrave\b|\bcritico\b", r"\bmaior\b|\bmedio\b", r"\bmenor\b"],
}
NOT_VERIFIED = {"en": r"not verified|unverified|was not checked", "pt": r"sem verificar|nao verificad|nao foi verificad"}
NOT_DONE = {"en": r"not done", "pt": r"nao pronto"}
WEAKEN = {"en": r"\bskip\b|do not weaken|don't weaken", "pt": r"\bskip\b|nao enfraqueca"}
TAIL_METRICS = r"\bp9[059]\b|\bmax(imo|imum)?\b|\bpercentil|\bpercentile"
NOT_APPLY = r"does not apply|nao se aplica|not applicable"
OPEN_MARKER = re.compile(r"\[(?:to confirm|a confirmar)\b[^\]]*\]", re.IGNORECASE)
# A template placeholder has no space right after "<" or right before ">", so
# comparisons such as "p95 < 300 ms and max > 1 s" do not match. Autolinks
# (<https://...>), comments, and common HTML tags are not placeholders either.
PLACEHOLDER = re.compile(
    r"<(?!\s)(?!https?:|mailto:|!--)"
    r"(?!/?(?:br|hr|b|i|em|strong|details|summary|sub|sup|kbd|code|pre|p|div|span|img|a)\b)"
    r"[^<>\n]{1,80}(?<!\s)>")
# A gate command is inline code that starts with a known tool, a ./script, or
# environment assignments followed by a tool.
COMMAND = re.compile(
    r"`(?:[A-Za-z_][A-Za-z0-9_]*=\S+\s+)*"
    r"(?:\./\S+|(?:npm|npx|pnpm|yarn|bun|deno|node|python3?|pytest|tox|nox|uv|poetry|pip|make|just|task|go|cargo|"
    r"mvn|mvnw|gradle|gradlew|dotnet|java|bundle|rake|rspec|ruby|php|composer|phpunit|k6|playwright|cypress|newman|"
    r"bash|sh|pwsh|powershell|docker|kubectl|helm|terraform|ruff|eslint|jest|vitest|tsc|turbo|nx|sqlplus|sql|psql|"
    r"mysql|curl|git)\b)[^`\n]*`", re.IGNORECASE)
LONG_SENTENCE_WORDS = 35


def fold(text: str) -> str:
    """Lower-case and strip accents, so 'Restrições' matches 'RESTRICOES'."""
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower()


def strip_code(text: str) -> str:
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"`[^`\n]*`", " ", text)
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    return text


def detect_lang(text: str) -> str:
    f = fold(text)
    pt = sum(f.count(w) for w in ("prioridades", "restricoes", "requisitos", "verificacao", "pronto quando", " nao ", " voce "))
    en = sum(f.count(w) for w in ("priorities", "constraints", "requirements", "verification", "done when", " the ", " not "))
    return "pt" if pt > en else "en"


def strip_accents(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def split_sections(lines: list[str], lang: str) -> dict[str, tuple[int, list[str]]]:
    """Return {key: (line_number, body_lines)}.

    A plain line is a heading only when it starts with the heading in capitals
    ("CONTEXT", "RESTRIÇÕES"), so prose such as "Context matters here" is not a
    heading. A Markdown heading line ("## Context") matches in any case."""
    idx = 1 if lang == "pt" else 0
    heads = {k: fold(v[idx]).upper() for k, v in SECTIONS.items()}
    found: dict[str, tuple[int, list[str]]] = {}
    current = None
    in_code = False
    for n, raw in enumerate(lines, 1):
        if raw.strip().startswith("```"):
            in_code = not in_code
        if not in_code:
            stripped = raw.strip()
            text = strip_accents(stripped.lstrip("#").strip())
            candidate = text.upper() if stripped.startswith("#") else text
            hit = None
            for key, head in heads.items():
                if candidate.startswith(head) and key not in found:
                    rest = candidate[len(head):len(head) + 1]
                    if rest in ("", " ", ":", "(", "."):
                        hit = key
                        break
            if hit:
                current = hit
                found[hit] = (n, [raw])
                continue
        if current:
            found[current][1].append(raw)
    return found


def sentences(text: str) -> list[tuple[int, str]]:
    """Split prose into (line_number, sentence). Contracts are line-oriented:
    each list item or paragraph line is its own unit, and code is ignored."""
    out: list[tuple[int, str]] = []
    in_code = False
    for n, raw in enumerate(text.splitlines(), 1):
        if raw.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code or raw.lstrip().startswith(("|", "<!--")):
            continue
        prose = re.sub(r"`[^`\n]*`", "CODE", raw).strip().lstrip("-*0123456789.) ").strip()
        for s in re.split(r"(?<=[.!?])\s+(?=[A-ZÀ-Ý\"'(<])", prose):
            if s.strip():
                out.append((n, s.strip()))
    return out


def lint(text: str, lang: str = "auto") -> dict:
    if lang == "auto":
        lang = detect_lang(text)
    lines = text.splitlines()
    findings: list[dict] = []

    def add(level: str, rule: str, msg: str, line: int | None = None) -> None:
        findings.append({"level": level, "rule": rule, "line": line, "message": msg})

    sections = split_sections(lines, lang)
    idx = 1 if lang == "pt" else 0
    for key, names in SECTIONS.items():
        if key not in sections:
            level = "ERROR" if names[2] else "WARN"
            add(level, "missing-section", f"section '{names[idx]}' not found"
                + ("" if names[2] else ": keep the heading with a one-line reason when it does not apply"))

    def body(key: str) -> str:
        return "\n".join(sections[key][1]) if key in sections else ""

    def line_of(key: str) -> int | None:
        return sections[key][0] if key in sections else None

    # Goal: text before the first section.
    first = min((v[0] for v in sections.values()), default=len(lines) + 1)
    goal = fold(strip_code("\n".join(lines[: first - 1]))).strip()
    if len(goal.split()) < 8:
        add("ERROR", "goal", "no goal paragraph before the first section", 1)
    elif not re.search(r"only needs|does not need|not needed|is enough|so precisa|nao precisa|basta", goal):
        add("WARN", "goal-scope", "the goal does not say what is enough or what is not needed", 1)

    # Priorities: ordered list with at least 2 items.
    if "priorities" in sections:
        items = [l for l in sections["priorities"][1][1:] if re.match(r"\s*\d+[.)]\s", l)]
        if len(items) < 2:
            add("ERROR", "priorities-order", "priorities need a numbered list with at least 2 items", line_of("priorities"))
        elif len(items) > 6:
            add("WARN", "priorities-count", f"{len(items)} priorities: more than 5 rarely break ties", line_of("priorities"))

    # Constraints: each bullet should carry a reason.
    if "constraints" in sections:
        reason = r"\breason:|\bmotivo:"
        start = sections["constraints"][0]
        for off, l in enumerate(sections["constraints"][1][1:], 1):
            if re.match(r"\s*-\s", l) and not re.search(reason, fold(l)):
                if not re.search(r"do not change|do not add|nao altere|nao adicione", fold(l)):
                    add("WARN", "constraint-reason", "constraint without 'Reason:'/'Motivo:'", start + off)

    # Verification: commands, reviewer isolation, severity scale, tail metrics.
    ver = body("verification")
    ver_f = fold(ver)
    if ver and not COMMAND.search(ver):
        add("ERROR", "gate-command", "VERIFICATION has no runnable command in backticks", line_of("verification"))
    if ver:
        rv = REVIEWER[lang]
        if not re.search(rv["present"], ver_f):
            add("ERROR", "reviewer", "VERIFICATION has no isolated reviewer", line_of("verification"))
        else:
            checks = [("new", "the reviewer is not a new subagent"),
                      ("every_round", "the reviewer is not new every round"),
                      ("only", "the reviewer's inputs are not limited ('only'/'somente')"),
                      ("no_other_file", "the reviewer is not told to read no other file"),
                      ("no_justification", "the builder is not forbidden to send justifications ('intentional'/'de propósito')")]
            for k, msg in checks:
                if not re.search(rv[k], ver_f):
                    add("WARN", f"reviewer-{k.replace('_', '-')}", msg, line_of("verification"))
            missing = [i for i, p in enumerate(SEVERITY[lang]) if not re.search(p, ver_f)]
            if missing:
                add("WARN", "severity-scale", "severity scale is incomplete (needs 3 defined levels)", line_of("verification"))
    tgt = fold(strip_code(body("target")))
    perf_target = re.search(r"\d\s*(ms|s\b|req/s|rps|fps|mb|gb|%)", tgt) and not re.search(NOT_APPLY, tgt)
    if perf_target and ver and not re.search(TAIL_METRICS, ver_f):
        add("WARN", "tail-metrics", "TARGET has numbers but VERIFICATION reports no p95/p99/max", line_of("verification"))

    # Failing-gate rule.
    fail = fold(body("failing"))
    if fail:
        if not re.search(WEAKEN[lang], fail):
            add("WARN", "no-weakening", "the failing-gate rule does not forbid weakening the gate", line_of("failing"))
        if not re.search(r"\d", strip_code(fail)):
            add("WARN", "round-cap", "the failing-gate rule sets no numeric cap on rounds or time", line_of("failing"))
        if not re.search(NOT_DONE[lang], fail):
            add("WARN", "not-done-report", "the failing-gate rule does not ask for a 'not done' report", line_of("failing"))

    # Done when.
    done = fold(body("done"))
    if done and not re.search(NOT_VERIFIED[lang], done):
        add("WARN", "unverified-list", "DONE WHEN does not ask for what was not verified", line_of("done"))

    # Line-level prose checks.
    in_code = False
    for n, raw in enumerate(lines, 1):
        if raw.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code or raw.strip().startswith("<!--"):
            continue
        prose = re.sub(r"`[^`\n]*`", " ", raw)
        for m in PLACEHOLDER.finditer(prose):
            add("ERROR", "placeholder", f"template placeholder left: {m.group(0)}", n)
        for m in PLACEHOLDER.finditer(" ".join(re.findall(r"`([^`\n]*)`", raw))):
            add("WARN", "placeholder-in-code", f"placeholder inside code: {m.group(0)}", n)
        pf = fold(prose)
        for p in ROLE_PLAY[lang]:
            if re.search(p, pf):
                add("ERROR", "role-play", "role-play line: state the task instead", n)
        for p in HYPE[lang]:
            m = re.search(p, pf)
            if m:
                add("WARN", "hype", f"motivational adjective '{m.group(0)}': replace it with a checkable criterion", n)
        for p in VAGUE_PERF[lang]:
            m = re.search(p, pf)
            if m and not re.search(r"\d", prose):
                add("WARN", "vague-performance", f"'{m.group(0)}' without a number: give number, unit, and condition", n)
        if ";" in prose:
            add("WARN", "semicolon", "semicolon: split into two sentences", n)

    for n, s in sentences(text):
        words = len(s.split())
        if words > LONG_SENTENCE_WORDS:
            add("WARN", "long-sentence", f"{words} words: '{s[:60]}...'", n)

    markers = OPEN_MARKER.findall(text)
    for m in markers:
        if not re.search(r"default:|padrao:|blocking|bloqueante", fold(m)):
            add("WARN", "open-item-kind", f"open item without 'Default:'/'Padrão:' or 'BLOCKING'/'BLOQUEANTE': {m[:60]}")
    words = len(strip_code(text).split())
    if words > 1000:
        add("WARN", "length", f"{words} words outside code: aim for 400 to 800 and stay under 1,000 (move the open-item list to the reply)")
    return {
        "lang": lang,
        "words": words,
        "open_items": markers,
        "errors": sum(f["level"] == "ERROR" for f in findings),
        "warnings": sum(f["level"] == "WARN" for f in findings),
        "findings": findings,
    }


def print_report(path: str, result: dict) -> None:
    for f in result["findings"]:
        where = f"{path}:{f['line']}" if f["line"] else path
        print(f"{where}: {f['level']:5} [{f['rule']}] {f['message']}")
    if result["open_items"]:
        print(f"{path}: {len(result['open_items'])} open item(s) to confirm with the user:")
        for m in result["open_items"]:
            print(f"  - {m}")
    print(f"{path}: lang={result['lang']} words={result['words']} errors={result['errors']} warnings={result['warnings']}")


BAD_SAMPLE = """You are an expert engineer. Build an amazing, fast API.

PRIORITIES
- quality

VERIFICATION
Make sure it works.
"""


# Legitimate lines that once produced false ERRORs. The selftest expects 0 errors here.
EDGE_SAMPLE = """Build the export endpoint for the billing screen. It only needs to read.

PRIORITIES (in this order when they conflict)
1. Correct data
2. Small diff

CONTEXT
- Context matters here: the proxy must act as a reverse proxy for the legacy service.

CONSTRAINTS
- Read only. Reason: shared database.

TARGET
- p95 < 300 ms and max > 1 s is not acceptable. Docs at <https://example.com/docs>.

ENVIRONMENT
- Tools: JDK 21. Interface changes go through the API team.

REQUIREMENTS
- Interface changes are not allowed in this task.

INTERFACE
- GET /export

VERIFICATION
- Tests: `./gradlew test`, `./mvnw verify`, and `bundle exec rspec` exit with code 0. Report mean, p95, p99, and max.
- Isolated reviewer: every round, start a new subagent. Give it ONLY the requirements and the evidence. Tell it to read no other file. Send no explanation of what is intentional. Scale: blocker, major, minor.

IF A GATE DOES NOT PASS
- Do not weaken the gate, do not skip tests. At most 5 rounds. Deliver a "not done" report.

DONE WHEN all gates pass. Deliver what was not verified, and why.
"""


def selftest() -> int:
    here = Path(__file__).resolve().parent.parent / "references"
    ok = True
    for name in ("example-api-nestjs-oracle.en.md", "example-api-nestjs-oracle.pt-BR.md"):
        p = here / name
        if not p.exists():
            print(f"selftest: missing {p}")
            ok = False
            continue
        r = lint(p.read_text(encoding="utf-8"))
        expected = "pt" if "pt-BR" in name else "en"
        if r["errors"] or r["lang"] != expected:
            print(f"selftest: {name} expected 0 errors and lang={expected}, got {r['errors']} errors, lang={r['lang']}")
            print_report(name, r)
            ok = False
    r = lint(EDGE_SAMPLE)
    if r["errors"]:
        print("selftest: edge sample should have 0 errors")
        print_report("edge-sample", r)
        ok = False
    r = lint(BAD_SAMPLE)
    rules = {f["rule"] for f in r["findings"]}
    for rule in ("role-play", "priorities-order", "gate-command", "reviewer", "missing-section"):
        if rule not in rules:
            print(f"selftest: bad sample did not trigger '{rule}'")
            ok = False
    print("selftest: OK" if ok else "selftest: FAILED")
    return 0 if ok else 1


def main(argv: list[str]) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")  # Windows consoles default to a legacy code page
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description="Lint a prompt contract (English or pt-BR).")
    ap.add_argument("files", nargs="*", help="contract files (.md)")
    ap.add_argument("--lang", choices=["auto", "en", "pt"], default="auto")
    ap.add_argument("--json", action="store_true", help="print JSON instead of text")
    ap.add_argument("--selftest", action="store_true", help="lint the bundled examples and a bad sample")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.files:
        ap.print_usage(sys.stderr)
        print("error: give at least one contract file, or --selftest", file=sys.stderr)
        return 2
    worst = 0
    results = {}
    for f in args.files:
        try:
            text = Path(f).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            print(f"error: cannot read {f}: {e}", file=sys.stderr)
            return 2
        r = lint(text, args.lang)
        results[f] = r
        if not args.json:
            print_report(f, r)
        if r["errors"]:
            worst = 1
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    return worst


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

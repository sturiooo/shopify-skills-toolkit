#!/usr/bin/env python3
"""Sprawdza, czy repozytorium nie zawiera danych klientów.

Użycie:
    python scripts/check-anonymization.py <czarna-lista.txt> [--repo .] [--no-history]

Czarna lista leży POZA repozytorium (sama zawiera nazwy klientów).
Format: jedna fraza na linię, `#` zaczyna komentarz. Dopasowanie bez rozróżniania
wielkości liter. Spacja, `-`, `_` i `.` w frazie dopasowują się także jako brak
separatora, więc `acme store` złapie `acme-store`, `acme_store` i `acmestore`.

Poza listą skrypt sprawdza wzorce generyczne: adresy *.myshopify.com, gid z
prawdziwym ID, długie liczby (ID motywów, rabatów, produktów), adresy e-mail,
tokeny Shopify, ścieżki prywatnego workspace, linki do pamięci `[[...]]`.

Domyślnie skanuje pliki śledzone przez git ORAZ całą historię (`git log -p --all`).
Kod wyjścia: 0 = brak trafień, 1 = są trafienia, 2 = błąd wywołania.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

# Wzorce generyczne: (nazwa, regex, dozwolone dopasowania)
GENERIC = [
    ("myshopify", r"[A-Za-z0-9<>\-_]+\.myshopify\.com",
     {"example-store.myshopify.com", "shops.myshopify.com", "<sklep>.myshopify.com",
      "*.myshopify.com", "SKLEP.myshopify.com", "X.myshopify.com", "<shop>.myshopify.com"}),
    ("gid z ID", r"gid://shopify/[A-Za-z]+/\d{4,}", set()),
    ("dluga liczba (ID)", r"(?<![\w.#-])#?\d{9,}(?![\w.])", set()),
    ("e-mail", r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+\.[A-Za-z.]{2,}",
     {"noreply@anthropic.com", "git@github.com"}),
    ("token Shopify", r"shp(?:at|ca|ss|ua|pa)_[A-Za-z0-9]{6,}", set()),
    ("client id (32 hex)", r"\b[0-9a-f]{32}\b", set()),
    ("sciezka Windows", r"[A-Za-z]:\\\\?Users", set()),
    ("sciezka domowa", r"/Users/[A-Za-z]", set()),
    ("workspace: _robocze", r"_robocze", set()),
    ("workspace: shopify-projekty", r"shopify-projekty", set()),
    ("workspace: biblioteka", r"_biblioteka-sekcji", set()),
    ("workspace: _snapshoty/_archiwum/_setup", r"_snapshoty|_archiwum|_setup/", set()),
    ("link do pamieci", r"\[\[[^\]]+\]\]", set()),
    ("pamiec: plik", r"\b(?:project|reference|feedback|user)_[a-z0-9_]+\.md\b", set()),
]

SKIP_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".zip"}


def load_blacklist(path: Path):
    terms = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip() if not raw.strip().startswith("#") else ""
        if line:
            terms.append(line)
    patterns = []
    for t in terms:
        parts = [re.escape(p) for p in re.split(r"[\s\-_.]+", t) if p]
        if not parts:
            continue
        rx = r"[\s\-_.]*".join(parts)
        patterns.append((t, re.compile(rx, re.IGNORECASE)))
    return patterns


def scan_text(label, text, blacklist, hits):
    for lineno, line in enumerate(text.splitlines(), 1):
        seen = set()
        for term, rx in blacklist:
            for m in rx.finditer(line):
                if m.span() in seen:
                    continue
                seen.add(m.span())
                hits.append((label, lineno, f"lista: {term}", m.group(0), line.strip()))
        for name, pattern, allowed in GENERIC:
            for m in re.finditer(pattern, line):
                if m.group(0) in allowed:
                    continue
                hits.append((label, lineno, name, m.group(0), line.strip()))


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                          text=True, encoding="utf-8", errors="replace").stdout


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("blacklist", type=Path, help="plik czarnej listy (poza repo)")
    ap.add_argument("--repo", type=Path, default=Path(__file__).resolve().parent.parent)
    ap.add_argument("--no-history", action="store_true", help="pomiń historię git")
    args = ap.parse_args()

    if not args.blacklist.is_file():
        print(f"Brak pliku czarnej listy: {args.blacklist}", file=sys.stderr)
        return 2
    repo = args.repo.resolve()
    try:
        if args.blacklist.resolve().is_relative_to(repo):
            print("UWAGA: czarna lista leży w repozytorium. Przenieś ją poza repo.", file=sys.stderr)
            return 2
    except AttributeError:
        pass

    blacklist = load_blacklist(args.blacklist)
    hits = []

    tracked = git(repo, "ls-files").splitlines()
    files = [repo / f for f in tracked] if tracked else [
        p for p in repo.rglob("*") if p.is_file() and ".git" not in p.parts]
    for p in files:
        if p.suffix.lower() in SKIP_SUFFIXES or not p.is_file():
            continue
        if p.resolve() == Path(__file__).resolve():
            continue  # sam skrypt zawiera wzorce w regexach
        text = p.read_text(encoding="utf-8", errors="replace")
        scan_text(str(p.relative_to(repo)).replace("\\", "/"), text, blacklist, hits)

    history_note = "pominięta"
    if not args.no_history:
        log = git(repo, "log", "-p", "--all", "--format=COMMIT %H%n%s%n%b")  # autor commita to nie dane klienta
        own = "scripts/check-anonymization.py"
        cleaned, skip = [], False
        for line in log.splitlines():
            if line.startswith("diff --git"):
                skip = own in line
            if not skip:
                cleaned.append(line)
        scan_text("git log -p --all", "\n".join(cleaned), blacklist, hits)
        commits = len(git(repo, "rev-list", "--all").split())
        history_note = f"{commits} commitów"

    print(f"Czarna lista: {len(blacklist)} fraz, wzorce generyczne: {len(GENERIC)}")
    print(f"Pliki: {len(files)}, historia: {history_note}")
    if not hits:
        print("WYNIK: 0 trafień")
        return 0
    for label, lineno, kind, match, line in hits:
        print(f"{label}:{lineno}: [{kind}] {match!r} | {line[:160]}")
    print(f"WYNIK: {len(hits)} trafień")
    return 1


if __name__ == "__main__":
    sys.exit(main())

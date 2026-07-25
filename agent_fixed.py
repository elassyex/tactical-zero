#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║         AUTONOMOUS BUG BOUNTY HUNTING AGENT                  ║
║         Full Recon + AI Analysis Pipeline                    ║
╚══════════════════════════════════════════════════════════════╝
Usage: python agent_fixed.py
       python agent_fixed.py --target https://example.com
       python agent_fixed.py --skip-slow
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

# ─────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────
WORDLIST_DIR = os.environ.get("BBF_WORDLIST_DIR", "/Users/mac/bugbounty-dataset")
WORDLISTS = {
    "dns_top":      f"{WORDLIST_DIR}/subdomains-top1million-110000.txt",
    "dns_jhaddix":  f"{WORDLIST_DIR}/dns-Jhaddix.txt",
    "dns_bitquark": f"{WORDLIST_DIR}/bitquark-subdomains-top100000.txt",
    "dir_common":   f"{WORDLIST_DIR}/common.txt",
    "dir_raft_med": f"{WORDLIST_DIR}/raft-medium-directories.txt",
    "dir_raft_lg":  f"{WORDLIST_DIR}/raft-large-directories.txt",
    "dir_files":    f"{WORDLIST_DIR}/raft-large-files.txt",
    "params":       f"{WORDLIST_DIR}/burp-parameter-names.txt",
    "best_dns":     f"{WORDLIST_DIR}/best-dns-wordlist.txt",
    "api_endpoints": f"{WORDLIST_DIR}/api-endpoints.txt",
    "dns_top_5k":   f"{WORDLIST_DIR}/SecLists/Discovery/DNS/subdomains-top1million-5000.txt",
}

OLLAMA_MODEL = "bugbounty-hunter"


# ─────────────────────────────────────────────────────────────
# BASIC HELPERS
# ─────────────────────────────────────────────────────────────
def q(value) -> str:
    return shlex.quote(str(value))


def banner():
    print("""
\033[1;32m╔══════════════════════════════════════════════════════════════╗
║         AUTONOMOUS BUG BOUNTY HUNTING AGENT                  ║
╚══════════════════════════════════════════════════════════════╝\033[0m
""")


def section(title):
    print(f"\n\033[1;36m{'─'*60}\033[0m")
    print(f"\033[1;33m  {title}\033[0m")
    print(f"\033[1;36m{'─'*60}\033[0m")


def info(msg):   print(f"\033[1;34m[*]\033[0m {msg}")
def success(msg): print(f"\033[1;32m[+]\033[0m {msg}")
def warn(msg):   print(f"\033[1;33m[!]\033[0m {msg}")
def error(msg):  print(f"\033[1;31m[-]\033[0m {msg}")


def run(cmd, timeout=120, silent=False):
    if not silent:
        info(f"Running: {cmd[:120]}...")
    try:
        r = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        out = (r.stdout or "").strip()
        err = (r.stderr or "").strip()
        if not silent:
            if out:
                lines = out.splitlines()
                preview = "\n".join(lines[:5])
                if len(lines) > 5:
                    preview += f"\n... (+{len(lines)-5} more lines)"
                print(f"\033[0;90m{preview}\033[0m")
            elif err:
                preview = "\n".join(err.splitlines()[:5])
                print(f"\033[0;90m{preview}\033[0m")
        return out
    except subprocess.TimeoutExpired:
        warn(f"Timeout: {cmd[:100]}")
        return ""
    except Exception as e:
        warn(f"Error: {e}")
        return ""


def tool_exists(tool):
    return shutil.which(tool) is not None


def write_file(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content or "", encoding="utf-8", errors="ignore")


def append_file(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", errors="ignore") as f:
        f.write(content or "")


def read_file(path):
    try:
        return Path(path).read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def count_lines(path):
    try:
        p = Path(path)
        if not p.exists():
            return 0
        return len(p.read_text(encoding="utf-8", errors="ignore").splitlines())
    except Exception:
        return 0


def write_lines(path, items):
    items = [str(x).strip() for x in items if str(x).strip()]
    write_file(path, "\n".join(items) + ("\n" if items else ""))


def merge_text_files(folder, output):
    folder = Path(folder)
    lines = set()
    for p in folder.rglob("*"):
        if p.is_file() and p.suffix in {".txt", ".json", ".log", ".out"}:
            try:
                for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
                    line = line.strip()
                    if line:
                        lines.add(line)
            except Exception:
                pass
    write_lines(output, sorted(lines))


def extract_host_from_text(value: str) -> str:
    value = value.strip()
    if not value:
        return ""
    if value.startswith(("http://", "https://")):
        parsed = urlparse(value)
        host = parsed.netloc
    else:
        host = value.split("/")[0]
    host = host.split("@")[-1].split(":")[0]
    host = host.strip().strip("[]")
    host = host.replace("*.", "")
    host = host.rstrip(".")
    return host


def normalize_hosts_file(src_file, dst_file):
    hosts = set()
    src_file = Path(src_file)
    if src_file.exists():
        for line in src_file.read_text(encoding="utf-8", errors="ignore").splitlines():
            h = extract_host_from_text(line)
            if h:
                hosts.add(h.lower())
    write_lines(dst_file, sorted(hosts))
    return str(dst_file)


def normalize_urls_file(src_file, dst_file):
    urls = set()
    src_file = Path(src_file)
    if src_file.exists():
        for line in src_file.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith(("http://", "https://")):
                urls.add(line)
            else:
                # keep lines that look like URLs even if scheme is missing
                if "/" in line or "." in line:
                    urls.add(line)
    write_lines(dst_file, sorted(urls))
    return str(dst_file)


def normalize_target(target: str):
    target = (target or "").strip()
    if not target:
        raise ValueError("empty target")

    if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", target):
        target = "https://" + target

    parsed = urlparse(target)
    host = parsed.netloc or parsed.path
    host = host.split("@")[-1].split(":")[0].strip().strip("[]").rstrip(".")
    if not host:
        raise ValueError(f"could not parse host from target: {target}")

    base = f"{parsed.scheme}://{host}"
    path = parsed.path or ""
    if path and path != "/":
        base += path.rstrip("/")
    return base, host.lower()


def safe_read(path, limit=2000):
    try:
        content = read_file(path)
        lines = content.splitlines()
        if len(lines) > 50:
            return "\n".join(lines[:50]) + f"\n... (+{len(lines)-50} more)"
        return content[:limit]
    except Exception:
        return ""


def ask_ai(prompt):
    try:
        from ollama import Client
        client = Client(host=os.environ.get("OLLAMA_HOST", "http://localhost:11434"))
        r = client.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        return r.message.content
    except Exception as e:
        warn(f"AI unavailable: {e}")
        return "AI analysis unavailable - check ollama is running"


def setup_workspace(domain, workspace_override=None):
    if workspace_override:
        workspace = Path(workspace_override)
    else:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        workspace = Path(f"./hunts/{domain}_{ts}")
    workspace.mkdir(parents=True, exist_ok=True)
    for d in ["subs", "urls", "js", "params", "vulns", "reports", "ports", "dirs"]:
        (workspace / d).mkdir(exist_ok=True)
    return workspace


def is_projectdiscovery_httpx():
    if not tool_exists("httpx"):
        return False
    out = run("httpx -h", silent=True)
    text = (out or "").lower()
    return "projectdiscovery" in text or "-status-code" in text or "-web-server" in text


# ─────────────────────────────────────────────────────────────
# STEP 1: PASSIVE SUBDOMAIN ENUMERATION
# ─────────────────────────────────────────────────────────────
def passive_subdomains(domain, ws):
    section("STEP 1: PASSIVE SUBDOMAIN ENUMERATION")
    subs_dir = ws / "subs"

    if tool_exists("subfinder"):
        run(f"subfinder -d {q(domain)} -all -recursive -silent -o {q(subs_dir/'subfinder.txt')}")
        success(f"subfinder: {count_lines(subs_dir/'subfinder.txt')} subs")
    else:
        warn("subfinder not installed")

    if tool_exists("assetfinder"):
        run(f"echo {q(domain)} | assetfinder -subs-only > {q(subs_dir / 'assetfinder.txt')}")
        success(f"assetfinder: {count_lines(subs_dir/'assetfinder.txt')} subs")
    else:
        warn("assetfinder not installed")

    if tool_exists("amass"):
        run(f"amass enum -d {q(domain)} -passive -timeout 5 -o {q(subs_dir/'amass.txt')}", timeout=360)
        success(f"amass: {count_lines(subs_dir/'amass.txt')} subs")
    else:
        warn("amass not installed")

    if tool_exists("findomain"):
        run(f"findomain -t {q(domain)} -u {q(subs_dir/'findomain.txt')}", timeout=120)
        success(f"findomain: {count_lines(subs_dir/'findomain.txt')} subs")
    else:
        warn("findomain not installed")

    info("Fetching crt.sh...")
    crtsh = run(
        f"curl -fsSL {q(f'https://crt.sh/?q=%25.{domain}&output=json')} "
        f'| python3 -c "import sys,json; data=json.load(sys.stdin); '
        f'[print(x) for item in data for x in item.get(\'name_value\',\'\').split(\'\\n\')]" '
        f'| sed \'s/\\*\\.//g\' | grep -oE "[A-Za-z0-9._-]+\\.{re.escape(domain)}" | sort -u',
        silent=True,
        timeout=180,
    )
    write_file(subs_dir / "crtsh.txt", crtsh)
    success(f"crt.sh: {count_lines(subs_dir/'crtsh.txt')} subs")

    if tool_exists("waybackurls"):
        wb = run(f'echo {q(domain)} | waybackurls 2>/dev/null | grep -oE "[A-Za-z0-9._-]+\\.{re.escape(domain)}" | sort -u', silent=True, timeout=180)
        write_file(subs_dir / "wayback_subs.txt", wb)
        success(f"wayback subs: {count_lines(subs_dir/'wayback_subs.txt')} subs")

    merge_text_files(subs_dir, subs_dir / "all_subs.txt")
    normalize_hosts_file(subs_dir / "all_subs.txt", subs_dir / "all_hosts.txt")
    success(f"Total unique subdomains: {count_lines(subs_dir/'all_subs.txt')}")
    return str(subs_dir / "all_subs.txt")


# ─────────────────────────────────────────────────────────────
# STEP 2: ACTIVE SUBDOMAIN ENUMERATION / BRUTEFORCE
# ─────────────────────────────────────────────────────────────
def active_subdomains(domain, ws, skip_slow=False):
    section("STEP 2: ACTIVE SUBDOMAIN BRUTEFORCE")
    subs_dir = ws / "subs"

    if skip_slow:
        warn("Skipping (--skip-slow flag set)")
        return

    wordlist = WORDLISTS["dns_top"] if os.path.exists(WORDLISTS["dns_top"]) else WORDLISTS["dns_jhaddix"]

    if tool_exists("puredns"):
        resolvers = "/tmp/resolvers.txt"
        if not os.path.exists(resolvers):
            run(f"wget -q https://raw.githubusercontent.com/trickest/resolvers/main/resolvers.txt -O {q(resolvers)}", timeout=120)
        run(f"puredns bruteforce {q(wordlist)} {q(domain)} -r {q(resolvers)} -q > {q(subs_dir/'puredns.txt')}", timeout=900)
        success(f"puredns: {count_lines(subs_dir/'puredns.txt')} subs")
    else:
        warn("puredns not installed")

    if tool_exists("dnsx"):
        run(f"dnsx -silent -d {q(domain)} -w {q(wordlist)} -o {q(subs_dir/'dnsx.txt')}", timeout=600)
        success(f"dnsx: {count_lines(subs_dir/'dnsx.txt')} subs")
    else:
        warn("dnsx not installed")

    merge_text_files(subs_dir, subs_dir / "all_subs.txt")
    normalize_hosts_file(subs_dir / "all_subs.txt", subs_dir / "all_hosts.txt")
    success(f"Total after bruteforce: {count_lines(subs_dir/'all_subs.txt')}")


# ─────────────────────────────────────────────────────────────
# STEP 3: SUBDOMAIN FUZZING
# ─────────────────────────────────────────────────────────────
def subdomain_fuzzing(domain, ws):
    section("STEP 3: SUBDOMAIN FUZZING (FFUF)")
    subs_dir = ws / "subs"
    wordlist = WORDLISTS["dns_top"] if os.path.exists(WORDLISTS["dns_top"]) else WORDLISTS["dns_top_5k"]

    if not tool_exists("ffuf"):
        warn("ffuf not installed")
        return

    # use a sane filter set; avoid malformed extension handling
    run(
        f"ffuf -u {q(f'https://FUZZ.{domain}')} -w {q(wordlist)} "
        f"-mc 200,301,302,403 -noninteractive -o {q(subs_dir/'ffuf_subs.json')} -of json",
        timeout=180,
    )

    run(
        f'ffuf -u {q(f"https://{domain}")} -w {q(wordlist)} -H "Host: FUZZ.{domain}" '
        f"-mc 200,201,301,302,307,403 -noninteractive -o {q(subs_dir/'vhosts.json')} -of json",
        timeout=180,
    )

    success("Subdomain fuzzing complete")


# ─────────────────────────────────────────────────────────────
# STEP 4: INFRASTRUCTURE DISCOVERY
# ─────────────────────────────────────────────────────────────
def infrastructure_discovery(domain, ws):
    section("STEP 4: INFRASTRUCTURE DISCOVERY")
    subs_dir = ws / "subs"

    whois_data = run(f"whois {q(domain)} 2>/dev/null | head -40", silent=True)
    write_file(subs_dir / "whois.txt", whois_data)

    if tool_exists("asnmap"):
        asn = run(f"asnmap -d {q(domain)} -silent 2>/dev/null", silent=True)
        write_file(subs_dir / "asn.txt", asn)
        if asn:
            success(f"ASN: {asn[:100]}")
            if tool_exists("dnsx"):
                run(f"echo {q(asn)} | asnmap -silent | dnsx -silent -resp-only -ptr > {q(subs_dir/'ptr_records.txt')}", timeout=180)
    else:
        warn("asnmap not installed")

    if tool_exists("hakrevdns"):
        ip = run(f"dig +short {q(domain)} 2>/dev/null | head -1", silent=True).strip()
        if ip:
            run(f"echo {q(ip)} | hakrevdns -d > {q(subs_dir/'hakrevdns.txt')}", timeout=90)

    if tool_exists("originiphunter"):
        run(f"echo {q(domain)} | originiphunter > {q(subs_dir/'origin_ip.txt')}", timeout=120)
    else:
        origin_check = run(f"dig +short {q(domain)} 2>/dev/null", silent=True)
        write_file(subs_dir / "dns_ips.txt", origin_check)
        info(f"DNS IPs: {origin_check}")

    success("Infrastructure discovery complete")


# ─────────────────────────────────────────────────────────────
# STEP 5: ALIVE HOST DETECTION
# ─────────────────────────────────────────────────────────────
def alive_hosts(all_subs_file, ws):
    section("STEP 5: ALIVE HOST DETECTION")
    subs_dir = ws / "subs"

    if not is_projectdiscovery_httpx():
        warn("ProjectDiscovery httpx not installed or unsupported - skipping")
        return str(subs_dir / "all_hosts.txt")

    # httpx expects hosts/URLs; all_subs.txt is host-only, so this is appropriate.
    run(
        f"httpx -l {q(all_subs_file)} -timeout 3 -silent -follow-redirects -title -status-code -content-length -web-server "
        f"-o {q(subs_dir/'alive_full.txt')}",
        timeout=120,
    )

    run(
        f"httpx -l {q(all_subs_file)} -timeout 3 -silent -follow-redirects -o {q(subs_dir/'alive_urls.txt')}",
        timeout=120,
    )

    run(
        f"httpx -l {q(all_subs_file)} -timeout 3 -silent -mc 403 -follow-redirects -o {q(subs_dir/'forbidden_403.txt')}",
        timeout=120,
    )

    run(
        f"httpx -l {q(all_subs_file)} -timeout 3 -silent -mc 404 -follow-redirects -o {q(subs_dir/'not_found_404.txt')}",
        timeout=120,
    )

    normalize_hosts_file(subs_dir / "alive_urls.txt", subs_dir / "alive_hosts.txt")
    normalize_urls_file(subs_dir / "alive_urls.txt", subs_dir / "alive_urls_clean.txt")

    alive_count = count_lines(subs_dir / "alive_hosts.txt")
    forbidden_count = count_lines(subs_dir / "forbidden_403.txt")
    success(f"Alive: {alive_count} | 403 Forbidden: {forbidden_count}")
    return str(subs_dir / "alive_hosts.txt")


# ─────────────────────────────────────────────────────────────
# STEP 6: URL DISCOVERY
# ─────────────────────────────────────────────────────────────
def url_discovery(domain, alive_hosts_file, alive_urls_file, ws):
    section("STEP 6: URL DISCOVERY")
    urls_dir = ws / "urls"

    hosts = Path(alive_hosts_file)
    urls = Path(alive_urls_file)

    if tool_exists("waybackurls") and hosts.exists():
        wb_out = urls_dir / "wayback.txt"
        wb_all = []
        for host in hosts.read_text(encoding="utf-8", errors="ignore").splitlines():
            host = host.strip()
            if not host:
                continue
            out = run(f"echo {q(host)} | waybackurls 2>/dev/null", silent=True, timeout=180)
            if out:
                wb_all.extend(out.splitlines())
        write_lines(wb_out, wb_all)
        success(f"waybackurls: {count_lines(wb_out)} URLs")

    if tool_exists("waymore") and hosts.exists():
        run(
            f"waymore -i {q(hosts)} -mode U -oU {q(urls_dir/'waymore.txt')}",
            timeout=900,
        )
        success(f"waymore: {count_lines(urls_dir/'waymore.txt')} URLs")

    if tool_exists("gau") and hosts.exists():
        out = run(f"cat {q(hosts)} | gau --threads 50", silent=True, timeout=300)
        write_file(urls_dir / "gau.txt", out)
        success(f"gau: {count_lines(urls_dir/'gau.txt')} URLs")

    if tool_exists("gauplus") and hosts.exists():
        out = run(f"cat {q(hosts)} | gauplus -t 50 -random-agent", silent=True, timeout=300)
        write_file(urls_dir / "gauplus.txt", out)
        success(f"gauplus: {count_lines(urls_dir/'gauplus.txt')} URLs")

    if tool_exists("hakrawler") and urls.exists():
        out = run(f"cat {q(urls)} | hakrawler -subs -u -insecure", silent=True, timeout=300)
        write_file(urls_dir / "hakrawler.txt", out)
        success(f"hakrawler: {count_lines(urls_dir/'hakrawler.txt')} URLs")

    if tool_exists("katana") and urls.exists():
        run(
            f"katana -list {q(urls)} -jc -kf all -d 5 -fx -aff -f url -silent > {q(urls_dir/'katana.txt')}",
            timeout=600,
        )
        success(f"katana: {count_lines(urls_dir/'katana.txt')} URLs")

    if tool_exists("gospider") and urls.exists():
        outdir = urls_dir / "gospider"
        outdir.mkdir(exist_ok=True)
        run(
            f"gospider -S {q(urls)} -t 20 -d 3 --js --sitemap --robots -o {q(outdir)}",
            timeout=600,
        )
        collected = []
        for p in outdir.rglob("*"):
            if p.is_file():
                try:
                    collected.extend([x for x in p.read_text(encoding="utf-8", errors="ignore").splitlines() if x.strip()])
                except Exception:
                    pass
        write_lines(urls_dir / "gospider.txt", collected)
        success(f"gospider: {count_lines(urls_dir/'gospider.txt')} URLs")

    if tool_exists("paramspider"):
        run(f"paramspider -d {q(domain)} -o {q(urls_dir/'paramspider.txt')}", timeout=180)
        success(f"paramspider: {count_lines(urls_dir/'paramspider.txt')} URLs")

    info("Wayback sensitive file enumeration...")
    sensitive_ext = (
        r"\.xls|\.xlsx|\.csv|\.sql|\.db|\.bak|\.backup|\.old|\.tar\.gz|\.tgz|"
        r"\.zip|\.7z|\.rar|\.pdf|\.log|\.ini|\.conf|\.config|\.env|\.json|\.xml|"
        r"\.yml|\.yaml|\.pem|\.key|\.crt|\.ssh|\.git|\.htaccess|\.htpasswd|\.php|"
        r"\.swp|\.dump|\.dmp|\.DS_Store|\.npmrc|\.dockerignore|\.env\.local|"
        r"\.env\.prod|\.env\.dev|\.env\.production|\.env\.staging"
    )
    wb_sensitive = []
    if tool_exists("waybackurls") and hosts.exists():
        for host in hosts.read_text(encoding="utf-8", errors="ignore").splitlines():
            host = host.strip()
            if not host:
                continue
            out = run(f"echo {q(host)} | waybackurls 2>/dev/null | grep -iE {q(sensitive_ext)}", silent=True, timeout=180)
            if out:
                wb_sensitive.extend(out.splitlines())
    write_lines(urls_dir / "wayback_sensitive.txt", wb_sensitive)
    success(f"Wayback sensitive files: {count_lines(urls_dir/'wayback_sensitive.txt')}")

    merge_text_files(urls_dir, urls_dir / "all_urls.txt")
    normalize_urls_file(urls_dir / "all_urls.txt", urls_dir / "all_urls_clean.txt")
    success(f"Total unique URLs: {count_lines(urls_dir/'all_urls.txt')}")
    return str(urls_dir / "all_urls.txt")


# ─────────────────────────────────────────────────────────────
# STEP 7: EXTRACT & CATEGORIZE INTERESTING ENDPOINTS
# ─────────────────────────────────────────────────────────────
def extract_endpoints(all_urls_file, ws):
    section("STEP 7: EXTRACTING INTERESTING ENDPOINTS")
    urls_dir = ws / "urls"

    categories = {
        "js.txt":          r"\.js(\?|$)",
        "asp.txt":         r"\.asp(\?|$)",
        "php.txt":         r"\.php(\?|$)",
        "jsp.txt":         r"\.jsp(\?|$)|\.jspx(\?|$)",
        "aspx.txt":        r"\.aspx(\?|$)",
        "api.txt":         r"/api/|/v[0-9]+/|graphql|gql|\.json(\?|$)|\.xml(\?|$)",
        "admin.txt":       r"admin|dashboard|internal|manage|panel|cp|cms",
        "auth.txt":        r"login|signin|sign-in|auth|oauth|sso|reset|password|forgot|register|signup",
        "upload.txt":      r"upload|file|download|import|export|image|media|attachment|document",
        "idor.txt":        r"[?&/][a-z_-]*(id|uid|user|account|order|invoice|ticket|num)=?[0-9]+",
        "redirect.txt":    r"url=|redirect=|r=|u=|goto=|return=|dest=|next=|target=|rurl=|returnUrl=",
        "debug.txt":       r"debug|test|dev|beta|staging|internal|local|temp|backup|old",
        "sensitive.txt":   r"\.env|\.bak|\.sql|\.log|\.config|\.conf|\.cfg|\.git|\.svn|backup",
        "cloud.txt":       r"aws|s3|bucket|gcp|azure|vault|token|apikey|api_key|secret|credential",
        "params.txt":      r"=",
        "ssrf.txt":        r"url=|uri=|src=|href=|path=|host=|domain=|http://|https://",
        "lfi.txt":         r"file=|path=|dir=|folder=|include=|page=|doc=|root=|pg=|style=",
        "rce.txt":         r"cmd=|exec=|command=|execute=|ping=|query=|jump=|code=|reg=|do=",
        "sqli.txt":        r"id=|select=|insert=|update=|delete=|where=|order=|sort=|cat=|search=",
        "xss.txt":         r"q=|s=|search=|lang=|keyword=|query=|name=|input=|text=|email=",
    }

    all_urls = Path(all_urls_file)
    lines = []
    if all_urls.exists():
        lines = all_urls.read_text(encoding="utf-8", errors="ignore").splitlines()

    for filename, pattern in categories.items():
        out = [x for x in lines if re.search(pattern, x, re.I)]
        write_lines(urls_dir / filename, out)
        if out:
            success(f"{filename}: {len(out)} URLs")

    if tool_exists("urinteresting") and all_urls.exists():
        out = run(f"cat {q(all_urls)} | urinteresting", silent=True, timeout=120)
        write_file(urls_dir / "interesting.txt", out)
        success(f"urinteresting: {count_lines(urls_dir/'interesting.txt')} URLs")

    if is_projectdiscovery_httpx() and all_urls.exists():
        run(
            f"httpx -l {q(all_urls)} -silent -status-code -content-length -o {q(urls_dir/'live_urls.txt')}",
            timeout=600,
        )
        success(f"Live URLs: {count_lines(urls_dir/'live_urls.txt')}")

    # parameter extraction from URLs
    param_names = set()
    param_keys = set()
    for u in lines:
        if "=" not in u:
            continue
        param_keys.add(re.sub(r"=[^&]*", "=", u))
        qs = u.split("?", 1)[1] if "?" in u else ""
        for part in qs.split("&"):
            if "=" in part:
                param_names.add(part.split("=", 1)[0].strip())

    write_lines(urls_dir / "param_keys.txt", sorted(param_keys))
    write_lines(urls_dir / "param_names.txt", sorted(param_names))
    success(f"Unique parameters: {count_lines(urls_dir/'param_names.txt')}")
    return urls_dir


# ─────────────────────────────────────────────────────────────
# STEP 8: JAVASCRIPT ANALYSIS
# ─────────────────────────────────────────────────────────────
def javascript_analysis(urls_dir, ws):
    section("STEP 8: JAVASCRIPT SECRET DISCOVERY")
    js_dir = ws / "js"
    js_file = urls_dir / "js.txt"

    if count_lines(js_file) == 0:
        warn("No JS files found")
        return

    if tool_exists("subjs"):
        run(f"cat {q(js_file)} | subjs > {q(js_dir/'subjs_extra.txt')}", timeout=180)
        if count_lines(js_dir / "subjs_extra.txt") > 0:
            append_file(js_file, "\n" + read_file(js_dir / "subjs_extra.txt"))

    if tool_exists("mantra"):
        run(f"cat {q(js_file)} | mantra > {q(js_dir/'mantra_secrets.txt')}", timeout=180)
        success(f"mantra secrets: {count_lines(js_dir/'mantra_secrets.txt')}")

    if tool_exists("jsecret"):
        run(f"cat {q(js_file)} | jsecret > {q(js_dir/'jsecret.txt')}", timeout=180)
        success(f"jsecret: {count_lines(js_dir/'jsecret.txt')}")

    if tool_exists("jsleak"):
        run(
            f"cat {q(js_file)} | xargs -P 10 -I {{}} jsleak -s -l -k -e {{}} >> {q(js_dir/'jsleak.txt')} 2>/dev/null",
            timeout=180,
        )
        success(f"jsleak: {count_lines(js_dir/'jsleak.txt')}")

    if tool_exists("trufflehog"):
        # Only scan local files if you actually downloaded them later; keep this best-effort.
        run(f"trufflehog filesystem {q(js_dir)} --json > {q(js_dir/'trufflehog.json')} 2>/dev/null", timeout=180)
        success("trufflehog scan complete")

    info("Manual regex secret extraction...")
    secrets_regex = (
        r"api[_-]?key|apikey|api_secret|access[_-]?token|auth[_-]?token|"
        r"secret[_-]?key|private[_-]?key|client[_-]?secret|password|passwd|"
        r"aws_access|aws_secret|AKIA[0-9A-Z]{16}|"
        r"ghp_[a-zA-Z0-9]{36}|gho_[a-zA-Z0-9]{36}|"
        r"eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+"
    )
    js_secrets = []
    for url in js_file.read_text(encoding="utf-8", errors="ignore").splitlines():
        url = url.strip()
        if not url:
            continue
        body = run(f"curl -fsSk {q(url)} 2>/dev/null", silent=True, timeout=30)
        if body:
            for m in re.finditer(secrets_regex, body, re.I):
                js_secrets.append(m.group(0))
    write_lines(js_dir / "regex_secrets.txt", sorted(set(js_secrets)))
    success(f"Regex secrets: {count_lines(js_dir/'regex_secrets.txt')}")

    if tool_exists("lazyegg") or os.path.exists("lazyegg.py"):
        cmd = "python3 lazyegg.py" if os.path.exists("lazyegg.py") else "lazyegg"
        lazy_cmd = f'{cmd} "{{}}" --js_urls --domains --ips'
        run(
            f"cat {q(js_file)} | head -20 | xargs -I {{}} bash -lc {q(lazy_cmd)} > {q(js_dir/'lazyegg.txt')} 2>/dev/null",
            timeout=180,
        )


# ─────────────────────────────────────────────────────────────
# STEP 9: PORT DISCOVERY
# ─────────────────────────────────────────────────────────────
def port_discovery(alive_hosts_file, ws):
    section("STEP 9: PORT DISCOVERY")
    ports_dir = ws / "ports"
    hosts_file = Path(alive_hosts_file)

    if tool_exists("naabu"):
        run(
            f"naabu -list {q(hosts_file)} -p 1-65535 -rate 1000 -silent -o {q(ports_dir/'naabu_all.txt')}",
            timeout=900,
        )
        run(
            f"naabu -list {q(hosts_file)} -top-ports 1000 -silent -o {q(ports_dir/'naabu_top1000.txt')}",
            timeout=360,
        )
        success(f"naabu: {count_lines(ports_dir/'naabu_top1000.txt')} open ports")
    else:
        warn("naabu not installed")

    if tool_exists("nmap"):
        run(
            f"nmap -iL {q(hosts_file)} -T4 -Pn --open -sV --version-intensity 3 -oN {q(ports_dir/'nmap.txt')} 2>/dev/null",
            timeout=900,
        )
        success("nmap scan complete")
    else:
        warn("nmap not installed")


# ─────────────────────────────────────────────────────────────
# STEP 10: DIRECTORY FUZZING & SCANNING
# ─────────────────────────────────────────────────────────────
def directory_scanning(target, alive_urls_file, ws):
    section("STEP 10: DIRECTORY FUZZING & SCANNING")
    dirs_dir = ws / "dirs"
    wordlist = WORDLISTS["dir_common"] if os.path.exists(WORDLISTS["dir_common"]) else f"{WORDLIST_DIR}/SecLists/Discovery/Web-Content/common.txt"
    raft_med = WORDLISTS["dir_raft_med"] if os.path.exists(WORDLISTS["dir_raft_med"]) else wordlist
    extensions = "php,html,json,js,log,txt,bak,old,zip,tar.gz,asp,aspx,jsp,xml,config,conf,sql,env"

    if tool_exists("feroxbuster"):
        run(
            f"feroxbuster -u {q(target)} -w {q(raft_med)} -t 50 -k -d 3 -e -x {q(extensions)} --silent -o {q(dirs_dir/'feroxbuster.txt')}",
            timeout=900,
        )
        success(f"feroxbuster: {count_lines(dirs_dir/'feroxbuster.txt')} paths")

    if tool_exists("gobuster"):
        run(
            f"gobuster dir -u {q(target)} -w {q(wordlist)} -k -q -x {q(extensions)} -o {q(dirs_dir/'gobuster.txt')} 2>/dev/null",
            timeout=900,
        )
        success(f"gobuster: {count_lines(dirs_dir/'gobuster.txt')} paths")

    if tool_exists("ffuf"):
        run(
            f"ffuf -u {q(target)}/FUZZ -w {q(wordlist)} -mc 200,201,301,302,307,401,403 -noninteractive -o {q(dirs_dir/'ffuf_dirs.json')} -of json",
            timeout=300,
        )
        run(
            f"ffuf -u {q(target)}/FUZZ -w {q(raft_med)} -e .{extensions.replace(',',',.')} -mc 200,201,204 -noninteractive -o {q(dirs_dir/'ffuf_files.json')} -of json",
            timeout=300,
        )
        run(
            f'ffuf -u {q(target)}/FUZZ -w {q(wordlist)} -H "X-Forwarded-For: 127.0.0.1" -H "X-Original-URL: /FUZZ" -mc 200,201 -noninteractive -o {q(dirs_dir/"ffuf_403bypass.json")} -of json',
            timeout=300,
        )
        success("ffuf scans complete")

    if tool_exists("dirsearch") or os.path.exists("dirsearch.py"):
        cmd = "dirsearch" if tool_exists("dirsearch") else "python3 dirsearch.py"
        run(
            f"{cmd} -u {q(target)} -e {q(extensions)} -i 200,204,301,302,307,308,401,403 -x 404,500,501,502,503 --random-agent --full-url -r -R 3 -q --no-color -o {q(dirs_dir/'dirsearch.txt')}",
            timeout=600,
        )
        success(f"dirsearch: {count_lines(dirs_dir/'dirsearch.txt')} paths")

    if tool_exists("bfac"):
        run(
            f"bfac --url {q(target)} --detection-technique all --level 3 --exclude-status-codes 404,500 > {q(dirs_dir/'bfac.txt')} 2>/dev/null",
            timeout=180,
        )
        success(f"bfac: {count_lines(dirs_dir/'bfac.txt')} backup files")


# ─────────────────────────────────────────────────────────────
# STEP 11: API ENDPOINT DISCOVERY
# ─────────────────────────────────────────────────────────────
def api_discovery(target, ws):
    section("STEP 11: API ENDPOINT DISCOVERY")
    dirs_dir = ws / "dirs"

    if tool_exists("kr"):
        run(
            f"kr scan {q(target)} -A=apiroutes-260227:10000 -x 8 -j 15 -v info > {q(dirs_dir/'kiterunner_api.txt')} 2>/dev/null",
            timeout=600,
        )
        run(
            f"kr scan {q(target)} -A=parameters-260227:5000 -x 5 -j 10 -v info >> {q(dirs_dir/'kiterunner_params.txt')} 2>/dev/null",
            timeout=600,
        )
        success(f"kiterunner: {count_lines(dirs_dir/'kiterunner_api.txt')} endpoints")
    else:
        warn("kiterunner (kr) not installed")
        if tool_exists("ffuf"):
            api_wordlist = WORDLISTS["api_endpoints"]
            if os.path.exists(api_wordlist):
                run(
                    f"ffuf -u {q(target)}/FUZZ -w {q(api_wordlist)} -mc 200,201,204,401,403 -noninteractive -o {q(dirs_dir/'ffuf_api.json')} -of json",
                    timeout=180,
                )


# ─────────────────────────────────────────────────────────────
# STEP 12: HIDDEN PARAMETER DISCOVERY
# ─────────────────────────────────────────────────────────────
def parameter_discovery(target, urls_dir, ws):
    section("STEP 12: HIDDEN PARAMETER DISCOVERY")
    params_dir = ws / "params"
    params_wl = WORDLISTS["params"] if os.path.exists(WORDLISTS["params"]) else ""
    php_file = urls_dir / "php.txt"
    all_urls = urls_dir / "all_urls.txt"

    if tool_exists("arjun"):
        run(f"arjun -u {q(target)} -q -oJ {q(params_dir/'arjun_main.json')}", timeout=300)
        if count_lines(php_file) > 0:
            run(f"arjun -i {q(php_file)} -q -oJ {q(params_dir/'arjun_php.json')}", timeout=300)
        run(f"arjun -u {q(target)} -m post -q -oJ {q(params_dir/'arjun_post.json')}", timeout=300)
        success("arjun parameter discovery complete")
    else:
        warn("arjun not installed")

    if tool_exists("x8") and params_wl:
        run(f"x8 -u {q(target)}?FUZZ=test -w {q(params_wl)} -o {q(params_dir/'x8.txt')}", timeout=180)

    if tool_exists("ffuf") and params_wl:
        run(
            f"ffuf -u {q(target)}?FUZZ=test -w {q(params_wl)} -mc 200,201 -noninteractive -o {q(params_dir/'ffuf_params.json')} -of json",
            timeout=180,
        )

    fuzz_urls = []
    if all_urls.exists():
        for l in all_urls.read_text(encoding="utf-8", errors="ignore").splitlines():
            if "?" not in l or "=" not in l:
                continue
            base, qs = l.split("?", 1)
            parts = []
            for p in qs.split("&"):
                if "=" in p:
                    k = p.split("=", 1)[0]
                    parts.append(f"{k}=FUZZ")
            if parts:
                fuzz_urls.append(base + "?" + "&".join(parts))
    write_lines(params_dir / "fuzz_urls.txt", sorted(set(fuzz_urls)))
    success(f"FUZZ-ready URLs: {count_lines(params_dir/'fuzz_urls.txt')}")


# ─────────────────────────────────────────────────────────────
# STEP 13: VULNERABILITY SCANNING
# ─────────────────────────────────────────────────────────────
def vulnerability_scan(target, alive_hosts_file, all_urls_file, ws):
    section("STEP 13: FULL VULNERABILITY SCANNING")
    vulns_dir = ws / "vulns"

    if tool_exists("nuclei"):
        run(
            f"nuclei -u {q(target)} -severity critical,high,medium -silent -o {q(vulns_dir/'nuclei_main.txt')}",
            timeout=900,
        )
        run(
            f"nuclei -u {q(target)} -t ~/.local/nuclei-templates/http/exposures/ -silent -o {q(vulns_dir/'nuclei_exposures.txt')} 2>/dev/null",
            timeout=900,
        )
        run(
            f"nuclei -u {q(target)} -t ~/.local/nuclei-templates/http/cves/ -severity critical,high -silent -o {q(vulns_dir/'nuclei_cves.txt')} 2>/dev/null",
            timeout=900,
        )
        run(
            f"nuclei -u {q(target)} -t ~/.local/nuclei-templates/http/technologies/ -silent -o {q(vulns_dir/'nuclei_tech.txt')} 2>/dev/null",
            timeout=900,
        )
        run(
            f"nuclei -list {q(alive_hosts_file)} -severity critical,high -silent -o {q(vulns_dir/'nuclei_bulk.txt')}",
            timeout=900,
        )
        success(f"nuclei: {count_lines(vulns_dir/'nuclei_main.txt')} findings")
    else:
        warn("nuclei not installed")

    if tool_exists("sqlmap"):
        sqli_file = ws / "urls" / "sqli.txt"
        if count_lines(sqli_file) > 0:
            run(
                f"sqlmap -m {q(sqli_file)} --dbs --banner --batch --random-agent --output-dir={q(vulns_dir/'sqlmap')} -q 2>/dev/null",
                timeout=600,
            )
            success("sqlmap scan complete")

    if tool_exists("ffuf"):
        info("Attempting 403 bypass.")
        forbidden_file = ws / "subs" / "forbidden_403.txt"
        if count_lines(forbidden_file) > 0:
            bypass_headers = [
                "X-Forwarded-For: 127.0.0.1",
                "X-Real-IP: 127.0.0.1",
            ]
            lines = forbidden_file.read_text(encoding="utf-8", errors="ignore").splitlines()[:10]
            for header in bypass_headers:
                for url in lines:
                    run(
                        f'curl -sk -o /dev/null -w "%{{http_code}} {q(url)}\\n" -H {q(header)} {q(url)} >> {q(vulns_dir/"403_bypass.txt")}',
                        timeout=45,
                    )


# ─────────────────────────────────────────────────────────────
# STEP 14: GITHUB DORKS
# ─────────────────────────────────────────────────────────────
def github_dorks(domain, ws):
    section("STEP 14: GITHUB DORKS & SECRET DISCOVERY")
    vulns_dir = ws / "vulns"

    dorks = [
        f'"{domain}" password',
        f'"{domain}" secret',
        f'"{domain}" api_key',
        f'"{domain}" token',
        f'"{domain}" credentials',
        f'"{domain}" config',
    ]

    dorks_str = "\n".join([
        f"https://github.com/search?q={d.replace(' ', '+')}&type=code"
        for d in dorks
    ])

    write_file(vulns_dir / "github_dorks.txt", f"""
# GitHub Dork URLs for {domain}
# Open each in browser and check for exposed secrets

{dorks_str}

# GitDorker command:
# python3 GitDorker.py -tf TOKENSFILE -q {domain} -d dorks/medium_dorks.txt

# Google dorks for sensitive Google Sheets:
# site:*.{domain} intext:"docs.google.com/spreadsheets"
# site:docs.google.com/spreadsheets "{domain}"
""")

    if tool_exists("trufflehog"):
        run(
            f"trufflehog github --org={q(domain.split('.')[0])} --results=verified --json > {q(vulns_dir/'trufflehog_github.json')} 2>/dev/null",
            timeout=180,
        )

    success("GitHub dorks saved")


# ─────────────────────────────────────────────────────────────
# STEP 15: AI ANALYSIS & REPORT GENERATION
# ─────────────────────────────────────────────────────────────
def ai_analysis_and_report(target, domain, ws):
    section("STEP 15: AI VULNERABILITY ANALYSIS")
    reports_dir = ws / "reports"

    data = {
        "subdomains":  safe_read(ws / "subs" / "all_subs.txt"),
        "alive":       safe_read(ws / "subs" / "alive_full.txt"),
        "ports":       safe_read(ws / "ports" / "naabu_top1000.txt"),
        "nuclei":      safe_read(ws / "vulns" / "nuclei_main.txt"),
        "nuclei_cves": safe_read(ws / "vulns" / "nuclei_cves.txt"),
        "nuclei_exp":  safe_read(ws / "vulns" / "nuclei_exposures.txt"),
        "admin":       safe_read(ws / "urls" / "admin.txt"),
        "auth":        safe_read(ws / "urls" / "auth.txt"),
        "uploads":     safe_read(ws / "urls" / "upload.txt"),
        "idor":        safe_read(ws / "urls" / "idor.txt"),
        "api":         safe_read(ws / "urls" / "api.txt"),
        "sensitive":   safe_read(ws / "urls" / "sensitive.txt"),
        "redirect":    safe_read(ws / "urls" / "redirect.txt"),
        "ssrf":        safe_read(ws / "urls" / "ssrf.txt"),
        "lfi":         safe_read(ws / "urls" / "lfi.txt"),
        "sqli":        safe_read(ws / "urls" / "sqli.txt"),
        "xss":         safe_read(ws / "urls" / "xss.txt"),
        "js_secrets":  safe_read(ws / "js" / "regex_secrets.txt"),
        "mantra":      safe_read(ws / "js" / "mantra_secrets.txt"),
        "dirs":        safe_read(ws / "dirs" / "feroxbuster.txt"),
        "params":      safe_read(ws / "params" / "arjun_main.json"),
        "wayback_sens": safe_read(ws / "urls" / "wayback_sensitive.txt"),
        "403_bypass":  safe_read(ws / "vulns" / "403_bypass.txt"),
    }

    prompt = f"""
You are an elite bug bounty hunter. Analyze this complete recon data for {target} and provide:

1. EXECUTIVE SUMMARY - What's the most critical finding?
2. VULNERABILITY LIST - All potential vulnerabilities found, sorted by severity
3. TOP 5 ATTACK VECTORS - Most promising paths to exploit
4. MANUAL TESTING CHECKLIST - What to test next manually
5. HACKERONE REPORT - Write a complete HackerOne submission for the most critical finding

TARGET: {target}

RECON DATA
SUBDOMAINS:
{data['subdomains']}

ALIVE HOSTS:
{data['alive']}

OPEN PORTS:
{data['ports']}

NUCLEI FINDINGS:
{data['nuclei']}

NUCLEI CVEs:
{data['nuclei_cves']}

NUCLEI EXPOSURES:
{data['nuclei_exp']}

ADMIN PANELS:
{data['admin']}

AUTH ENDPOINTS:
{data['auth']}

UPLOAD ENDPOINTS:
{data['uploads']}

IDOR TARGETS:
{data['idor']}

API ENDPOINTS:
{data['api']}

SENSITIVE FILES:
{data['sensitive']}

OPEN REDIRECT PARAMS:
{data['redirect']}

SSRF CANDIDATES:
{data['ssrf']}

LFI CANDIDATES:
{data['lfi']}

SQLI CANDIDATES:
{data['sqli']}

XSS CANDIDATES:
{data['xss']}

JS SECRETS:
{data['js_secrets']}

MANTRA SECRETS:
{data['mantra']}

DIRECTORIES:
{data['dirs']}

HIDDEN PARAMS:
{data['params']}

WAYBACK SENSITIVE FILES:
{data['wayback_sens']}

403 BYPASS RESULTS:
{data['403_bypass']}
"""

    info("Running AI analysis (this may take a minute)...")
    analysis = ask_ai(prompt)

    report_content = f"""# Bug Bounty Report: {target}
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## AI Analysis
{analysis}

---

## Raw Recon Data

### Subdomains
{read_file(ws/'subs'/'all_subs.txt')}

### Alive Hosts
{read_file(ws/'subs'/'alive_full.txt')}

### Nuclei Findings
{read_file(ws/'vulns'/'nuclei_main.txt')}
{read_file(ws/'vulns'/'nuclei_cves.txt')}
{read_file(ws/'vulns'/'nuclei_exposures.txt')}

### JS Secrets
{read_file(ws/'js'/'regex_secrets.txt')}
{read_file(ws/'js'/'mantra_secrets.txt')}

### Open Ports
{read_file(ws/'ports'/'naabu_top1000.txt')}

### Admin Panels
{read_file(ws/'urls'/'admin.txt')}

### Auth Endpoints
{read_file(ws/'urls'/'auth.txt')}

### API Endpoints
{read_file(ws/'urls'/'api.txt')}

### Upload Endpoints
{read_file(ws/'urls'/'upload.txt')}

### IDOR Targets
{read_file(ws/'urls'/'idor.txt')}

### Sensitive Files
{read_file(ws/'urls'/'sensitive.txt')}

### SQLi Candidates
{read_file(ws/'urls'/'sqli.txt')}

### XSS Candidates
{read_file(ws/'urls'/'xss.txt')}

### SSRF Candidates
{read_file(ws/'urls'/'ssrf.txt')}

### LFI Candidates
{read_file(ws/'urls'/'lfi.txt')}

### Wayback Sensitive Files
{read_file(ws/'urls'/'wayback_sensitive.txt')}

### Directories
{read_file(ws/'dirs'/'feroxbuster.txt')}

### Hidden Parameters
{read_file(ws/'params'/'arjun_main.json')}
"""

    report_path = reports_dir / f"report_{domain}.md"
    write_file(report_path, report_content)

    json_path = reports_dir / f"summary_{domain}.json"
    write_file(json_path, json.dumps({
        "target": target,
        "domain": domain,
        "timestamp": datetime.now().isoformat(),
        "stats": {
            "subdomains": count_lines(ws / "subs" / "all_subs.txt"),
            "alive_hosts": count_lines(ws / "subs" / "alive_hosts.txt"),
            "total_urls": count_lines(ws / "urls" / "all_urls.txt"),
            "nuclei_findings": count_lines(ws / "vulns" / "nuclei_main.txt"),
            "js_secrets": count_lines(ws / "js" / "regex_secrets.txt"),
            "admin_panels": count_lines(ws / "urls" / "admin.txt"),
            "open_ports": count_lines(ws / "ports" / "naabu_top1000.txt"),
        },
        "ai_analysis": analysis
    }, indent=2))

    success(f"Report saved: {report_path}")
    success(f"JSON summary: {json_path}")

    print(f"\n\033[1;32m{'═'*60}\033[0m")
    print(f"\033[1;33mAI ANALYSIS:\033[0m")
    print(f"\033[1;32m{'═'*60}\033[0m")
    print(analysis)

    return str(report_path)


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────
def main():
    banner()

    parser = argparse.ArgumentParser(description="Autonomous Bug Bounty Agent")
    parser.add_argument("--target", help="Target URL (e.g. https://example.com)")
    parser.add_argument("--skip-slow", action="store_true", help="Skip slow bruteforce steps")
    parser.add_argument("--model", default="bugbounty-hunter", help="Ollama model name")
    parser.add_argument("--workspace", help="Override workspace directory path")
    args = parser.parse_args()

    global OLLAMA_MODEL
    OLLAMA_MODEL = args.model

    target = args.target or input("\033[1;32m🎯 Enter target URL: \033[0m").strip()
    target, domain = normalize_target(target)

    print(f"\n\033[1;32m[*] Target: {target}\033[0m")
    print(f"\033[1;32m[*] Domain: {domain}\033[0m")
    print(f"\033[1;32m[*] Model:  {OLLAMA_MODEL}\033[0m")
    print(f"\033[1;32m[*] Time:   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\033[0m\n")

    ws = setup_workspace(domain, args.workspace)
    success(f"Workspace: {ws}")

    start = time.time()

    all_subs = passive_subdomains(domain, ws)
    active_subdomains(domain, ws, args.skip_slow)
    subdomain_fuzzing(domain, ws)
    infrastructure_discovery(domain, ws)
    alive_hosts_file = alive_hosts(all_subs, ws)
    alive_urls_file = ws / "subs" / "alive_urls.txt"
    all_urls = url_discovery(domain, alive_hosts_file, alive_urls_file, ws)
    urls_dir = extract_endpoints(all_urls, ws)
    javascript_analysis(urls_dir, ws)
    port_discovery(alive_hosts_file, ws)
    directory_scanning(target, alive_urls_file, ws)
    api_discovery(target, ws)
    parameter_discovery(target, urls_dir, ws)
    vulnerability_scan(target, alive_hosts_file, all_urls, ws)
    github_dorks(domain, ws)
    report = ai_analysis_and_report(target, domain, ws)

    elapsed = int(time.time() - start)
    mins, secs = divmod(elapsed, 60)

    print(f"\n\033[1;32m{'═'*60}\033[0m")
    print(f"\033[1;32m✅ HUNT COMPLETE in {mins}m {secs}s\033[0m")
    print(f"\033[1;32m📁 Workspace: {ws}\033[0m")
    print(f"\033[1;32m📄 Report:    {report}\033[0m")
    print(f"\033[1;32m{'═'*60}\033[0m\n")


if __name__ == "__main__":
    main()

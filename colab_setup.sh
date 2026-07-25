#!/bin/bash
# ╔═══════════════════════════════════════════════════════════╗
# ║  TACTICAL ZERO - Colab Tool Installer                    ║
# ║  Installs all 38+ recon/vuln scanning tools             ║
# ╚═══════════════════════════════════════════════════════════╝
set -e

echo "[*] TACTICAL ZERO - Installing all tools..."
echo "============================================"

# ── System packages ──────────────────────────────────────────
echo "[*] Installing system packages..."
apt-get update -qq
apt-get install -y -qq python3-dev python3-pip wget curl git unzip tar whois dnsutils nmap -qq

# ── Go language ──────────────────────────────────────────────
echo "[*] Installing Go..."
if ! command -v go &> /dev/null; then
    GO_VERSION="1.22.4"
    wget -q "https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz" -O /tmp/go.tar.gz
    tar -C /usr/local -xzf /tmp/go.tar.gz
    rm /tmp/go.tar.gz
    export PATH=$PATH:/usr/local/go/bin
    export GOPATH=$HOME/go
    export PATH=$PATH:$GOPATH/bin
    echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
    echo 'export GOPATH=$HOME/go' >> ~/.bashrc
    echo 'export PATH=$PATH:$GOPATH/bin' >> ~/.bashrc
fi
echo "  [+] Go $(go version 2>/dev/null || echo 'installing...')"

# ── Python dependencies ──────────────────────────────────────
echo "[*] Installing Python dependencies..."
pip install -q requests pyyaml ollama openai gitpython arjun paramspider jsleak

# ── Create tools directory ───────────────────────────────────
TOOLS_DIR="/usr/local/bin"
mkdir -p $TOOLS_DIR

# ═══════════════════════════════════════════════════════════════
# SUBDOMAIN ENUMERATION
# ═══════════════════════════════════════════════════════════════
echo ""
echo "[*] === Subdomain Enumeration Tools ==="

# subfinder
echo "[*] Installing subfinder..."
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest 2>/dev/null && echo "  [+] subfinder" || echo "  [!] subfinder failed"

# assetfinder
echo "[*] Installing assetfinder..."
go install github.com/tomnomnom/assetfinder@latest 2>/dev/null && echo "  [+] assetfinder" || echo "  [!] assetfinder failed"

# amass
echo "[*] Installing amass..."
go install -v github.com/owasp-amass/amass/v4/...@master 2>/dev/null && echo "  [+] amass" || echo "  [!] amass failed"

# findomain
echo "[*] Installing findomain..."
wget -q "https://github.com/findomain/findomain/releases/latest/download/findomain-linux" -O $TOOLS_DIR/findomain && chmod +x $TOOLS_DIR/findomain && echo "  [+] findomain" || echo "  [!] findomain failed"

# ═══════════════════════════════════════════════════════════════
# DNS TOOLS
# ═══════════════════════════════════════════════════════════════
echo ""
echo "[*] === DNS Tools ==="

# dnsx
echo "[*] Installing dnsx..."
go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest 2>/dev/null && echo "  [+] dnsx" || echo "  [!] dnsx failed"

# puredns
echo "[*] Installing puredns..."
go install github.com/d3mondev/puredns/v2@latest 2>/dev/null && echo "  [+] puredns" || echo "  [!] puredns failed"

# asnmap
echo "[*] Installing asnmap..."
go install -v github.com/projectdiscovery/asnmap/cmd/asnmap@latest 2>/dev/null && echo "  [+] asnmap" || echo "  [!] asnmap failed"

# hakrevdns
echo "[*] Installing hakrevdns..."
go install github.com/hakluke/hakrevdns@latest 2>/dev/null && echo "  [+] hakrevdns" || echo "  [!] hakrevdns failed"

# ═══════════════════════════════════════════════════════════════
# HTTP PROBING
# ═══════════════════════════════════════════════════════════════
echo ""
echo "[*] === HTTP Probing Tools ==="

# httpx
echo "[*] Installing httpx..."
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest 2>/dev/null && echo "  [+] httpx" || echo "  [!] httpx failed"

# ═══════════════════════════════════════════════════════════════
# PORT SCANNING
# ═══════════════════════════════════════════════════════════════
echo ""
echo "[*] === Port Scanning Tools ==="

# naabu
echo "[*] Installing naabu..."
go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest 2>/dev/null && echo "  [+] naabu" || echo "  [!] naabu failed"

# ═══════════════════════════════════════════════════════════════
# URL DISCOVERY & CRAWLING
# ═══════════════════════════════════════════════════════════════
echo ""
echo "[*] === URL Discovery & Crawling Tools ==="

# waybackurls
echo "[*] Installing waybackurls..."
go install github.com/tomnomnom/waybackurls@latest 2>/dev/null && echo "  [+] waybackurls" || echo "  [!] waybackurls failed"

# gau (GetAllUrls)
echo "[*] Installing gau..."
go install github.com/lc/gau/v2/cmd/gau@latest 2>/dev/null && echo "  [+] gau" || echo "  [!] gau failed"

# gauplus
echo "[*] Installing gauplus..."
go install github.com/bagasjs/gauplus@latest 2>/dev/null && echo "  [+] gauplus" || echo "  [!] gauplus failed"

# katana
echo "[*] Installing katana..."
go install github.com/projectdiscovery/katana/cmd/katana@latest 2>/dev/null && echo "  [+] katana" || echo "  [!] katana failed"

# gospider
echo "[*] Installing gospider..."
go install github.com/jaeles-project/gospider@latest 2>/dev/null && echo "  [+] gospider" || echo "  [!] gospider failed"

# hakrawler
echo "[*] Installing hakrawler..."
go install github.com/hakluke/hakrawler@latest 2>/dev/null && echo "  [+] hakrawler" || echo "  [!] hakrawler failed"

# waymore
echo "[*] Installing waymore..."
pip install -q waymore 2>/dev/null && echo "  [+] waymore" || echo "  [!] waymore failed"

# ═══════════════════════════════════════════════════════════════
# DIRECTORY / VHOST FUZZING
# ═══════════════════════════════════════════════════════════════
echo ""
echo "[*] === Fuzzing Tools ==="

# ffuf
echo "[*] Installing ffuf..."
go install github.com/ffuf/ffuf/v2@latest 2>/dev/null && echo "  [+] ffuf" || echo "  [!] ffuf failed"

# feroxbuster
echo "[*] Installing feroxbuster..."
wget -q "https://github.com/epi052/feroxbuster/releases/latest/download/x86_64-linux-feroxbuster.tar.gz" -O /tmp/feroxbuster.tar.gz && tar -xzf /tmp/feroxbuster.tar.gz -C $TOOLS_DIR feroxbuster && chmod +x $TOOLS_DIR/feroxbuster && rm /tmp/feroxbuster.tar.gz && echo "  [+] feroxbuster" || echo "  [!] feroxbuster failed"

# gobuster
echo "[*] Installing gobuster..."
go install github.com/OJ/gobuster/v3@latest 2>/dev/null && echo "  [+] gobuster" || echo "  [!] gobuster failed"

# kiterunner (kr)
echo "[*] Installing kiterunner..."
go install github.com/projectdiscovery/kiterunner/cmd/kr@latest 2>/dev/null && echo "  [+] kiterunner" || echo "  [!] kiterunner failed"

# dirsearch
echo "[*] Installing dirsearch..."
git clone -q https://github.com/ma3sTi0/fr3dy/dirsearch.git /opt/dirsearch 2>/dev/null && ln -sf /opt/dirsearch/dirsearch.py $TOOLS_DIR/dirsearch && chmod +x /opt/dirsearch/dirsearch.py && echo "  [+] dirsearch" || echo "  [!] dirsearch failed"

# ═══════════════════════════════════════════════════════════════
# VULNERABILITY SCANNING
# ═══════════════════════════════════════════════════════════════
echo ""
echo "[*] === Vulnerability Scanning Tools ==="

# nuclei
echo "[*] Installing nuclei..."
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest 2>/dev/null && echo "  [+] nuclei" || echo "  [!] nuclei failed"

# nuclei templates
echo "[*] Updating nuclei templates..."
nuclei -ut 2>/dev/null || echo "  [!] nuclei template update skipped"

# sqlmap
echo "[*] Installing sqlmap..."
git clone -q https://github.com/sqlmapproject/sqlmap.git /opt/sqlmap 2>/dev/null && ln -sf /opt/sqlmap/sqlmap.py $TOOLS_DIR/sqlmap && chmod +x /opt/sqlmap/sqlmap.py && echo "  [+] sqlmap" || echo "  [!] sqlmap failed"

# ═══════════════════════════════════════════════════════════════
# PARAMETER DISCOVERY
# ═══════════════════════════════════════════════════════════════
echo ""
echo "[*] === Parameter Discovery Tools ==="

# arjun
echo "[*] Installing arjun..."
pip install -q arjun 2>/dev/null && echo "  [+] arjun" || echo "  [!] arjun failed"

# x8
echo "[*] Installing x8..."
go install github.com/Sh1Yo/x8@latest 2>/dev/null && echo "  [+] x8" || echo "  [!] x8 failed"

# paramspider
echo "[*] Installing paramspider..."
pip install -q paramspider 2>/dev/null && echo "  [+] paramspider" || echo "  [!] paramspider failed"

# ═══════════════════════════════════════════════════════════════
# JAVASCRIPT / SECRET DISCOVERY
# ═══════════════════════════════════════════════════════════════
echo ""
echo "[*] === JavaScript & Secret Discovery Tools ==="

# subjs
echo "[*] Installing subjs..."
go install github.com/lc/subjs@latest 2>/dev/null && echo "  [+] subjs" || echo "  [!] subjs failed"

# trufflehog
echo "[*] Installing trufflehog..."
go install github.com/trufflesecurity/trufflehog/v3@latest 2>/dev/null && echo "  [+] trufflehog" || echo "  [!] trufflehog failed"

# jsleak
echo "[*] Installing jsleak..."
pip install -q jsleak 2>/dev/null && echo "  [+] jsleak" || echo "  [!] jsleak failed"

# ═══════════════════════════════════════════════════════════════
# WORDLISTS
# ═══════════════════════════════════════════════════════════════
echo ""
echo "[*] === Downloading Wordlists ==="
mkdir -p /usr/share/wordlists
if [ ! -f /usr/share/wordlists/dirb/common.txt ]; then
    wget -q "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/common.txt" -O /usr/share/wordlists/dirb/common.txt 2>/dev/null
fi
if [ ! -f /usr/share/wordlists/seclist ]; then
    git clone -q --depth 1 https://github.com/danielmiessler/SecLists.git /opt/seclists 2>/dev/null
    ln -sf /opt/seclists /usr/share/wordlists/seclist 2>/dev/null
fi
echo "  [+] Wordlists ready"

# ═══════════════════════════════════════════════════════════════
# COPY BINARIES TO /usr/local/bin
# ═══════════════════════════════════════════════════════════════
echo ""
echo "[*] Copying Go binaries to PATH..."
cp -f $HOME/go/bin/* $TOOLS_DIR/ 2>/dev/null || true

# ═══════════════════════════════════════════════════════════════
# VERIFICATION
# ═══════════════════════════════════════════════════════════════
echo ""
echo "[*] ========================================"
echo "[*] TOOL VERIFICATION"
echo "[*] ========================================"
TOOLS=(
    subfinder assetfinder amass findomain
    dnsx puredns asnmap hakrevdns
    httpx
    naabu nmap
    waybackurls gau katana gospider hakrawler
    ffuf gobuster nuclei
    arjun x8 paramspider
    subjs trufflehog
)

FOUND=0
MISSING=0
for tool in "${TOOLS[@]}"; do
    if command -v "$tool" &> /dev/null; then
        echo "  [+] $tool"
        ((FOUND++))
    else
        echo "  [!] $tool NOT FOUND"
        ((MISSING++))
    fi
done

echo ""
echo "[*] ========================================"
echo "[*] SUMMARY: $FOUND tools installed, $MISSING missing"
echo "[*] ========================================"
echo ""
echo "[*] Setup complete! Run with:"
echo "    python3 bbf.py --target https://example.com --mode full"

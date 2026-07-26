#!/bin/bash
# ╔═══════════════════════════════════════════════════════════╗
# ║  TACTICAL ZERO - Colab Full Tool Installer               ║
# ║  Installs ALL 38+ recon/vuln scanning tools              ║
# ╚═══════════════════════════════════════════════════════════╝

echo "[*] TACTICAL ZERO - Installing all tools..."
echo "============================================"

# ── System packages ──────────────────────────────────────────
echo "[*] Installing system packages..."
apt-get update -qq
apt-get install -y -qq python3-dev python3-pip wget curl git unzip tar whois dnsutils nmap jq

# ── Go language ──────────────────────────────────────────────
echo "[*] Installing Go..."
if ! command -v go &> /dev/null; then
    GO_VERSION="1.22.4"
    wget -q "https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz" -O /tmp/go.tar.gz
    tar -C /usr/local -xzf /tmp/go.tar.gz
    rm /tmp/go.tar.gz
fi
export PATH=/usr/local/go/bin:$HOME/go/bin:$PATH
export GOPATH=$HOME/go
mkdir -p $HOME/go/bin
echo 'export PATH=/usr/local/go/bin:$HOME/go/bin:$PATH' >> /etc/environment
echo "  [+] Go $(go version)"

# ── Python dependencies ──────────────────────────────────────
echo "[*] Installing Python dependencies..."
pip install -q requests pyyaml ollama openai gitpython arjun paramspider jsleak waymore 2>&1 | tail -1

TOOLS_DIR="/usr/local/bin"
FAILED=0
INSTALLED=0

install_go() {
    local name=$1
    local pkg=$2
    echo -n "  [*] $name... "
    if go install $pkg 2>&1 | tail -3; then
        cp -f $HOME/go/bin/$name $TOOLS_DIR/ 2>/dev/null
        chmod +x $TOOLS_DIR/$name 2>/dev/null
        echo "[OK]"
        ((INSTALLED++))
    else
        echo "[FAILED]"
        ((FAILED++))
    fi
}

install_binary() {
    local name=$1
    local url=$2
    echo -n "  [*] $name... "
    if wget -q "$url" -O "$TOOLS_DIR/$name" 2>/dev/null; then
        chmod +x "$TOOLS_DIR/$name"
        echo "[OK]"
        ((INSTALLED++))
    else
        echo "[FAILED]"
        ((FAILED++))
    fi
}

install_git() {
    local name=$1
    local repo=$2
    local path=${3:-$name.py}
    echo -n "  [*] $name... "
    if git clone -q "$repo" "/opt/$name" 2>/dev/null; then
        ln -sf "/opt/$name/$path" "$TOOLS_DIR/$name"
        chmod +x "/opt/$name/$path" 2>/dev/null
        echo "[OK]"
        ((INSTALLED++))
    else
        echo "[FAILED]"
        ((FAILED++))
    fi
}

# ═══════════════════════════════════════════════════════════════
# SUBDOMAIN ENUMERATION
# ═══════════════════════════════════════════════════════════════
echo ""
echo "[*] === Subdomain Enumeration ==="
install_go subfinder "github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"
install_go assetfinder "github.com/tomnomnom/assetfinder@latest"
install_go amass "github.com/owasp-amass/amass/v4/cmd/amass@latest"
install_binary findomain "https://github.com/findomain/findomain/releases/latest/download/findomain-linux"

# ═══════════════════════════════════════════════════════════════
# DNS TOOLS
# ═══════════════════════════════════════════════════════════════
echo ""
echo "[*] === DNS Tools ==="
install_go dnsx "github.com/projectdiscovery/dnsx/cmd/dnsx@latest"
install_go puredns "github.com/d3mondev/puredns/v2@latest"
install_go asnmap "github.com/projectdiscovery/asnmap/cmd/asnmap@latest"
install_go hakrevdns "github.com/hakluke/hakrevdns@latest"

# ═══════════════════════════════════════════════════════════════
# HTTP PROBING
# ═══════════════════════════════════════════════════════════════
echo ""
echo "[*] === HTTP Probing ==="
install_go httpx "github.com/projectdiscovery/httpx/cmd/httpx@latest"

# ═══════════════════════════════════════════════════════════════
# PORT SCANNING
# ═══════════════════════════════════════════════════════════════
echo ""
echo "[*] === Port Scanning ==="
install_go naabu "github.com/projectdiscovery/naabu/v2/cmd/naabu@latest"

# ═══════════════════════════════════════════════════════════════
# URL DISCOVERY & CRAWLING
# ═══════════════════════════════════════════════════════════════
echo ""
echo "[*] === URL Discovery & Crawling ==="
install_go waybackurls "github.com/tomnomnom/waybackurls@latest"
install_go gau "github.com/lc/gau/v2/cmd/gau@latest"
install_go gauplus "github.com/bagasjs/gauplus@latest"
install_go katana "github.com/projectdiscovery/katana/cmd/katana@latest"
install_go gospider "github.com/jaeles-project/gospider@latest"
install_go hakrawler "github.com/hakluke/hakrawler@latest"

# ═══════════════════════════════════════════════════════════════
# FUZZING
# ═══════════════════════════════════════════════════════════════
echo ""
echo "[*] === Fuzzing ==="
install_go ffuf "github.com/ffuf/ffuf/v2@latest"
install_go gobuster "github.com/OJ/gobuster/v3@latest"
install_go kiterunner "github.com/projectdiscovery/kiterunner/cmd/kr@latest"
install_git dirsearch "https://github.com/ma3sTi0/fr3dy/dirsearch.git" "dirsearch.py"

# ═══════════════════════════════════════════════════════════════
# VULNERABILITY SCANNING
# ═══════════════════════════════════════════════════════════════
echo ""
echo "[*] === Vulnerability Scanning ==="
install_go nuclei "github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest"
install_git sqlmap "https://github.com/sqlmapproject/sqlmap.git" "sqlmap.py"

# ═══════════════════════════════════════════════════════════════
# PARAMETER DISCOVERY
# ═══════════════════════════════════════════════════════════════
echo ""
echo "[*] === Parameter Discovery ==="
install_go x8 "github.com/Sh1Yo/x8@latest"

# ═══════════════════════════════════════════════════════════════
# JS / SECRET DISCOVERY
# ═══════════════════════════════════════════════════════════════
echo ""
echo "[*] === JS & Secret Discovery ==="
install_go subjs "github.com/lc/subjs@latest"
install_go trufflehog "github.com/trufflesecurity/trufflehog/v3@latest"

# ═══════════════════════════════════════════════════════════════
# FINAL COPY & SYMLINK
# ═══════════════════════════════════════════════════════════════
echo ""
echo "[*] Copying all Go binaries to PATH..."
for bin in $HOME/go/bin/*; do
    [ -f "$bin" ] && cp -f "$bin" "$TOOLS_DIR/" 2>/dev/null
done

# Wordlists
echo "[*] Setting up wordlists..."
mkdir -p /usr/share/wordlists/dirb
[ ! -f /usr/share/wordlists/dirb/common.txt ] && \
    wget -q "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/common.txt" \
    -O /usr/share/wordlists/dirb/common.txt 2>/dev/null

# ═══════════════════════════════════════════════════════════════
# NUCLEI TEMPLATES
# ═══════════════════════════════════════════════════════════════
echo "[*] Updating nuclei templates..."
nuclei -ut 2>/dev/null || true

# ═══════════════════════════════════════════════════════════════
# VERIFICATION
# ═══════════════════════════════════════════════════════════════
echo ""
echo "============================================"
echo "         TOOL VERIFICATION"
echo "============================================"
ALL_TOOLS=(
    subfinder assetfinder amass findomain
    dnsx puredns asnmap hakrevdns
    httpx
    naabu nmap
    waybackurls gau katana gospider hakrawler
    ffuf gobuster nuclei kr
    arjun x8 paramspider
    subjs trufflehog
)

FOUND=0
MISSING_TOOLS=()
for tool in "${ALL_TOOLS[@]}"; do
    if command -v "$tool" &> /dev/null || [ -f "$TOOLS_DIR/$tool" ]; then
        echo "  [+] $tool"
        ((FOUND++))
    else
        echo "  [!] $tool MISSING"
        MISSING_TOOLS+=("$tool")
    fi
done

echo ""
echo "============================================"
echo "  Installed: $FOUND / ${#ALL_TOOLS[@]}"
echo "============================================"
if [ ${#MISSING_TOOLS[@]} -gt 0 ]; then
    echo "  Missing: ${MISSING_TOOLS[*]}"
fi
echo ""
echo "  Run: python3 bbf.py --target https://example.com"

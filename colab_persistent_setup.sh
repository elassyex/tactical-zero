#!/bin/bash
# ╔═══════════════════════════════════════════════════════════╗
# ║  TACTICAL ZERO - Colab Persistent Setup                  ║
# ║  Saves tools to Google Drive, restores on reconnect      ║
# ╚═══════════════════════════════════════════════════════════╝

DRIVE_DIR="/content/drive/MyDrive/tactical-zero"
TOOLS_MARKER="$DRIVE_DIR/.tools_installed"

echo "[*] TACTICAL ZERO - Persistent Setup"
echo "============================================"

# ── Mount Google Drive ───────────────────────────────────────
echo "[*] Mounting Google Drive..."
if [ ! -d "/content/drive/MyDrive" ]; then
    python3 -c "
from google.colab import drive
drive.mount('/content/drive')
" 2>/dev/null
fi

# ── Check if tools are already installed on Drive ────────────
if [ -f "$TOOLS_MARKER" ]; then
    echo "[+] Tools found on Google Drive - restoring..."
    
    # Restore binaries
    if [ -d "$DRIVE_DIR/bin" ]; then
        cp -f $DRIVE_DIR/bin/* /usr/local/bin/ 2>/dev/null
        chmod +x /usr/local/bin/* 2>/dev/null
    fi
    
    # Restore Go
    if [ -d "$DRIVE_DIR/go" ]; then
        cp -f $DRIVE_DIR/go/* $HOME/go/bin/ 2>/dev/null
    fi
    
    # Restore wordlists
    if [ -d "$DRIVE_DIR/wordlists" ]; then
        mkdir -p /usr/share/wordlists/dirb
        cp -rf $DRIVE_DIR/wordlists/* /usr/share/wordlists/ 2>/dev/null
    fi
    
    # Restore nuclei templates
    if [ -d "$DRIVE_DIR/nuclei-templates" ]; then
        mkdir -p ~/.local/nuclei-templates
        cp -rf $DRIVE_DIR/nuclei-templates/* ~/.local/ 2>/dev/null
    fi
    
    # Restore repo
    if [ ! -d "/content/tactical-zero" ]; then
        cp -rf $DRIVE_DIR/repo /content/tactical-zero 2>/dev/null
    fi
    
    echo "[+] Tools restored from Google Drive"
else
    echo "[*] First run - installing tools to Google Drive..."
    
    # ── System packages ──────────────────────────────────────
    apt-get update -qq
    apt-get install -y -qq python3-dev python3-pip wget curl git unzip tar whois dnsutils nmap jq
    
    # ── Go ───────────────────────────────────────────────────
    if ! command -v go &> /dev/null; then
        GO_VERSION="1.22.4"
        wget -q "https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz" -O /tmp/go.tar.gz
        tar -C /usr/local -xzf /tmp/go.tar.gz
        rm /tmp/go.tar.gz
    fi
    export PATH=/usr/local/go/bin:$HOME/go/bin:$PATH
    export GOPATH=$HOME/go
    mkdir -p $HOME/go/bin
    
    # ── Python deps ──────────────────────────────────────────
    pip install -q requests pyyaml ollama openai gitpython arjun paramspider jsleak waymore
    
    # ── Install all Go tools ─────────────────────────────────
    TOOLS_DIR="/usr/local/bin"
    
    go_tool() {
        local name=$1
        local pkg=$2
        echo -n "  [*] $name... "
        go install $pkg 2>/dev/null && cp -f $HOME/go/bin/$name $TOOLS_DIR/ 2>/dev/null && echo "[OK]" || echo "[SKIP]"
    }
    
    echo "[*] Installing subdomain tools..."
    go_tool subfinder "github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"
    go_tool assetfinder "github.com/tomnomnom/assetfinder@latest"
    go_tool amass "github.com/owasp-amass/amass/v4/cmd/amass@latest"
    wget -q "https://github.com/findomain/findomain/releases/latest/download/findomain-linux" -O $TOOLS_DIR/findomain && chmod +x $TOOLS_DIR/findomain
    
    echo "[*] Installing DNS tools..."
    go_tool dnsx "github.com/projectdiscovery/dnsx/cmd/dnsx@latest"
    go_tool puredns "github.com/d3mondev/puredns/v2@latest"
    go_tool asnmap "github.com/projectdiscovery/asnmap/cmd/asnmap@latest"
    go_tool hakrevdns "github.com/hakluke/hakrevdns@latest"
    
    echo "[*] Installing HTTP tools..."
    go_tool httpx "github.com/projectdiscovery/httpx/cmd/httpx@latest"
    go_tool naabu "github.com/projectdiscovery/naabu/v2/cmd/naabu@latest"
    
    echo "[*] Installing URL tools..."
    go_tool waybackurls "github.com/tomnomnom/waybackurls@latest"
    go_tool gau "github.com/lc/gau/v2/cmd/gau@latest"
    go_tool katana "github.com/projectdiscovery/katana/cmd/katana@latest"
    go_tool gospider "github.com/jaeles-project/gospider@latest"
    go_tool hakrawler "github.com/hakluke/hakrawler@latest"
    
    echo "[*] Installing fuzz tools..."
    go_tool ffuf "github.com/ffuf/ffuf/v2@latest"
    go_tool gobuster "github.com/OJ/gobuster/v3@latest"
    go_tool kiterunner "github.com/projectdiscovery/kiterunner/cmd/kr@latest"
    
    echo "[*] Installing vuln tools..."
    go_tool nuclei "github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest"
    go_tool subjs "github.com/lc/subjs@latest"
    go_tool trufflehog "github.com/trufflesecurity/trufflehog/v3@latest"
    go_tool x8 "github.com/Sh1Yo/x8@latest"
    
    # Git-based tools
    git clone -q https://github.com/sqlmapproject/sqlmap.git /opt/sqlmap 2>/dev/null
    ln -sf /opt/sqlmap/sqlmap.py $TOOLS_DIR/sqlmap
    
    # Wordlists
    mkdir -p /usr/share/wordlists/dirb
    wget -q "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/common.txt" \
        -O /usr/share/wordlists/dirb/common.txt 2>/dev/null
    
    # Nuclei templates
    nuclei -ut 2>/dev/null || true
    
    # Copy all Go binaries
    for bin in $HOME/go/bin/*; do
        [ -f "$bin" ] && cp -f "$bin" "$TOOLS_DIR/" 2>/dev/null
    done
    
    # ── Save to Google Drive ─────────────────────────────────
    echo "[*] Saving tools to Google Drive..."
    mkdir -p $DRIVE_DIR/bin
    mkdir -p $DRIVE_DIR/go
    mkdir -p $DRIVE_DIR/wordlists
    mkdir -p $DRIVE_DIR/nuclei-templates
    mkdir -p $DRIVE_DIR/repo
    
    # Save binaries
    for tool in subfinder assetfinder amass findomain dnsx puredns asnmap hakrevdns \
                httpx naabu waybackurls gau katana gospider hakrawler \
                ffuf gobuster kiterunner nuclei subjs trufflehog x8 kr sqlmap dirsearch; do
        [ -f "$TOOLS_DIR/$tool" ] && cp -f "$TOOLS_DIR/$tool" $DRIVE_DIR/bin/ 2>/dev/null
    done
    
    # Save Go binaries
    cp -f $HOME/go/bin/* $DRIVE_DIR/go/ 2>/dev/null
    
    # Save wordlists
    cp -rf /usr/share/wordlists/* $DRIVE_DIR/wordlists/ 2>/dev/null
    
    # Save nuclei templates
    cp -rf ~/.local/nuclei-templates/* $DRIVE_DIR/nuclei-templates/ 2>/dev/null
    
    # Save repo
    cp -rf /content/tactical-zero $DRIVE_DIR/repo/ 2>/dev/null
    
    # Mark as installed
    date > $TOOLS_MARKER
    
    echo "[+] Tools saved to Google Drive"
fi

echo ""
echo "============================================"
echo "  Setup complete!"
echo "============================================"

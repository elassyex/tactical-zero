#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/.venv"

echo "[*] Installing TACTICAL ZERO dependencies..."

# Check if deps are already available
check_deps() {
    python3 -c "import requests, yaml, ollama, openai" 2>/dev/null
}

if check_deps; then
    echo "[+] Python dependencies already available system-wide. Skipping venv."
else
    echo "[*] Creating virtual environment..."
    python3 -m venv "${VENV_DIR}"
    source "${VENV_DIR}/bin/activate"
    pip install -U pip
    pip install -r "${SCRIPT_DIR}/requirements.txt"
    echo "[+] Virtual environment created at ${VENV_DIR}"
    echo "    To use it: source ${VENV_DIR}/bin/activate"
fi

echo "[*] Checking required external tools..."
for tool in subfinder assetfinder httpx naabu nuclei waybackurls gau katana ffuf amass findomain; do
    if command -v "$tool" &> /dev/null; then
        echo "  [+] $tool found"
    else
        echo "  [!] $tool NOT FOUND - install via 'go install ...' or package manager"
    fi
done

echo "[+] Setup complete."
echo "    Quick start: python3 ${SCRIPT_DIR}/bbf_unified.py --target https://example.com"

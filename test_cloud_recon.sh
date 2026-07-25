#!/bin/bash

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║   CLOUD RECON TEST SCRIPT                                    ║"
echo "║   Test your cloud environment before full recon              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if running in cloud
if [[ -f "/content" ]]; then
  echo "🚀 Running in Google Colab"
  ENVIRONMENT="colab"
elif [[ -d "/workspace" ]]; then
  echo "🚀 Running in GitHub Codespaces"
  ENVIRONMENT="codespaces"
elif [[ -f "/proc/1/cgroup" ]]; then
  echo "🚀 Running in AWS Lambda"
  ENVIRONMENT="lambda"
elif [[ -f "/railway" ]]; then
  echo "🚀 Running in Railway.app"
  ENVIRONMENT="railway"
else
  echo "⚠️  Running in local environment"
  ENVIRONMENT="local"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 TEST 1: Check Python version"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 --version

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 TEST 2: Check pip"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
pip3 --version

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 TEST 3: Check bug bounty tools"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

tools=("subfinder" "assetfinder" "httpx" "naabu" "nuclei" "waybackurls" "gau" "katana" "ffuf" "amass" "findomain")
missing_tools=0

for tool in "${tools[@]}"; do
  if command -v $tool &> /dev/null; then
    version=$($tool --version 2>&1 | head -1)
    echo "  ✅ $tool: $version"
  else
    echo "  ❌ $tool: NOT INSTALLED"
    ((missing_tools++))
  fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 TEST 4: Check Python packages"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python_packages=("ollama" "openai" "httpx" "pandas" "numpy" "transformers" "torch" "requests" "yaml" "sqlalchemy" "pydantic")
missing_packages=0

for pkg in "${python_packages[@]}"; do
  if python3 -c "import $pkg" 2>&1; then
    echo "  ✅ $pkg"
  else
    echo "  ❌ $pkg: NOT INSTALLED"
    ((missing_packages++))
  fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 TEST 5: Test subfinder"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if command -v subfinder &> /dev/null; then
  echo "  Testing subfinder on ory.com..."
  timeout 60 subfinder -d ory.com -silent -timeout 30 | head -5
  if [ $? -eq 0 ]; then
    echo "  ✅ Subfinder working!"
  else
    echo "  ⚠️  Subfinder timed out or failed"
  fi
else
  echo "  ❌ Subfinder not installed"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 TEST 6: Test httpx"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if command -v httpx &> /dev/null; then
  echo "  Testing httpx..."
  timeout 60 httpx -u https://ory.com -silent -title -status-code -timeout 30 | head -3
  if [ $? -eq 0 ]; then
    echo "  ✅ Httpx working!"
  else
    echo "  ⚠️  Httpx timed out or failed"
  fi
else
  echo "  ❌ Httpx not installed"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 TEST 7: Test nuclei"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if command -v nuclei &> /dev/null; then
  echo "  Testing nuclei..."
  timeout 120 nuclei -u https://ory.com -severity critical -timeout 30 | head -3
  if [ $? -eq 0 ]; then
    echo "  ✅ Nuclei working!"
  else
    echo "  ⚠️  Nuclei timed out or failed"
  fi
else
  echo "  ❌ Nuclei not installed"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 TEST SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Environment: $ENVIRONMENT"
echo "  Tools installed: $(( ${#tools[@]} - missing_tools ))/${#tools[@]}"
echo "  Packages installed: $(( ${#python_packages[@]} - missing_packages ))/${#python_packages[@]}"
echo "  Missing tools: $missing_tools"
echo "  Missing packages: $missing_packages"
echo ""

if [ $missing_tools -gt 0 ]; then
  echo "⚠️  Install missing tools:"
  echo "  apt-get install -y subfinder assetfinder httpx naabu nuclei waybackurls gau katana ffuf amass findomain"
fi

if [ $missing_packages -gt 0 ]; then
  echo "⚠️  Install missing packages:"
  echo "  pip3 install -r requirements.txt"
fi

echo ""
echo "✅ TEST COMPLETE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

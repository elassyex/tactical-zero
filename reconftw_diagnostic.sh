#!/bin/bash
echo "🔍 RECONFTW DIAGNOSTIC"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "1️⃣  Checking reconftw version..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
!cd /content/reconftw && ./reconftw.sh -v 2>&1
echo ""

echo "2️⃣  Checking help (first 150 lines)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
!cd /content/reconftw && ./reconftw.sh -h 2>&1 | head -150
echo ""

echo "3️⃣  Checking for subbrute in help..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
!cd /content/reconftw && ./reconftw.sh -h 2>&1 | grep -i "subbrute"
echo ""

echo "4️⃣  Checking for output in help..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
!cd /content/reconftw && ./reconftw.sh -h 2>&1 | grep -i "output"
echo ""

echo "5️⃣  Listing config files..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
!find /content/reconftw -maxdepth 3 -name "*config*" -type f 2>/dev/null
echo ""

echo "6️⃣  Checking config.d directory..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -d "/content/reconftw/config.d" ]; then
    echo "Config.d exists:"
    !ls -la /content/reconftw/config.d/
    echo ""
    echo "Subbrute config:"
    !ls -la /content/reconftw/config.d/*subbrute* 2>/dev/null || echo "No subbrute config found"
else
    echo "No config.d directory"
fi
echo ""

echo "7️⃣  Checking main config file..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f "/content/reconftw/config.conf" ]; then
    echo "Config file exists"
    echo "First 50 lines:"
    !head -50 /content/reconftw/config.conf
    echo ""
    echo "Subbrute setting:"
    !grep -i "subbrute" /content/reconftw/config.conf 2>/dev/null || echo "No subbrute found"
else
    echo "No config.conf found"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 RECOMMENDED COMMANDS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Basic recon:"
echo "  !cd /content/reconftw && ./reconftw.sh -d ory.com -r --ai"
echo ""
echo "Alternative:"
echo "  !cd /content/reconftw && ./reconftw.sh ory.com -r --ai"
echo ""
echo "To disable subbrute:"
echo "  1. Download config: files.download('/content/reconftw/config.conf')"
echo "  2. Edit file locally"
echo "  3. Upload back: !cp /content/config.conf /content/reconftw/config.conf"
echo ""

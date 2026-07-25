#!/bin/bash
echo "🔍 RECONFTW CONFIG DIAGNOSTIC"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "1️⃣  Checking for config files in reconftw directory..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# List all config files
echo ""
echo "Config files found:"
!find /content/reconftw -maxdepth 2 -name "*config*" -type f 2>/dev/null | sort

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  Checking config file locations..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check main config locations
for loc in "/content/reconftw/config.conf" "/content/reconftw/config" "/content/reconftw/.config" "/content/reconftw/conf" "/content/reconftw/settings.conf" "/content/reconftw/config.json"; do
    if [ -f "$loc" ]; then
        echo "✅ Found: $loc"
        echo ""
        echo "File content:"
        cat "$loc" 2>/dev/null | head -20
        echo ""
    else
        echo "❌ Not found: $loc"
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  Checking for config.d directory..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -d "/content/reconftw/config.d" ]; then
    echo "✅ Found config.d directory"
    echo ""
    echo "Config.d contents:"
    ls -la /content/reconftw/config.d/
    echo ""
    
    # Check for subbrute config
    if [ -f "/content/reconftw/config.d/subbrute.conf" ]; then
        echo "✅ Found subbrute.conf"
        cat /content/reconftw/config.d/subbrute.conf 2>/dev/null
        echo ""
    else
        echo "❌ No subbrute.conf found"
    fi
else
    echo "❌ No config.d directory found"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  Checking subbrute setting in main config..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "/content/reconftw/config.conf" ]; then
    echo "Checking /content/reconftw/config.conf:"
    echo ""
    
    # Check for subbrute
    if grep -q "subbrute" /content/reconftw/config.conf; then
        echo "✅ Found subbrute setting:"
        grep "subbrute" /content/reconftw/config.conf
        echo ""
    else
        echo "❌ No subbrute setting found in config.conf"
        echo ""
    fi
    
    # Show first 30 lines
    echo "First 30 lines of config.conf:"
    head -30 /content/reconftw/config.conf
    echo ""
else
    echo "❌ No config.conf found"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5️⃣  Checking alternative config locations..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check common config locations
for loc in "/root/.config/reconftw.conf" "/root/reconftw.conf" "/root/.reconftw/config" "/root/reconftw/config" "/home/reconftw/config.conf"; do
    if [ -f "$loc" ]; then
        echo "✅ Found alternative: $loc"
        grep "subbrute" "$loc" 2>/dev/null
        echo ""
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6️⃣  Checking reconftw version and help..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "reconftw version:"
!cd /content/reconftw && ./reconftw.sh -v 2>&1 | head -5
echo ""

echo "reconftw help - config section:"
!cd /content/reconftw && ./reconftw.sh -h 2>&1 | grep -A 10 -i "config" | head -30
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 NEXT STEPS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "If subbrute is still running:"
echo "1. Use --no-subbrute flag in command"
echo "2. Edit the correct config file in /content/reconftw/"
echo "3. Make sure config file format is correct (key=value)"
echo "4. Add --config /content/reconftw/config.conf to command"
echo ""

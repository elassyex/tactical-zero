#!/bin/bash
# Test script for Ory.com custom nuclei templates

echo "=== ORY.COM CUSTOM NUCLEI TEMPLATE TESTING ==="
echo "Date: $(date)"
echo "Target: https://ory.com"
echo ""

cd /Users/mac/bugbounty_framework/hunts/ory.com_20260720

echo "📊 RUNNING CUSTOM NUCLEI TEMPLATES..."
echo ""

# Run all custom templates
echo "1. Testing SSRF templates..."
nuclei -u https://ory.com -t custom_nuclei_templates/http/custom/ory-ssrf.yaml -severity high,critical -silent -o results/ssrf.txt
echo "   Results: $(wc -l < results/ssrf.txt) findings"

echo ""
echo "2. Testing IDOR templates..."
nuclei -u https://ory.com -t custom_nuclei_templates/http/custom/ory-idor.yaml -severity high,critical -silent -o results/idor.txt
echo "   Results: $(wc -l < results/idor.txt) findings"

echo ""
echo "3. Testing JWT templates..."
nuclei -u https://ory.com -t custom_nuclei_templates/http/custom/ory-jwt-exploit.yaml -severity critical -silent -o results/jwt.txt
echo "   Results: $(wc -l < results/jwt.txt) findings"

echo ""
echo "4. Testing OAuth2 templates..."
nuclei -u https://ory.com -t custom_nuclei_templates/http/custom/ory-oauth.yaml -severity high,critical -silent -o results/oauth.txt
echo "   Results: $(wc -l < results/oauth.txt) findings"

echo ""
echo "5. Testing Misconfiguration templates..."
nuclei -u https://ory.com -t custom_nuclei_templates/http/custom/ory-misconfig.yaml -severity high,critical -silent -o results/misconfig.txt
echo "   Results: $(wc -l < results/misconfig.txt) findings"

echo ""
echo "6. Testing CORS templates..."
nuclei -u https://ory.com -t custom_nuclei_templates/http/custom/ory-cors.yaml -severity medium,high -silent -o results/cors.txt
echo "   Results: $(wc -l < results/cors.txt) findings"

echo ""
echo "7. Testing Auth Bypass templates..."
nuclei -u https://ory.com -t custom_nuclei_templates/http/custom/ory-auth-bypass.yaml -severity critical,high -silent -o results/auth-bypass.txt
echo "   Results: $(wc -l < results/auth-bypass.txt) findings"

echo ""
echo "━"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "📊 SUMMARY:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Total custom templates tested: 7"
echo ""
echo "Findings by category:"
echo "  • SSRF: $(wc -l < results/ssrf.txt) findings"
echo "  • IDOR: $(wc -l < results/idor.txt) findings"
echo "  • JWT: $(wc -l < results/jwt.txt) findings"
echo "  • OAuth2: $(wc -l < results/oauth.txt) findings"
echo "  • Misconfig: $(wc -l < results/misconfig.txt) findings"
echo "  • CORS: $(wc -l < results/cors.txt) findings"
echo "  • Auth Bypass: $(wc -l < results/auth-bypass.txt) findings"
echo ""
echo "Total vulnerabilities found: $(cat results/*.txt 2>/dev/null | wc -l)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Testing complete!"

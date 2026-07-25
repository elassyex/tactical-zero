"""
Zero-Day & Complex Logic Vulnerability Detection Heuristics
Identifies anomalies, logic flaws, and hints of unknown vulnerabilities.
"""
import json, re
from typing import Dict, List, Optional, Any
from pathlib import Path
import hashlib


class ZeroDayHeuristics:
    """
    Advanced heuristics engine for detecting zero-day indicators and 
    complex logic vulnerabilities that automated scanners miss.
    """

    def __init__(self, workspace, ai_brain=None):
        self.workspace = workspace
        self.ai = ai_brain
        self.anomalies: List[Dict] = []
        self.logic_indicators: List[Dict] = []

    def analyze_response_patterns(self, urls: List[str]) -> List[Dict]:
        """Analyze HTTP response patterns for anomalies."""
        findings = []
        from urllib.parse import urlparse
        import subprocess, shlex

        def curl_cmd(url):
            return f"curl -sk -I -w '\\nHTTP_CODE:%{{http_code}}\\nSIZE:%{{size_download}}\\nTIME:%{{time_total}}\\n' '{url}' --max-time 15 2>/dev/null"

        # Baseline: get normal response for root path
        baseline = {}
        for url in urls[:5]:
            resp = subprocess.run(curl_cmd(url), shell=True, capture_output=True, text=True).stdout
            baseline[url] = self._parse_response(resp)

        # Check each endpoint
        checked = set()
        for url in urls:
            if len(checked) >= 200:
                break
            checked.add(url)
            resp = subprocess.run(curl_cmd(url), shell=True, capture_output=True, text=True).stdout
            parsed = self._parse_response(resp)

            anomaly = self._detect_anomaly(url, parsed, baseline)
            if anomaly:
                findings.append(anomaly)

        self.anomalies.extend(findings)
        return findings

    def _parse_response(self, resp: str) -> Dict:
        headers = {}
        code = ""
        size = "0"
        for line in resp.splitlines():
            if line.startswith("HTTP_CODE:"):
                code = line.replace("HTTP_CODE:", "").strip()
            elif line.startswith("SIZE:"):
                size = line.replace("SIZE:", "").strip()
            elif ":" in line:
                parts = line.split(":", 1)
                headers[parts[0].strip().lower()] = parts[1].strip()
        return {"code": code, "size": size, "headers": headers}

    def _detect_anomaly(self, url: str, parsed: Dict, baseline: Dict) -> Optional[Dict]:
        anomalies = []

        # Anomaly 1: Unexpected success on admin/internal paths
        url_lower = url.lower()
        if any(k in url_lower for k in ["admin", "internal", "debug", "test", "staging", "dev", "api/v", "graphql"]) and parsed["code"] == "200":
            anomalies.append({"type": "exposed_sensitive_path", "detail": f"{url} returns 200 OK"})

        # Anomaly 2: Abnormally large response for simple endpoint
        try:
            if int(parsed["size"]) > 100000 and not any(ext in url for ext in [".js", ".css", ".png", ".jpg", ".pdf"]):
                anomalies.append({"type": "abnormal_response_size", "detail": f"Size: {parsed['size']} bytes"})
        except ValueError:
            pass

        # Anomaly 3: Missing security headers on auth endpoints
        if any(k in url_lower for k in ["login", "auth", "oauth", "signin", "api"]):
            sec_headers = ["x-frame-options", "content-security-policy", "x-content-type-options", "strict-transport-security"]
            missing = [h for h in sec_headers if h not in parsed["headers"]]
            if len(missing) >= 3:
                anomalies.append({"type": "missing_security_headers", "detail": f"Missing: {', '.join(missing)}"})

        # Anomaly 4: Cookie without secure/httponly flags
        cookies = parsed["headers"].get("set-cookie", "")
        if cookies:
            if "secure" not in cookies.lower() or "httponly" not in cookies.lower():
                anomalies.append({"type": "insecure_cookie", "detail": cookies[:100]})

        # Anomaly 5: Server header revealing version
        server = parsed["headers"].get("server", "")
        if server and any(c.isdigit() for c in server):
            anomalies.append({"type": "server_version_disclosure", "detail": server})

        # Anomaly 6: CORS misconfiguration
        cors = parsed["headers"].get("access-control-allow-origin", "")
        if cors == "*" and any(k in url_lower for k in ["api", "auth", "user", "account"]):
            anomalies.append({"type": "wildcard_cors", "detail": f"CORS: {cors}"})

        if anomalies:
            return {
                "url": url,
                "code": parsed["code"],
                "anomalies": anomalies,
                "severity": "medium" if any(a["type"] in ("exposed_sensitive_path", "wildcard_cors") for a in anomalies) else "low",
            }
        return None

    def analyze_parameters_for_logic_flaws(self, param_file: str) -> List[Dict]:
        """Identify parameter structures that suggest logic flaws."""
        findings = []
        if not Path(param_file).exists():
            return findings

        params = set()
        for line in Path(param_file).read_text().splitlines():
            line = line.strip()
            if "=" in line:
                for p in line.split("&"):
                    if "=" in p:
                        params.add(p.split("=")[0].lower())

        # Logic flaw parameter patterns
        logic_patterns = {
            "price_manipulation": ["price", "cost", "amount", "total", "subtotal", "discount", "coupon_value"],
            "quantity_manipulation": ["qty", "quantity", "count", "limit", "max", "min", "items"],
            "role_escalation": ["role", "privilege", "permission", "level", "type", "group", "is_admin", "is_staff"],
            "id_manipulation": ["id", "uid", "user_id", "order_id", "account_id", "ref_id", "transaction_id"],
            "state_manipulation": ["status", "state", "active", "enabled", "verified", "approved", "published"],
            "rate_bypass": ["limit", "offset", "page", "per_page", "max_results", "batch_size"],
            "negative_testing": ["credit", "balance", "points", "reward", "cashback", "refund"],
        }

        for flaw_type, indicators in logic_patterns.items():
            matched = [p for p in params if any(ind in p for ind in indicators)]
            if matched:
                findings.append({
                    "type": "logic_flaw_indicator",
                    "flaw_type": flaw_type,
                    "parameters": matched,
                    "severity": "medium",
                    "description": f"Parameters suggest potential {flaw_type.replace('_', ' ')}",
                })

        self.logic_indicators.extend(findings)
        return findings

    def analyze_javascript_for_anti_patterns(self, js_dir: str) -> List[Dict]:
        """Detect dangerous patterns in JavaScript files."""
        findings = []
        js_path = Path(js_dir)
        if not js_path.exists():
            return findings

        dangerous_patterns = {
            "hardcoded_secrets": re.compile(r'(?i)(api[_-]?key|secret|password|token|auth)\s*[:=]\s*["\'][^"\']{8,}["\']'),
            "dangerous_eval": re.compile(r'(?i)(eval\s*\(|new\s+Function\s*\(|setTimeout\s*\(["\'])'),
            "disabled_security": re.compile(r'(?i)(verify\s*=\s*false|rejectUnauthorized\s*=\s*false|strictSSL\s*=\s*false)'),
            "debug_endpoints": re.compile(r'(?i)(/debug|/test|/internal|/admin|/dev|/staging|localhost|127\.0\.0\.1)'),
            "sensitive_apis": re.compile(r'(?i)(fetch\s*\(\s*["\'].*?/(api/|graphql|gql|rest/|v\d+/))'),
            "postMessage_handler": re.compile(r'(?i)(window\.addEventListener\s*\(\s*["\']message["\'])'),
            "prototype_pollution": re.compile(r'(?i)(Object\.assign|\.extend\s*\(|\.merge\s*\()'),
        }

        for js_file in js_path.rglob("*.txt"):
            content = js_file.read_text(errors="ignore")
            for pattern_name, pattern in dangerous_patterns.items():
                matches = pattern.findall(content)
                if matches:
                    # Deduplicate
                    unique = list(set(matches))[:5]
                    findings.append({
                        "type": "js_anti_pattern",
                        "pattern": pattern_name,
                        "file": str(js_file),
                        "matches": unique,
                        "severity": "high" if pattern_name in ("hardcoded_secrets", "dangerous_eval") else "medium",
                    })

        return findings

    def detect_inconsistent_access_control(self, alive_file: str, urls_file: str) -> List[Dict]:
        """Find endpoints that behave inconsistently suggesting access control issues."""
        findings = []
        if not Path(alive_file).exists() or not Path(urls_file).exists():
            return findings

        import subprocess, shlex

        # Test endpoints with and without auth-like headers
        test_endpoints = []
        for line in Path(urls_file).read_text().splitlines():
            line = line.strip()
            if any(k in line.lower() for k in ["api", "user", "account", "order", "admin", "internal"]):
                test_endpoints.append(line)

        tested = set()
        for endpoint in test_endpoints[:50]:
            if endpoint in tested:
                continue
            tested.add(endpoint)

            # Request 1: Normal
            r1 = subprocess.run(
                f"curl -sk -o /dev/null -w '%{{http_code}}:%{{size_download}}' '{endpoint}' --max-time 10 2>/dev/null",
                shell=True, capture_output=True, text=True
            ).stdout.strip()

            # Request 2: With Authorization header (fuzz)
            r2 = subprocess.run(
                f"curl -sk -H 'Authorization: Bearer abc123' -o /dev/null -w '%{{http_code}}:%{{size_download}}' '{endpoint}' --max-time 10 2>/dev/null",
                shell=True, capture_output=True, text=True
            ).stdout.strip()

            if r1 != r2 and "200" in (r1.split(":")[0] if ":" in r1 else r1):
                findings.append({
                    "type": "inconsistent_access_control",
                    "endpoint": endpoint,
                    "without_auth": r1,
                    "with_auth": r2,
                    "severity": "medium",
                })

        return findings

    def analyze_tech_stack_versions(self, nmap_file: str, nuclei_tech_file: str) -> List[Dict]:
        """Identify potentially vulnerable technology versions."""
        findings = []
        tech_versions = []

        if Path(nmap_file).exists():
            for line in Path(nmap_file).read_text().splitlines():
                if "/" in line and any(c.isdigit() for c in line):
                    tech_versions.append(line.strip())

        if Path(nuclei_tech_file).exists():
            for line in Path(nuclei_tech_file).read_text().splitlines():
                if "[" in line and "]" in line:
                    tech_versions.append(line.strip())

        # Known vulnerable version patterns
        vuln_patterns = [
            (r"(?i)apache/2\.4\.(4[0-9]|5[0-8])", "Apache 2.4.x - Check for known CVEs"),
            (r"(?i)nginx/1\.(1[0-9]|2[0-3])", "Nginx 1.x - Check for known CVEs"),
            (r"(?i)php/7\.[0-4]", "PHP 7.x EOL - Known vulnerabilities"),
            (r"(?i)php/5\.", "PHP 5.x EOL - Critical vulnerabilities"),
            (r"(?i)jquery\s+1\.[0-9]", "jQuery 1.x - Known XSS CVEs"),
            (r"(?i)wordpress\s+5\.[0-8]", "WordPress 5.x - Check for known CVEs"),
            (r"(?i)drupal\s+7|drupal\s+8\.[0-8]", "Drupal - Check for SA-CORE vulnerabilities"),
            (r"(?i)node\.js\s+(10|12|14|16)\.", "Node.js EOL versions"),
            (r"(?i)python\s+2\.", "Python 2 EOL - Security issues"),
            (r"(?i)tomcat\s+8|tomcat\s+9\.[0-3]", "Apache Tomcat - Check CVEs"),
        ]

        for tech in tech_versions:
            for pattern, description in vuln_patterns:
                if re.search(pattern, tech):
                    findings.append({
                        "type": "outdated_technology",
                        "technology": tech,
                        "description": description,
                        "severity": "medium",
                    })

        return findings

    def generate_recon_synopsis(self) -> Dict[str, Any]:
        """Generate a comprehensive synopsis for AI analysis."""
        return {
            "anomalies": self.anomalies,
            "logic_indicators": self.logic_indicators,
            "total_anomalies": len(self.anomalies),
            "total_logic_indicators": len(self.logic_indicators),
            "zero_day_hints": self._compile_zero_day_hints(),
            "tech_stack_summary": self._extract_tech_stack(),
        }

    def _compile_zero_day_hints(self) -> List[Dict]:
        hints = []
        for a in self.anomalies:
            for anom in a.get("anomalies", []):
                if anom["type"] in ("exposed_sensitive_path", "inconsistent_access_control"):
                    hints.append({
                        "type": anom["type"],
                        "url": a.get("url", ""),
                        "confidence": "medium",
                        "indicators": [anom["detail"]],
                    })
        for li in self.logic_indicators:
            hints.append({
                "type": "logic_flaw",
                "flaw_type": li.get("flaw_type"),
                "parameters": li.get("parameters", []),
                "confidence": "medium",
                "indicators": li.get("parameters", []),
            })
        return hints

    def _extract_tech_stack(self) -> List[str]:
        stack = set()
        for a in self.anomalies:
            for anom in a.get("anomalies", []):
                if anom["type"] == "server_version_disclosure":
                    stack.add(anom["detail"])
        return sorted(stack)

    def run_all_heuristics(self, alive_file: str, urls_file: str, param_file: str, js_dir: str, nmap_file: str, nuclei_tech_file: str) -> Dict[str, List[Dict]]:
        """Execute all heuristic analysis phases."""
        results = {}

        if Path(urls_file).exists():
            urls = [l.strip() for l in Path(urls_file).read_text().splitlines() if l.strip()][:200]
            results["response_patterns"] = self.analyze_response_patterns(urls)

        if Path(param_file).exists():
            results["logic_flaws"] = self.analyze_parameters_for_logic_flaws(param_file)

        if Path(js_dir).exists():
            results["js_anti_patterns"] = self.analyze_javascript_for_anti_patterns(js_dir)

        results["access_control"] = self.detect_inconsistent_access_control(alive_file, urls_file)
        results["outdated_tech"] = self.analyze_tech_stack_versions(nmap_file, nuclei_tech_file)

        # Save findings
        for category, findings in results.items():
            for finding in findings:
                self.workspace.add_finding(finding)

        self.workspace.write_json("vulns/heuristic_findings.json", results)
        return results

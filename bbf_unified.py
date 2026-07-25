#!/usr/bin/env python3
"""
TACTICAL ZERO Unified Hunter - Single file entry point
"""
import sys, os, re, shlex, shutil, subprocess, time, argparse
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from framework.core.config import FrameworkConfig
from framework.core.workspace import WorkspaceManager
from framework.core.feedback import FeedbackLoop
from framework.ai.brain import AIBrain
from framework.adapters.intel import ThreatIntelAggregator
from framework.agents.scanner import DynamicScanner
from framework.agents.heuristics import ZeroDayHeuristics


def banner():
    print("""
\033[1;32m╔═══════════════════════════════════════════════════════════════╗
║   TACTICAL ZERO v3.0 - AUTONOMOUS BUG BOUNTY FRAMEWORK      ║
║   Intelligence-Driven | AI-Augmented | Adaptive             ║
╚═══════════════════════════════════════════════════════════════╝\033[0m
""")
def info(msg): print(f"\033[1;34m[*]\033[0m {msg}")
def success(msg): print(f"\033[1;32m[+]\033[0m {msg}")
def warn(msg): print(f"\033[1;33m[!]\033[0m {msg}")
def section(title):
    print(f"\n\033[1;36m{'─'*60}\033[0m")
    print(f"\033[1;33m  {title}\033[0m")
    print(f"\033[1;36m{'─'*60}\033[0m")

def run_cmd(cmd, timeout=120, silent=False):
    if not silent: info(f"Running: {cmd[:120]}...")
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return (r.stdout or "").strip()
    except Exception as e:
        warn(str(e))
        return ""

def tool_exists(tool): return shutil.which(tool) is not None
def write_file(path, content):
    p = Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(str(content) or "", errors="ignore")
def count_lines(path):
    try:
        p = Path(path)
        if not p.exists(): return 0
        return len(p.read_text(errors="ignore").splitlines())
    except: return 0
def write_lines(path, items):
    items = [str(x).strip() for x in items if str(x).strip()]
    write_file(path, "\n".join(items) + ("\n" if items else ""))
def merge_text_files(folder, output):
    lines = set()
    for p in Path(folder).rglob("*.txt"):
        try:
            for line in p.read_text(errors="ignore").splitlines():
                if line.strip(): lines.add(line.strip())
        except: pass
    write_lines(output, sorted(lines))
def normalize_hosts_file(src_file, dst_file):
    hosts = set()
    src = Path(src_file)
    if src.exists():
        for line in src.read_text(errors="ignore").splitlines():
            line = line.strip().split("/")[0].split(":")[0].lower()
            if line and "." in line: hosts.add(line)
    write_lines(dst_file, sorted(hosts))
def normalize_urls_file(src_file, dst_file):
    urls = set()
    src = Path(src_file)
    if src.exists():
        for line in src.read_text(errors="ignore").splitlines():
            line = line.strip()
            if line.startswith(("http://", "https://")): urls.add(line)
    write_lines(dst_file, sorted(urls))

class UnifiedHuntOrchestrator:
    def __init__(self, args):
        self.args = args
        self.domain = args.domain
        self.target = args.target
        self.ws = WorkspaceManager(args.output, self.domain)
        self.ws.init()

        class FakeArgs:
            pass
        fa = FakeArgs()
        fa.target = args.target
        fa.shodan_api_key = args.shodan_api_key or os.getenv("SHODAN_API_KEY","")
        fa.vt_api_key = args.vt_api_key or os.getenv("VT_API_KEY","")
        fa.nuclei_templates = "~/.local/nuclei-templates"
        fa.model = args.model
        fa.ollama_host = args.ollama_host
        fa.openai_api_key = os.getenv("OPENAI_API_KEY","")
        fa.skip_slow = args.skip_slow
        fa.mode = "full"
        fa.focus = "all"
        fa.output = args.output
        fa.max_subdomains = 0
        fa.threads = 50
        fa.learn_from = args.learn_from or ""
        fa.config = "config/config.yaml"
        self.config = FrameworkConfig.from_args(fa)

        self.ai = AIBrain(self.config, self.ws)
        self.intel = ThreatIntelAggregator(self.config.shodan_api_key, self.config.vt_api_key)
        self.scanner = DynamicScanner(self.config, self.ws, self.ai)
        self.feedback = FeedbackLoop(self.ws, self.config, self.ai)
        self.heuristics = ZeroDayHeuristics(self.ws, self.ai)

    def _detect_tech_stack(self):
        stack = []
        # Direct probe: fetch HTTP headers from target
        try:
            import subprocess as sp
            r = sp.run(
                f"curl -sk -I {self.target} --max-time 10 2>/dev/null",
                shell=True, capture_output=True, text=True, timeout=15
            )
            headers = (r.stdout or "").lower()
            for t, sig in [("Apache","apache"), ("nginx","nginx"), ("IIS","iis"), ("PHP","php"),
                           ("Express","express"), ("Next.js","next"), ("Django","django"),
                           ("Flask","flask"), ("Spring","spring"), ("Tomcat","tomcat"),
                           ("WordPress","wordpress"), ("Drupal","drupal"), ("Joomla","joomla")]:
                if sig in headers:
                    stack.append(t)
        except Exception:
            pass

        # Direct probe: check common tech endpoints
        try:
            import subprocess as sp
            for path, tech in [("/swagger-ui.html","swagger"),("/swagger.json","swagger"),
                               ("/actuator","actuator"),("/api/v1","api"),
                               ("/graphql","graphql"),("/admin","admin"),
                               ("/login","auth")]:
                r = sp.run(
                    f"curl -sk -o /dev/null -w '%{{http_code}}' {self.target}{path} --max-time 5 2>/dev/null",
                    shell=True, capture_output=True, text=True, timeout=8
                )
                code = (r.stdout or "").strip()
                if code and code != "000" and code != "404":
                    stack.append(tech)
        except Exception:
            pass

        nmap_file = self.ws.path("ports/nmap.txt")
        if nmap_file.exists():
            txt = nmap_file.read_text(errors="ignore")
            for t in ["Apache","nginx","IIS","Node.js","Express","Next.js","Django","Flask","Spring","Tomcat","PHP","WordPress"]:
                if t.lower() in txt.lower(): stack.append(t)
        ntech = self.ws.path("vulns/nuclei_tech.txt")
        if ntech.exists():
            txt = ntech.read_text(errors="ignore")
            for t in ["grafana","kibana","jenkins","prometheus","swagger","actuator"]:
                if t.lower() in txt.lower(): stack.append(t)
        return list(set(stack))

    def _detect_api_patterns(self):
        api_file = self.ws.path("urls/api.txt")
        if not api_file.exists(): return []
        urls = api_file.read_text(errors="ignore").splitlines()
        patterns = []
        for url in urls[:20]:
            if "/api/v" in url:
                patterns.append({"id": "api_{}".format(len(patterns)), "path": "/api/v1/FUZZ", "method": "GET", "indicator": "api"})
            elif "graphql" in url.lower():
                patterns.append({"id": "graphql_{}".format(len(patterns)), "path": "/graphql", "method": "POST", "indicator": "graphql"})
        return patterns

    def _load_recon_text(self):
        parts = []
        for key, path in [
            ("subdomains", "subs/all_hosts.txt"),
            ("urls", "urls/all_urls_clean.txt"),
            ("ports", "ports/naabu_top1000.txt"),
            ("nuclei", "vulns/nuclei_main.txt"),
            ("cves", "vulns/nuclei_cves.txt"),
            ("admin", "urls/admin.txt"),
            ("auth", "urls/auth.txt"),
            ("api", "urls/api.txt"),
            ("sensitive", "urls/sensitive.txt"),
            ("ssrf", "urls/ssrf.txt"),
            ("sqli", "urls/sqli.txt"),
            ("xss", "urls/xss.txt"),
            ("js_secrets", "js/regex_secrets.txt"),
            ("dirs", "dirs/feroxbuster.txt"),
            ("params", "params/arjun_main.json"),
        ]:
            p = self.ws.path(path)
            if p.exists():
                lines = p.read_text(errors="ignore").splitlines()[:30]
                parts.append("\n=== {} ===\n".format(key.upper()) + "\n".join(lines))
        return "\n".join(parts)

    def _generate_final_report(self):
        recon_text = self._load_recon_text()[:12000]
        ai_analysis = self.ai.analyze_recon(self.target, recon_text)
        report = "# Bug Bounty Report: {}\n\nGenerated: {}\n\n## AI Analysis\n\n{}\n".format(
            self.target, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ai_analysis
        )
        self.ws.write("reports/final_report.md", report)
        success("Final report generated")

    def run(self):
        start = time.time()
        banner()
        info("Target: {}".format(self.target))
        info("Domain: {}".format(self.domain))
        info("Workspace: {}".format(self.ws.root))
        info("AI Model: {}".format(self.config.model))
        info("Shodan: {}".format("YES" if self.config.has_shodan() else "NO"))
        info("VirusTotal: {}".format("YES" if self.config.has_vt() else "NO"))
        if self.args.learn_from:
            info("Learning from: {}".format(self.args.learn_from))
        print()

        session_id = self.feedback.record_session_start(self.target, {"domain": self.domain, "mode": "unified"})

        # PHASE 0: THREAT INTEL
        if self.config.has_shodan() or self.config.has_vt():
            section("PHASE 0: THREAT INTELLIGENCE GATHERING")
            intel = self.intel.gather(self.domain)
            self.ws.write_json("intel/threat_intel.json", intel)
            priority = intel.get("target_priority", {})
            success("Priority Score: {} ({})".format(priority.get("score", 0), priority.get("priority", "unknown")))
            for reason in priority.get("reasons", [])[:5]:
                info(reason)
            if intel.get("all_subdomains"):
                intel_text = str(intel)[:8000]
                analysis = self.ai.find_zero_day_hints(intel_text, self.target)
                self.ws.write("ai/intel_analysis.md", "# Threat Intel Analysis\n\n{}".format(analysis))
                success("AI intel analysis saved")

        # PHASE 1: RECON (run existing agent in subprocess)
        section("PHASE 1: COMPLETE RECONNAISSANCE")
        import subprocess as sp
        # We run the original agent as a subprocess to leverage its mature recon
        agent_path = self.args.agent_path or os.path.join(os.path.dirname(__file__), "agent_fixed.py")
        if os.path.exists(agent_path):
            info("Running recon via agent_fixed.py...")
            cmd = [
                sys.executable, agent_path,
                "--target", self.target,
                "--workspace", str(self.ws.root),
            ]
            if self.args.skip_slow: cmd.append("--skip-slow")
            sp.run(cmd, timeout=7200)
            success("Reconnaissance complete")
        else:
            warn("agent_fixed.py not found; recon must be run manually")
            warn("Place it at: {}".format(agent_path))

        self.feedback.record_technique(session_id, "full_recon", True)

        # PHASE 2: DYNAMIC SCANNING
        section("PHASE 2: DYNAMIC SCANNING & CUSTOM TEMPLATES")
        recon_data = {
            "tech_stack": self._detect_tech_stack(),
            "api_patterns": self._detect_api_patterns(),
            "anomalies": [], "logic_indicators": [], "zero_day_hints": [],
        }
        findings = self.scanner.run_all_dynamic_scans(recon_data)
        success("Dynamic scan findings: {}".format(len(findings)))
        for f in findings: self.feedback.record_finding(session_id, f)

        # PHASE 3: HEURISTICS
        section("PHASE 3: ZERO-DAY & LOGIC HEURISTICS")
        h_results = self.heuristics.run_all_heuristics(
            str(self.ws.path("subs/alive_hosts.txt")),
            str(self.ws.path("urls/all_urls_clean.txt")),
            str(self.ws.path("urls/param_names.txt")),
            str(self.ws.path("js")),
            str(self.ws.path("ports/nmap.txt")),
            str(self.ws.path("vulns/nuclei_tech.txt")),
        )
        total_h = sum(len(v) for v in h_results.values())
        success("Heuristic findings: {}".format(total_h))

        # PHASE 4: AI ANALYSIS
        section("PHASE 4: AI VULNERABILITY ANALYSIS")
        recon_text = self._load_recon_text()[:12000]
        analysis = self.ai.analyze_recon(self.target, recon_text)
        self.ws.write("reports/ai_analysis.md", "# AI Vulnerability Analysis\n\n{}".format(analysis))
        success("AI analysis saved")

        # Zero-day hints
        tech_stack_str = ",".join(self._detect_tech_stack())
        zero_day = self.ai.find_zero_day_hints(recon_text[:8000], self.target, tech_stack_str)
        self.ws.write("reports/zero_day_hints.md", "# Zero-Day Hints\n\n{}".format(zero_day))
        success("Zero-day hints saved")

        # Report generation
        section("PHASE 5: REPORT GENERATION")
        self._generate_final_report()

        # Learning
        if self.args.learn_from:
            section("PHASE 6: AI CONTINUOUS LEARNING")
            lr = self.ai.learn_from_past_bounties(self.args.learn_from)
            self.ws.write("ai/learning_results.md", "# Learning Results\n\n{}".format(lr))
            success("AI learning complete")

        # Close
        self.feedback.close_session(session_id, "completed")
        elapsed = int(time.time() - start)
        mins, secs = divmod(elapsed, 60)
        print("\n{}".format("="*60))
        print("[+] HUNT COMPLETE in {}m {}s".format(mins, secs))
        print("[+] Workspace: {}".format(self.ws.root))
        print("{}\n".format("="*60))


def main():
    parser = argparse.ArgumentParser(description="Tactical Zero Unified Bug Bounty Hunter")
    parser.add_argument("--target", required=True, help="Target URL (https://example.com)")
    parser.add_argument("--domain", help="Domain override")
    parser.add_argument("--output", default="./hunts", help="Output directory")
    parser.add_argument("--shodan-api-key", default=os.getenv("SHODAN_API_KEY"), help="Shodan API key")
    parser.add_argument("--vt-api-key", default=os.getenv("VT_API_KEY"), help="VirusTotal API key")
    parser.add_argument("--model", default="bugbounty-hunter", help="Ollama model name")
    parser.add_argument("--ollama-host", default=os.getenv("OLLAMA_HOST", "http://localhost:11434"), help="Ollama host")
    parser.add_argument("--skip-slow", action="store_true", help="Skip slow brute-force")
    parser.add_argument("--learn-from", help="Path to JSON file with past findings")
    parser.add_argument("--agent-path", help="Path to your original agent_fixed.py")
    args = parser.parse_args()

    if not args.target.startswith(("http://", "https://")):
        args.target = "https://" + args.target
    if not args.domain:
        from urllib.parse import urlparse
        args.domain = urlparse(args.target).netloc.split(":")[0]

    orchestrator = UnifiedHuntOrchestrator(args)
    orchestrator.run()


if __name__ == "__main__":
    main()

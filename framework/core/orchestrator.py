
"""
TACTICAL ZERO Orchestrator - Coordinates all framework components
"""
import asyncio, subprocess, shlex, shutil
from pathlib import Path

from framework.core.feedback import FeedbackLoop
from framework.ai.brain import AIBrain
from framework.adapters.intel import ThreatIntelAggregator
from framework.agents.scanner import DynamicScanner
from framework.agents.heuristics import ZeroDayHeuristics

class HuntOrchestrator:
    def __init__(self, config, workspace):
        self.config = config
        self.ws = workspace
        self.ai = AIBrain(config, workspace)
        self.intel = ThreatIntelAggregator(config.shodan_api_key, config.vt_api_key)
        self.scanner = DynamicScanner(config, workspace, self.ai)
        self.feedback = FeedbackLoop(workspace, config, self.ai)
        self.heuristics = ZeroDayHeuristics(workspace, self.ai)

    async def run(self):
        print(f"[+] TACTICAL ZERO orchestrator initialized for {self.config.target}")
        
        # Gather threat intelligence
        if self.config.has_shodan() or self.config.has_vt():
            print("[+] Gathering threat intelligence...")
            intel = self.intel.gather(self.config.domain)
            self.ws.write_json("intel/threat_intel.json", intel)
            print(f"    Shodan hosts: {len(intel.get('sources',{}).get('shodan',{}).get('subdomains',[]))}")
            print(f"    VT subdomains: {len(intel.get('sources',{}).get('virustotal',{}).get('subdomains',[]))}")
            
            # AI analysis of intel
            intel_text = str(intel)[:8000]
            analysis = self.ai.find_zero_day_hints(intel_text, self.config.target)
            self.ws.write("ai/intel_analysis.md", analysis)
        
        # Note: Recon steps are delegated to the existing robust agent
        print("[!] For full recon pipeline, run the existing agent_fixed.py first")
        print("[+] Then run AI analysis with: --mode ai-only")
        
        # Dynamic scanning on existing recon data
        recon_data = self._load_recon_data()
        if recon_data:
            print("[+] Running dynamic scans...")
            findings = self.scanner.run_all_dynamic_scans(recon_data)
            print(f"    Dynamic findings: {len(findings)}")
            
            print("[+] Running heuristic analysis...")
            heuristic_results = self.heuristics.run_all_heuristics(
                str(self.ws.path("subs/alive_hosts.txt")),
                str(self.ws.path("urls/all_urls_clean.txt")),
                str(self.ws.path("urls/param_names.txt")),
                str(self.ws.path("js")),
                str(self.ws.path("ports/nmap.txt")),
                str(self.ws.path("vulns/nuclei_tech.txt")),
            )
            print(f"    Heuristic findings: {sum(len(v) for v in heuristic_results.values())}")
        
        # AI final analysis
        print("[+] Running AI vulnerability analysis...")
        report = self._build_ai_report()
        self.ws.write("reports/final_report.md", report)
        print(f"[+] Report saved to {self.ws.path('reports/final_report.md')}")
        
        # Feedback
        self.feedback.close_session(1, "completed")
        print("[+] Hunt complete.")

    def _load_recon_data(self):
        data = {}
        for key, path in [
            ("subdomains", "subs/all_hosts.txt"),
            ("urls", "urls/all_urls_clean.txt"),
            ("ports", "ports/naabu_top1000.txt"),
            ("nuclei", "vulns/nuclei_main.txt"),
        ]:
            p = self.ws.path(path)
            if p.exists():
                data[key] = p.read_text(errors="ignore")[:2000]
        return data

    def _build_ai_report(self):
        recon_text = str(self._load_recon_data())[:12000]
        return self.ai.analyze_recon(self.config.target, recon_text)

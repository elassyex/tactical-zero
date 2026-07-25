#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════╗
║   TACTICAL ZERO - Autonomous Bug Bounty Framework         ║
║   Autonomous Recon + AI Analysis + Threat Intelligence    ║
╚═══════════════════════════════════════════════════════════╝

Entry: python3 bbf.py --target https://example.com
"""

import argparse, json, os, sys, time, asyncio
from datetime import datetime
from pathlib import Path

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "framework")
if SRC not in sys.path: sys.path.insert(0, SRC)

from framework.core.orchestrator import HuntOrchestrator
from framework.core.config import FrameworkConfig
from framework.core.workspace import WorkspaceManager


def banner():
    print("""
\033[1;32m╔═══════════════════════════════════════════════════════════╗
║   TACTICAL ZERO - Autonomous Bug Bounty Framework         ║
║   v3.0 | Intelligence-Driven | AI-Augmented | Adaptive    ║
╚═══════════════════════════════════════════════════════════╝\033[0m
""")


def main():
    banner()
    parser = argparse.ArgumentParser(description="Tactical Zero BB Framework")
    parser.add_argument("--target", required=True, help="Target URL or domain")
    parser.add_argument("--shodan-api-key", default=os.getenv("SHODAN_API_KEY",""), help="Shodan API key")
    parser.add_argument("--vt-api-key", default=os.getenv("VT_API_KEY",""), help="VirusTotal API key")
    parser.add_argument("--nuclei-templates", default="~/.local/nuclei-templates", help="Nuclei templates dir")
    parser.add_argument("--model", default="bugbounty-hunter", help="Ollama model name")
    parser.add_argument("--ollama-host", default=os.getenv("OLLAMA_HOST","http://localhost:11434"), help="Ollama host")
    parser.add_argument("--openai-api-key", default=os.getenv("OPENAI_API_KEY",""), help="OpenAI API key (optional)")
    parser.add_argument("--skip-slow", action="store_true", help="Skip slow brute-force steps")
    parser.add_argument("--mode", choices=["recon","scan","full","ai-only"], default="full", help="Operation mode")
    parser.add_argument("--focus", choices=["all","api","web","infrastructure","mobile","cloud"], default="all", help="Attack surface focus")
    parser.add_argument("--output", default="./hunts", help="Output directory")
    parser.add_argument("--max-subdomains", type=int, default=0, help="Max subdomains to process (0=unlimited)")
    parser.add_argument("--threads", type=int, default=50, help="Concurrent threads")
    parser.add_argument("--learn-from", help="Path to JSON file with past bounty findings for training")
    parser.add_argument("--config", default="config/config.yaml", help="Framework config file")
    args = parser.parse_args()

    config = FrameworkConfig.from_args(args)
    ws = WorkspaceManager(config.output_dir, config.domain)
    ws.init()

    print(f"\033[1;34m[*] Target    : {config.target}")
    print(f"[*] Domain    : {config.domain}")
    print(f"[*] Mode      : {config.mode}")
    print(f"[*] Focus     : {config.focus}")
    print(f"[*] Workspace : {ws.root}")
    print(f"[*] AI Model  : {config.model}")
    print(f"[*] Started   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\033[0m\n")

    orchestrator = HuntOrchestrator(config, ws)
    start = time.time()
    try:
        asyncio.run(orchestrator.run())
    except KeyboardInterrupt:
        print("\n\033[1;31m[!] Interrupted by user\033[0m")
        sys.exit(1)
    except Exception as e:
        print(f"\n\033[1;31m[-] Fatal error: {e}\033[0m")
        raise
    finally:
        elapsed = int(time.time() - start)
        print(f"\n\033[1;32m{'═'*60}")
        print(f"  HUNT COMPLETE in {elapsed//60}m {elapsed%60}s")
        print(f"  Workspace: {ws.root}")
        print(f"{'═'*60}\033[0m\n")


if __name__ == "__main__":
    main()

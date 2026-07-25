"""Framework configuration management."""
import os, yaml
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from urllib.parse import urlparse
from pathlib import Path


@dataclass
class FrameworkConfig:
    target: str
    domain: str
    raw_target: str
    shodan_api_key: str = ""
    vt_api_key: str = ""
    nuclei_templates_dir: str = "~/.local/nuclei-templates"
    model: str = "bugbounty-hunter"
    ollama_host: str = "http://localhost:11434"
    openai_api_key: str = ""
    skip_slow: bool = False
    mode: str = "full"
    focus: str = "all"
    output_dir: str = "./hunts"
    max_subdomains: int = 0
    threads: int = 50
    learn_from: str = ""
    config_path: str = ""
    slack_webhook: str = ""
    discord_webhook: str = ""
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    wordlists: Dict[str, str] = field(default_factory=dict)
    custom_scripts_dir: str = "./custom_scripts"
    auto_exploit: bool = False
    noise_filter_level: str = "high"
    priority_vectors: List[str] = field(default_factory=list)

    @classmethod
    def from_args(cls, args):
        raw = args.target.strip()
        if not raw.startswith(("http://", "https://")):
            raw = "https://" + raw
        parsed = urlparse(raw)
        domain = parsed.netloc or parsed.path
        domain = domain.split(":")[0].lower().strip("[]")
        target = f"{parsed.scheme}://{domain}{parsed.path}" if parsed.path != "/" else f"{parsed.scheme}://{domain}"

        config = cls(
            target=target,
            domain=domain,
            raw_target=raw,
            shodan_api_key=args.shodan_api_key,
            vt_api_key=args.vt_api_key,
            nuclei_templates_dir=os.path.expanduser(args.nuclei_templates),
            model=args.model,
            ollama_host=args.ollama_host,
            openai_api_key=args.openai_api_key,
            skip_slow=args.skip_slow,
            mode=args.mode,
            focus=args.focus,
            output_dir=args.output,
            max_subdomains=args.max_subdomains,
            threads=args.threads,
            learn_from=args.learn_from or "",
            config_path=args.config,
            slack_webhook=os.getenv("SLACK_WEBHOOK",""),
            discord_webhook=os.getenv("DISCORD_WEBHOOK",""),
            telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN",""),
            telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID",""),
            custom_scripts_dir="./custom_scripts",
            noise_filter_level="high",
        )
        config._load_yaml()
        config._setup_wordlists()
        return config

    def _load_yaml(self):
        cp = Path(self.config_path)
        if cp.exists():
            with open(cp) as f:
                data = yaml.safe_load(f) or {}
            for k, v in data.items():
                if hasattr(self, k) and not getattr(self, k):
                    setattr(self, k, v)

    def _setup_wordlists(self):
        defaults = {
            "dns_top": "/usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-110000.txt",
            "dns_jhaddix": "/usr/share/wordlists/seclists/Discovery/DNS/dns-Jhaddix.txt",
            "dns_bitquark": "/usr/share/wordlists/seclists/Discovery/DNS/bitquark-subdomains-top100000.txt",
            "dir_common": "/usr/share/wordlists/seclists/Discovery/Web-Content/common.txt",
            "dir_raft_med": "/usr/share/wordlists/seclists/Discovery/Web-Content/raft-medium-directories.txt",
            "dir_raft_lg": "/usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-directories.txt",
            "dir_files": "/usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-files.txt",
            "params": "/usr/share/wordlists/seclists/Discovery/Web-Content/burp-parameter-names.txt",
            "api_endpoints": "/usr/share/wordlists/seclists/Discovery/Web-Content/api/api endpoints.txt",
        }
        if self.wordlists:
            defaults.update(self.wordlists)
        self.wordlists = {k: v for k, v in defaults.items() if os.path.exists(v)}

    def has_shodan(self) -> bool:
        return bool(self.shodan_api_key)

    def has_vt(self) -> bool:
        return bool(self.vt_api_key)

    def has_openai(self) -> bool:
        return bool(self.openai_api_key)

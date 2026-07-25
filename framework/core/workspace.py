"""Workspace management for organized output."""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional


class WorkspaceManager:
    def __init__(self, output_dir: str, domain: str):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.root = Path(output_dir) / f"{domain}_{ts}"
        self.domain = domain
        self._state: Dict[str, Any] = {"stages": {}, "findings": []}

    def init(self):
        self.root.mkdir(parents=True, exist_ok=True)
        for d in ["subs", "urls", "js", "params", "vulns", "reports",
                  "ports", "dirs", "intel", "nuclei", "findings", "ai", "db"]:
            (self.root / d).mkdir(exist_ok=True)
        return self

    def path(self, *parts) -> Path:
        return self.root.joinpath(*parts)

    def write(self, rel_path: str, content: str):
        p = self.path(rel_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8", errors="ignore")

    def write_json(self, rel_path: str, data: dict):
        self.write(rel_path, json.dumps(data, indent=2, default=str))

    def read(self, rel_path: str) -> str:
        try:
            return self.path(rel_path).read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return ""

    def read_json(self, rel_path: str) -> dict:
        try:
            return json.loads(self.read(rel_path))
        except Exception:
            return {}

    def save_findings(self, findings: list):
        self._state["findings"].extend(findings)
        self.write_json("db/findings.json", self._state["findings"])

    def update_stage(self, stage: str, data: dict):
        self._state["stages"][stage] = data
        self.write_json("db/state.json", self._state)

    def get_state(self) -> Dict[str, Any]:
        return self._state

    def add_finding(self, finding: Dict[str, Any]):
        finding["timestamp"] = datetime.now().isoformat()
        finding["id"] = f"{len(self._state['findings'])+1:04d}"
        self._state["findings"].append(finding)
        self.write_json("db/findings.json", self._state["findings"])

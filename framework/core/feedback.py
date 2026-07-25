"""
Feedback Loop & Continuous Learning System
Learns from successful findings to refine search parameters and prioritize targets.
"""
import json, os, re
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime


class FeedbackLoop:
    """
    Implements the learning system that:
    1. Records scan outcomes and findings
    2. Analyzes patterns in successful vs failed attempts
    3. Updates target priorities based on historical data
    4. Generates refined reconnaissance rules
    5. Improves Nuclei templates over time
    """

    def __init__(self, workspace, config, ai_brain=None):
        self.workspace = workspace
        self.config = config
        self.ai = ai_brain
        self.db_path = Path("data/learning_db.json")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db = self._load_db()

    def _load_db(self) -> Dict:
        if self.db_path.exists():
            try:
                return json.loads(self.db_path.read_text())
            except Exception:
                pass
        return {
            "sessions": [],
            "successful_patterns": {},
            "failed_patterns": {},
            "target_scores": {},
            "technique_effectiveness": {},
            "template_performance": {},
            "noise_indicators": [],
        }

    def _save_db(self):
        self.db_path.write_text(json.dumps(self.db, indent=2, default=str))

    def record_session_start(self, target: str, config_snapshot: dict):
        session = {
            "id": len(self.db["sessions"]) + 1,
            "target": target,
            "timestamp": datetime.now().isoformat(),
            "config": config_snapshot,
            "findings": [],
            "techniques_used": [],
            "outcome": "in_progress",
        }
        self.db["sessions"].append(session)
        self._save_db()
        return session["id"]

    def record_finding(self, session_id: int, finding: Dict):
        finding["recorded_at"] = datetime.now().isoformat()
        finding["session_id"] = session_id
        for s in self.db["sessions"]:
            if s["id"] == session_id:
                s["findings"].append(finding)
                break

        # Update pattern tracking
        self._update_pattern_tracking(finding)
        self._save_db()

    def record_technique(self, session_id: int, technique: str, success: bool, metadata: dict = None):
        for s in self.db["sessions"]:
            if s["id"] == session_id:
                s["techniques_used"].append({
                    "name": technique,
                    "success": success,
                    "metadata": metadata or {},
                    "timestamp": datetime.now().isoformat(),
                })
                break

        # Track technique effectiveness
        if technique not in self.db["technique_effectiveness"]:
            self.db["technique_effectiveness"][technique] = {"success": 0, "failure": 0, "total": 0}
        self.db["technique_effectiveness"][technique]["total"] += 1
        if success:
            self.db["technique_effectiveness"][technique]["success"] += 1
        else:
            self.db["technique_effectiveness"][technique]["failure"] += 1
        self._save_db()

    def _update_pattern_tracking(self, finding: Dict):
        pattern_type = finding.get("type", "unknown")
        severity = finding.get("severity", "info")

        # Successful patterns
        if severity in ("critical", "high"):
            if pattern_type not in self.db["successful_patterns"]:
                self.db["successful_patterns"][pattern_type] = []
            self.db["successful_patterns"][pattern_type].append({
                "finding": finding,
                "timestamp": datetime.now().isoformat(),
            })
            # Keep last 50 per type
            self.db["successful_patterns"][pattern_type] = self.db["successful_patterns"][pattern_type][-50:]

        # Track noise indicators for false positive reduction
        if severity == "info":
            indicator = finding.get("indicator", "")
            if indicator:
                self.db["noise_indicators"].append({
                    "indicator": indicator,
                    "type": pattern_type,
                    "count": self.db["noise_indicators"].count({"indicator": indicator, "type": pattern_type}) + 1,
                })
            self.db["noise_indicators"] = self.db["noise_indicators"][-200:]

    def calculate_target_score(self, target: str, intel_data: Dict) -> Dict:
        """Calculate a priority score for a target based on learning data."""
        score = 0
        reasons = []

        # Base score from threat intel
        priority_data = intel_data.get("target_priority", {})
        score += priority_data.get("score", 0)
        reasons.extend(priority_data.get("reasons", []))

        # Historical success rate for this domain pattern
        domain_pattern = target.split(".")[-2:] if "." in target else [target]
        domain_key = ".".join(domain_pattern)
        hist = self.db["target_scores"].get(domain_key, {})
        if hist:
            success_rate = hist.get("successes", 0) / max(hist.get("total", 1), 1)
            score += success_rate * 20
            if success_rate > 0.3:
                reasons.append(f"High historical success rate ({success_rate:.0%})")

        # Technique effectiveness for this target type
        tech_stack = intel_data.get("tech_stack", [])
        for tech in tech_stack:
            for technique, stats in self.db["technique_effectiveness"].items():
                if tech.lower() in technique.lower():
                    success_rate = stats["success"] / max(stats["total"], 1)
                    if success_rate > 0.5:
                        score += 5
                        reasons.append(f"Effective technique '{technique}' for {tech}")

        # Template performance
        for template_id, perf in self.db["template_performance"].items():
            if perf.get("false_positive_rate", 0) < 0.1 and perf.get("findings", 0) > 0:
                score += 3

        # Prioritize targets with known CVEs in their stack
        cves = intel_data.get("cves", [])
        if cves:
            score += len(cves) * 5
            reasons.append(f"{len(cves)} known CVEs in technology stack")

        priority = "critical" if score > 50 else "high" if score > 30 else "medium" if score > 15 else "low"
        return {"score": score, "reasons": reasons, "priority": priority, "domain_key": domain_key}

    def update_target_score(self, target: str, success: bool):
        domain_pattern = target.split(".")[-2:] if "." in target else [target]
        domain_key = ".".join(domain_pattern)
        if domain_key not in self.db["target_scores"]:
            self.db["target_scores"][domain_key] = {"successes": 0, "failures": 0, "total": 0}
        self.db["target_scores"][domain_key]["total"] += 1
        if success:
            self.db["target_scores"][domain_key]["successes"] += 1
        else:
            self.db["target_scores"][domain_key]["failures"] += 1
        self._save_db()

    def get_prioritized_targets(self, targets: List[str], intel_data: Dict) -> List[Dict]:
        """Sort targets by calculated priority score."""
        scored = []
        for target in targets:
            score_data = self.calculate_target_score(target, intel_data)
            scored.append({"target": target, **score_data})
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored

    def generate_refined_rules(self) -> Dict:
        """Generate updated reconnaissance rules based on learning."""
        rules = {
            "subdomain_priorities": [],
            "path_priorities": [],
            "parameter_priorities": [],
            "technology_focus": [],
            "skip_patterns": [],
        }

        # Analyze successful patterns
        for pattern_type, findings in self.db["successful_patterns"].items():
            if not findings:
                continue
            recent = findings[-10:]
            # Extract common indicators
            indicators = []
            for f in recent:
                for key in ["endpoint", "path", "url", "parameter", "technology"]:
                    if key in f.get("finding", {}):
                        indicators.append(f["finding"][key])

            # Add to rules
            if pattern_type in ("ssrf", "idor", "lfi", "rce", "sqli", "xss"):
                for ind in set(indicators)[:5]:
                    rules["parameter_priorities"].append({"param": ind, "pattern": pattern_type})
            elif pattern_type in ("exposure", "jenkins", "grafana", "swagger"):
                for ind in set(indicators)[:5]:
                    rules["path_priorities"].append({"path": ind, "pattern": pattern_type})

        # Analyze technique effectiveness
        sorted_techniques = sorted(
            self.db["technique_effectiveness"].items(),
            key=lambda x: x[1]["success"] / max(x[1]["total"], 1),
            reverse=True,
        )
        rules["recommended_techniques"] = [
            {"name": t[0], "success_rate": t[1]["success"] / max(t[1]["total"], 1)}
            for t in sorted_techniques[:10]
        ]

        # Noise indicators to skip
        noise_counts = {}
        for n in self.db["noise_indicators"]:
            key = (n["indicator"], n["type"])
            noise_counts[key] = noise_counts.get(key, 0) + 1
        rules["skip_patterns"] = [
            {"indicator": k[0], "type": k[1], "count": v}
            for k, v in sorted(noise_counts.items(), key=lambda x: x[1], reverse=True)[:20]
        ]

        return rules

    def filter_findings(self, findings: List[Dict]) -> List[Dict]:
        """Apply noise filtering based on learned patterns."""
        filtered = []
        for finding in findings:
            # Skip known noise
            skip = False
            for noise in self.db["noise_indicators"][-50:]:
                if finding.get("indicator") == noise["indicator"] and finding.get("type") == noise["type"]:
                    skip = True
                    break
            if not skip:
                filtered.append(finding)
        return filtered

    def improve_templates(self, template_dir: str):
        """Suggest improvements to existing templates based on performance."""
        if not self.ai:
            return []

        improvements = []
        for template_id, perf in self.db["template_performance"].items():
            fp_rate = perf.get("false_positive_rate", 0)
            if fp_rate > 0.3:
                # High false positive - ask AI to improve
                prompt = f"""Improve this Nuclei template which has {fp_rate:.0%} false positive rate:
Template ID: {template_id}
Current findings: {perf.get('findings', 0)}
False positives: {perf.get('false_positives', 0)}

Provide specific matcher improvements to reduce false positives.
"""
                response = self.ai.ask(prompt)
                improvements.append({
                    "template": template_id,
                    "issue": "high_false_positive",
                    "suggestion": response,
                })

        return improvements

    def export_learning_report(self) -> str:
        """Generate a human-readable learning report."""
        report = f"""# TACTICAL ZERO Learning Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Session Statistics
- Total sessions: {len(self.db['sessions'])}
- Successful sessions: {sum(1 for s in self.db['sessions'] if len(s.get('findings', [])) > 0)}
- Total findings: {sum(len(s.get('findings', [])) for s in self.db['sessions'])}

## Most Effective Techniques
"""
        sorted_tech = sorted(
            self.db["technique_effectiveness"].items(),
            key=lambda x: x[1]["success"] / max(x[1]["total"], 1),
            reverse=True,
        )[:10]

        for name, stats in sorted_tech:
            rate = stats["success"] / max(stats["total"], 1)
            report += f"- {name}: {rate:.0%} success ({stats['success']}/{stats['total']})\n"

        report += "\n## Successful Patterns\n"
        for pattern_type, findings in self.db["successful_patterns"].items():
            if findings:
                report += f"- {pattern_type}: {len(findings)} findings\n"

        report += "\n## Top Target Domains\n"
        sorted_targets = sorted(
            self.db["target_scores"].items(),
            key=lambda x: x[1]["successes"] / max(x[1]["total"], 1),
            reverse=True,
        )[:10]
        for domain, scores in sorted_targets:
            rate = scores["successes"] / max(scores["total"], 1)
            report += f"- {domain}: {rate:.0%} success\n"

        return report

    def close_session(self, session_id: int, outcome: str):
        for s in self.db["sessions"]:
            if s["id"] == session_id:
                s["outcome"] = outcome
                s["ended_at"] = datetime.now().isoformat()
                break
        self._save_db()

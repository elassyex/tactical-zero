"""
AI Brain Module for TACTICAL ZERO
Multi-provider LLM support with BB-specialized skills, prompt engineering,
and a continuous learning feedback loop.
"""
import json, os, re, time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class BBSkill:
    name: str
    system_prompt: str
    user_template: str
    requires_context: List[str] = field(default_factory=list)
    temperature: float = 0.2
    max_tokens: int = 4000


# ─── BUILT-IN BUG BOUNTY SKILLS ──────────────────────────────
SKILL_VULNERABILITY_ANALYSIS = BBSkill(
    name="vulnerability_analysis",
    system_prompt=(
        "You are an elite bug bounty hunter with 15+ years of experience. "
        "You have found critical vulnerabilities at Google, Facebook, Apple, and Microsoft. "
        "Your analysis is precise, technical, and actionable.\n\n"
        "RULES:\n"
        "1. Identify REAL vulnerabilities, not theoretical ones\n"
        "2. Prioritize by impact (RCE > SQLi > SSRF > XSS > Info Disclosure)\n"
        "3. Provide exact reproduction steps\n"
        "4. Suggest the most likely parameter to fuzz\n"
        "5. Rate each finding: Critical / High / Medium / Low / Info\n"
        "6. For each finding, estimate bounty potential: $0-500 / $500-2k / $2k-5k / $5k-10k / $10k+\n"
    ),
    user_template="""Analyze the following recon data for target {target}.

{recon_data}

Provide:
1. CRITICAL FINDINGS (with exact reproduction steps)
2. HIGH-VALUE ATTACK VECTORS (top 5, sorted by exploitability)
3. MANUAL TESTING CHECKLIST (what to test next)
4. BOUNTY POTENTIAL ESTIMATES per finding
5. SUGGESTED PAYLOADS for the most promising vectors
""",
    requires_context=["target", "recon_data"],
    temperature=0.15,
)

SKILL_NUCLEI_TEMPLATE_GENERATION = BBSkill(
    name="nuclei_template_generation",
    system_prompt=(
        "You are a Nuclei template expert. Generate valid YAML Nuclei templates "
        "that detect specific vulnerability patterns. Templates must be syntactically correct, "
        "use proper matchers, and follow the Nuclei template specification.\n\n"
        "RULES:\n"
        "1. Use id:, info:, and requests: blocks\n"
        "2. Include proper severity and tags\n"
        "3. Use {{BaseURL}} and {{Hostname}} variables\n"
        "4. Include extractors for proof of vulnerability\n"
        "5. Matchers should be specific to avoid false positives\n"
    ),
    user_template="""Generate a Nuclei template to detect the following vulnerability pattern:

Description: {description}
Target Type: {target_type}
Detection Pattern: {pattern}
Evidence from recon: {evidence}

Output the complete YAML template. No markdown code blocks, just raw YAML.
""",
    requires_context=["description", "target_type", "pattern", "evidence"],
    temperature=0.1,
)

SKILL_EXPLOIT_CHAIN_DESIGN = BBSkill(
    name="exploit_chain_design",
    system_prompt=(
        "You design multi-step exploit chains for bug bounties. "
        "You think in terms of combining low-severity issues into critical findings.\n\n"
        "RULES:\n"
        "1. Chain multiple low/medium findings into critical impact\n"
        "2. Consider authentication bypass → privilege escalation → sensitive data access\n"
        "3. Consider information leak → account takeover\n"
        "4. Consider SSRF → internal service access → cloud metadata\n"
        "5. Each step must be verifiable\n"
    ),
    user_template="""Design an exploit chain for {target} using these findings:

{findings}

Provide a step-by-step chain with:
1. Prerequisites
2. Step 1 (entry point)
3. Step 2 (escalation)
4. Step 3 (impact)
5. Proof of concept payload sequence
6. Estimated bounty value if successful
""",
    requires_context=["target", "findings"],
    temperature=0.2,
)

SKILL_REPORT_WRITING = BBSkill(
    name="report_writing",
    system_prompt=(
        "You write professional bug bounty reports that get accepted and paid. "
        "Reports follow HackerOne/Bugcrowd standards and include clear impact statements.\n\n"
        "RULES:\n"
        "1. Title: clear, concise, includes vulnerability type\n"
        "2. Summary: 2-3 sentences max\n"
        "3. Steps to Reproduce: numbered, exact, copy-paste friendly\n"
        "4. Impact: business impact, not just technical\n"
        "5. Mitigation: specific, actionable\n"
        "6. Proof of Concept: {{BaseURL}} variable for host\n"
    ),
    user_template="""Write a complete {platform} report for:

Vulnerability: {vuln_type}
Target: {target}
Endpoint: {endpoint}
Evidence: {evidence}
Severity: {severity}

Generate the full report in markdown.
""",
    requires_context=["platform", "vuln_type", "target", "endpoint", "evidence", "severity"],
    temperature=0.15,
)

SKILL_TREND_ANALYSIS = BBSkill(
    name="trend_analysis",
    system_prompt=(
        "You analyze bug bounty trends and security research to identify "
        "emerging vulnerability classes and exploitation techniques.\n\n"
        "RULES:\n"
        "1. Focus on trends from the last 12 months\n"
        "2. Identify techniques that are under-tested\n"
        "3. Correlate technology stacks with vulnerability patterns\n"
        "4. Suggest novel test vectors based on emerging patterns\n"
    ),
    user_template="""Analyze the following technology stack and suggest emerging attack vectors:

Target: {target}
Tech Stack: {tech_stack}
Recent Findings: {recent_findings}

Provide:
1. Emerging vulnerability trends matching this stack
2. Under-tested attack surfaces
3. Novel vectors to try
4. References to recent disclosed reports
""",
    requires_context=["target", "tech_stack", "recent_findings"],
    temperature=0.3,
)

SKILL_NOISE_FILTER = BBSkill(
    name="noise_filter",
    system_prompt=(
        "You filter security scan output to identify only high-signal findings. "
        "You discard false positives, duplicate information, and low-value noise.\n\n"
        "RULES:\n"
        "1. Keep only findings with actionable impact\n"
        "2. Remove generic headers, common configurations\n"
        "3. Flag findings that need manual verification\n"
        "4. Score each finding 0-100 on exploitability\n"
        "5. Group similar findings\n"
    ),
    user_template="""Filter and prioritize these scan results:

{scan_results}

Target: {target}
Focus: {focus}

Output a JSON array of findings with: id, title, severity, exploitability_score, action, rationale.
""",
    requires_context=["scan_results", "target", "focus"],
    temperature=0.1,
)

SKILL_ZERO_DAY_HINT = BBSkill(
    name="zero_day_hint",
    system_prompt=(
        "You identify hints of zero-day or unreported vulnerabilities in recon data. "
        "You look for anomalies, unusual behaviors, and patterns that don't match known CVEs.\n\n"
        "RULES:\n"
        "1. Flag anomalous response patterns\n"
        "2. Identify logic flaws from URL/parameter structures\n"
        "3. Look for inconsistent access controls\n"
        "4. Find unusual API behaviors\n"
        "5. Suggest custom fuzzing strategies\n"
    ),
    user_template="""Analyze this recon data for zero-day hints:

{recon_data}

Target: {target}
Tech Stack: {tech_stack}

Identify:
1. Anomalies suggesting unknown vulnerabilities
2. Logic flaw indicators
3. Behavior inconsistencies
4. Recommended custom testing approaches
5. Confidence level for each hint
""",
    requires_context=["recon_data", "target", "tech_stack"],
    temperature=0.25,
)

SKILL_TRAINING_MENTOR = BBSkill(
    name="training_mentor",
    system_prompt=(
        "You are a bug bounty training mentor. You analyze past findings and teach "
        "the system how to better identify similar issues in the future.\n\n"
        "RULES:\n"
        "1. Identify what signals led to successful findings\n"
        "2. Create pattern templates for future detection\n"
        "3. Suggest new reconnaissance steps\n"
        "4. Update strategy based on program-specific learnings\n"
    ),
    user_template="""Analyze these past bounty findings and generate learnings:

{findings}

Generate:
1. Key patterns that led to successful findings
2. New reconnaissance rules to add
3. Updated priority scoring logic
4. Nuclei template suggestions for detected patterns
5. Strategy adjustments for similar targets
""",
    requires_context=["findings"],
    temperature=0.2,
)

ALL_SKILLS: Dict[str, BBSkill] = {
    s.name: s for s in [
        SKILL_VULNERABILITY_ANALYSIS,
        SKILL_NUCLEI_TEMPLATE_GENERATION,
        SKILL_EXPLOIT_CHAIN_DESIGN,
        SKILL_REPORT_WRITING,
        SKILL_TREND_ANALYSIS,
        SKILL_NOISE_FILTER,
        SKILL_ZERO_DAY_HINT,
        SKILL_TRAINING_MENTOR,
    ]
}


class AIConnector:
    """Unified AI provider connector (Ollama, OpenAI, etc)."""

    def __init__(self, config):
        self.config = config
        self.provider = self._detect_provider()
        self._conversation_history: List[Dict[str, str]] = []
        self._rate_limit_map: Dict[str, float] = {}

    def _detect_provider(self) -> str:
        if self.config.has_openai():
            return "openai"
        return "ollama"

    def _rate_limit(self, provider: str):
        now = time.time()
        last = self._rate_limit_map.get(provider, 0)
        if provider == "ollama" and now - last < 0.5:
            time.sleep(0.5 - (now - last))
        elif provider == "openai" and now - last < 0.2:
            time.sleep(0.2 - (now - last))
        self._rate_limit_map[provider] = time.time()

    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.2, max_tokens: int = 4000) -> str:
        if self.provider == "openai":
            return self._chat_openai(messages, temperature, max_tokens)
        return self._chat_ollama(messages, temperature, max_tokens)

    def _chat_ollama(self, messages, temperature, max_tokens) -> str:
        self._rate_limit("ollama")
        try:
            import ollama
            client = ollama.Client(host=self.config.ollama_host)
            r = client.chat(
                model=self.config.model,
                messages=messages,
                options={"temperature": temperature, "num_predict": max_tokens},
            )
            return r["message"]["content"]
        except Exception as e:
            return f"[OLLAMA ERROR: {e}]"

    def _chat_openai(self, messages, temperature, max_tokens) -> str:
        self._rate_limit("openai")
        try:
            import openai
            client = openai.OpenAI(api_key=self.config.openai_api_key)
            r = client.chat.completions.create(
                model="gpt-4o" if "gpt-4" in self.config.model else self.config.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return r.choices[0].message.content
        except Exception as e:
            return f"[OPENAI ERROR: {e}]"

    def ask(self, prompt: str, system: str = "", temperature: float = 0.2, max_tokens: int = 4000) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        return self.chat(messages, temperature, max_tokens)


class AIBrain:
    """
    Main AI orchestrator with BB-specialized skills, memory, and learning.
    This is the central intelligence of TACTICAL ZERO.
    """

    def __init__(self, config, workspace=None):
        self.config = config
        self.workspace = workspace
        self.connector = AIConnector(config)
        self.memory_path = Path("data/ai_memory.json")
        self.memory_path.parent.mkdir(parents=True, exist_ok=True)
        self.memory = self._load_memory()
        self.session_context: Dict[str, Any] = {}

    def _load_memory(self) -> Dict:
        if self.memory_path.exists():
            try:
                return json.loads(self.memory_path.read_text())
            except Exception:
                pass
        return {
            "successful_patterns": [],
            "failed_patterns": [],
            "target_profiles": {},
            "skill_improvements": {},
            "bounty_estimates": {},
        }

    def _save_memory(self):
        self.memory_path.write_text(json.dumps(self.memory, indent=2, default=str))

    def use_skill(self, skill_name: str, context: Dict[str, Any]) -> str:
        if skill_name not in ALL_SKILLS:
            raise ValueError(f"Unknown skill: {skill_name}. Available: {list(ALL_SKILLS.keys())}")
        skill = ALL_SKILLS[skill_name]

        # Validate required context
        missing = [c for c in skill.requires_context if c not in context]
        if missing:
            raise ValueError(f"Skill '{skill_name}' missing context: {missing}")

        # Build prompt
        prompt = skill.user_template.format(**context)

        # Add memory context for training mentor
        if skill_name == "training_mentor" and self.memory.get("successful_patterns"):
            prompt += f"\n\nPreviously successful patterns:\n{json.dumps(self.memory['successful_patterns'][-10:], indent=2)}"

        # Add target profile if available
        if context.get("target") and context["target"] in self.memory.get("target_profiles", {}):
            profile = self.memory["target_profiles"][context["target"]]
            prompt += f"\n\nTarget profile (from past runs):\n{json.dumps(profile, indent=2)}"

        response = self.connector.ask(
            prompt=prompt,
            system=skill.system_prompt,
            temperature=skill.temperature,
            max_tokens=skill.max_tokens,
        )

        # Save to session context
        self.session_context[skill_name] = {"prompt": prompt, "response": response}

        if self.workspace:
            ts = int(time.time())
            self.workspace.write(f"ai/{skill_name}_{ts}.md", f"# {skill_name}\n\n## Prompt\n{prompt}\n\n## Response\n{response}")

        return response

    def analyze_recon(self, target: str, recon_data: str) -> str:
        return self.use_skill("vulnerability_analysis", {
            "target": target,
            "recon_data": recon_data[:15000],  # Token limit safety
        })

    def generate_nuclei_template(self, description: str, target_type: str, pattern: str, evidence: str) -> str:
        return self.use_skill("nuclei_template_generation", {
            "description": description,
            "target_type": target_type,
            "pattern": pattern,
            "evidence": evidence,
        })

    def design_exploit_chain(self, target: str, findings: str) -> str:
        return self.use_skill("exploit_chain_design", {
            "target": target,
            "findings": findings,
        })

    def write_report(self, platform: str, vuln_type: str, target: str, endpoint: str, evidence: str, severity: str) -> str:
        return self.use_skill("report_writing", {
            "platform": platform,
            "vuln_type": vuln_type,
            "target": target,
            "endpoint": endpoint,
            "evidence": evidence,
            "severity": severity,
        })

    def filter_noise(self, scan_results: str, target: str, focus: str = "all") -> str:
        return self.use_skill("noise_filter", {
            "scan_results": scan_results,
            "target": target,
            "focus": focus,
        })

    def find_zero_day_hints(self, recon_data: str, target: str, tech_stack: str = "") -> str:
        return self.use_skill("zero_day_hint", {
            "recon_data": recon_data,
            "target": target,
            "tech_stack": tech_stack,
        })

    def analyze_trends(self, target: str, tech_stack: str, recent_findings: str) -> str:
        return self.use_skill("trend_analysis", {
            "target": target,
            "tech_stack": tech_stack,
            "recent_findings": recent_findings,
        })

    def train_from_findings(self, findings: List[Dict]) -> str:
        findings_json = json.dumps(findings, indent=2, default=str)
        response = self.use_skill("training_mentor", {"findings": findings_json})

        # Parse and update memory
        try:
            # Extract patterns from AI response
            patterns = self._extract_patterns(response)
            self.memory["successful_patterns"].extend(patterns)
            self.memory["successful_patterns"] = self.memory["successful_patterns"][-200:]  # Keep last 200
            self._save_memory()
        except Exception:
            pass

        return response

    def _extract_patterns(self, text: str) -> List[Dict]:
        patterns = []
        for line in text.splitlines():
            if any(k in line.lower() for k in ["pattern", "template", "rule", "regex", "indicator"]):
                patterns.append({"text": line.strip(), "source": "ai_training"})
        return patterns

    def save_target_profile(self, target: str, profile: Dict):
        if "target_profiles" not in self.memory:
            self.memory["target_profiles"] = {}
        self.memory["target_profiles"][target] = profile
        self._save_memory()

    def get_target_profile(self, target: str) -> Optional[Dict]:
        return self.memory.get("target_profiles", {}).get(target)

    def update_skill(self, skill_name: str, feedback: str, success: bool):
        if skill_name not in self.memory["skill_improvements"]:
            self.memory["skill_improvements"][skill_name] = {"runs": 0, "successes": 0, "feedback": []}
        self.memory["skill_improvements"][skill_name]["runs"] += 1
        if success:
            self.memory["skill_improvements"][skill_name]["successes"] += 1
        self.memory["skill_improvements"][skill_name]["feedback"].append(feedback)
        self.memory["skill_improvements"][skill_name]["feedback"] = self.memory["skill_improvements"][skill_name]["feedback"][-20:]
        self._save_memory()

    def learn_from_past_bounties(self, filepath: str) -> str:
        if not os.path.exists(filepath):
            return f"[No learning file found at {filepath}]"
        try:
            with open(filepath) as f:
                data = json.load(f)
            findings = data if isinstance(data, list) else data.get("findings", [])
            return self.train_from_findings(findings)
        except Exception as e:
            return f"[Learning error: {e}]"

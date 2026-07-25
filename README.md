# TACTICAL ZERO - Autonomous Bug Bounty Framework

**v3.0 | Intelligence-Driven | AI-Augmented | Adaptive**

## Quick Start

```bash
# 1. Install dependencies
pip3 install -r requirements.txt

# 2. Set API keys (optional but recommended)
export SHODAN_API_KEY="your_key"
export VT_API_KEY="your_key"

# 3. Run a hunt
python3 bbf.py --target https://example.com

# 4. Run with AI analysis only (after recon)
python3 bbf.py --target https://example.com --mode ai-only
```

## Architecture

```
TACTICAL ZERO
├── bbf.py                      # Entry point
├── framework/
│   ├── core/
│   │   ├── config.py           # Configuration management
│   │   ├── workspace.py        # Output organization
│   │   ├── feedback.py         # Learning & feedback loop
│   │   └── orchestrator.py     # Pipeline coordination
│   ├── adapters/
│   │   └── intel.py            # Shodan/VT threat intel
│   ├── ai/
│   │   └── brain.py            # Multi-provider AI with BB skills
│   ├── agents/
│   │   ├── scanner.py          # Dynamic scanning engine
│   │   └── heuristics.py       # Zero-day & logic flaw detection
│   └── agents/
│       └── (future)
├── config/
│   └── config.yaml             # Framework configuration
├── data/
│   └── ai_memory.json          # AI learning database
└── docs/
    └── TRAINING.md             # AI training guide
```

## Key Features

### 1. Threat Intelligence Integration
- **Shodan**: Service discovery, CVE mapping, network topology
- **VirusTotal**: Domain reputation, subdomains, communicating files
- **Priority Scoring**: Automatically ranks targets by exploitability

### 2. AI-Powered Analysis (8 Specialized Skills)
| Skill | Purpose |
|-------|---------|
| `vulnerability_analysis` | Deep recon analysis + bounty estimates |
| `nuclei_template_generation` | Auto-create custom templates from findings |
| `exploit_chain_design` | Chain low-severity into critical findings |
| `report_writing` | HackerOne/Bugcrowd-ready reports |
| `trend_analysis` | Emerging vulnerability detection |
| `noise_filter` | High-signal filtering based on context |
| `zero_day_hint` | Anomaly detection for unknown vulns |
| `training_mentor` | Learn from past bounty successes |

### 3. Dynamic Scanning Engine
- Auto-generates custom Nuclei templates from detected tech stack
- Creative 403 bypass testing with 9+ techniques
- SSRF payload injection with internal service targeting
- Business logic flaw detection (price/quantity/role manipulation)
- Advanced JWT security testing (none alg, secret extraction)

### 4. Feedback & Learning Loop
- Tracks technique effectiveness across sessions
- Calculates target priority scores based on historical data
- Generates refined recon rules from successful patterns
- Filters noise based on learned false positive indicators
- Improved template suggestions with AI-driven optimization

### 5. Zero-Day & Logic Vulnerability Heuristics
- Response pattern anomaly detection
- JavaScript anti-pattern analysis
- Inconsistent access control identification
- Technology version vulnerability mapping
- Logic flaw parameter inference

## Training the AI for Bug Bounties

See `docs/TRAINING.md` for the complete guide on:
- Training with past bounty findings
- Crafting effective prompts
- Building a knowledge base
- Fine-tuning models

## Configuration

Edit `config/config.yaml` or set environment variables:

```yaml
shodan_api_key: ""
vt_api_key: ""
ollama_host: "http://localhost:11434"
model: "bugbounty-hunter"
focus: all          # all, api, web, infrastructure, mobile, cloud
noise_filter_level: high
```

## Output Structure

```
hunts/
└── example.com_20250716_053219/
    ├── subs/           # Subdomain data
    ├── urls/           # URL discovery & categorization
    ├── js/             # JavaScript secrets
    ├── params/         # Hidden parameters
    ├── vulns/          # Vulnerability findings
    ├── ports/          # Port scans
    ├── dirs/           # Directory brute force
    ├── intel/          # Threat intelligence
    ├── nuclei/         # Custom Nuclei templates
    ├── ai/             # AI analysis outputs
    └── reports/        # Final reports
```

## License

For educational and authorized security testing only.

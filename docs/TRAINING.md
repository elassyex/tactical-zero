# AI Training Guide for TACTICAL ZERO

This guide explains how to train, configure, and optimize the AI components of TACTICAL ZERO for maximum bounty hunting effectiveness.

## Table of Contents
1. [Model Selection](#model-selection)
2. [Training with Past Findings](#training-with-past-findings)
3. [Skill-Specific Prompt Engineering](#skill-specific-prompt-engineering)
4. [Building the Knowledge Base](#building-the-knowledge-base)
5. [Fine-Tuning with Ollama](#fine-tuning-with-ollama)
6. [Continuous Learning Workflow](#continuous-learning-workflow)

---

## Model Selection

### Recommended Models (Ranked for Bug Bounty Work)

| Rank | Model | Strengths | Best For |
|------|-------|-----------|----------|
| 1 | **Llama 3.1 70B** | Strong reasoning, large context | Full analysis, exploit chains |
| 2 | **Claude 3.5 Sonnet** | Excellent following instructions | Report writing, template generation |
| 3 | **GPT-4o** | Fast, good at structured output | Quick filtering, trend analysis |
| 4 | **Mistral 7B Instruct** | Fast, runs locally | Basic analysis on limited hardware |
| 5 | **Llama 3.1 8B** | Very fast local inference | Noise filtering, simple tasks |

### Setting Up Ollama Models

```bash
# Pull a base model
ollama pull llama3.1:70b

# Create a custom BB-specialized model
cat > Modelfile << 'EOF'
FROM llama3.1:70b
SYSTEM """You are TacticalZero, an elite bug bounty hunter with 15+ years of experience. You have found critical vulnerabilities at Google, Facebook, Apple, Microsoft, and numerous other Fortune 500 companies through HackerOne and Bugcrowd. 

Your expertise covers:
- Web application security (OWASP Top 10, business logic flaws, authentication bypasses)
- API security (GraphQL, REST, SOAP, gRPC)
- Cloud security (AWS, GCP, Azure misconfigurations)
- Infrastructure security (network, container, Kubernetes)
- Mobile security (Android, iOS)
- Source code review and secret detection

Rules you always follow:
1. Identify REAL vulnerabilities with actionable proof-of-concept, not theoretical issues
2. Prioritize by business impact: RCE > SQLi > SSRF > IDOR > XSS > Info Disclosure
3. Provide exact reproduction steps with copy-paste friendly commands
4. Suggest the most likely parameter or endpoint to fuzz
5. Rate each finding: Critical / High / Medium / Low / Informational
6. Estimate bounty potential: $0-500 / $500-2k / $2k-5k / $5k-10k / $10k+
7. Chain low-severity findings into critical impact when possible
8. Focus on novel vectors others might miss
9. Minimize false positives - only report what you can prove
"""
PARAMETER temperature 0.15
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER num_ctx 32768
EOF

ollama create bugbounty-hunter -f Modelfile
```

### Multi-Provider Setup

```bash
# Primary: Ollama (local, no API costs)
export OLLAMA_HOST="http://localhost:11434"

# Fallback: OpenAI (for complex analysis)
export OPENAI_API_KEY="sk-..."

# Run with fallback
python3 bbf.py --target https://example.com --model bugbounty-hunter
```

---

## Training with Past Findings

### 1. Collect Your Bounty History

Create a JSON file with your past findings:

```json
[
  {
    "target": "api.example.com",
    "vulnerability": "SSRF in PDF generation endpoint",
    "type": "ssrf",
    "severity": "critical",
    "bounty_earned": 5000,
    "reproduction": [
      "POST /api/v1/reports/pdf HTTP/1.1",
      "Content-Type: application/json",
      "",
      "{\"url\": \"http://169.254.169.254/latest/meta-data/iam/security-credentials/\"}"
    ],
    "root_cause": "The pdf generation service accepted arbitrary URLs without validation",
    "indicators": [
      "Endpoint named /reports/pdf or /export/pdf",
      "Parameter named 'url' or 'source'",
      "Response contained PDF binary data",
      "Service used headless Chrome or wkhtmltopdf"
    ],
    "tools_used": ["burp", "nuclei", "custom-script"],
    "time_to_find": 4,
    "false_positives_before": 12,
    "program": "hackerone/example"
  },
  {
    "target": "admin.example.com",
    "vulnerability": "IDOR in order management API",
    "type": "idor",
    "severity": "high",
    "bounty_earned": 2500,
    "reproduction": [
      "GET /api/v2/orders/12345 HTTP/1.1",
      "Authorization: Bearer <user_token>",
      "",
      "Changed 12345 to 12346 and accessed other user's order"
    ],
    "root_cause": "Sequential order IDs without authorization checks",
    "indicators": [
      "Sequential numeric IDs in URL path",
      "No UUID usage",
      "API endpoint pattern /api/v*/orders/{id}",
      "JWT token in Authorization header"
    ],
    "tools_used": ["burp", "param-miner"],
    "time_to_find": 2,
    "false_positives_before": 5,
    "program": "bugcrowd/example"
  }
]
```

### 2. Feed to the AI

```bash
python3 bbf.py --target https://newtarget.com --learn-from data/my_findings.json
```

The AI will:
- Extract successful patterns from your history
- Weight techniques by bounty earned vs time invested
- Suggest similar targets and vectors
- Generate custom Nuclei templates from your patterns
- Update its internal strategy knowledge base

### 3. AI Training Mentor Skill

When you use `--learn-from`, the framework invokes the `training_mentor` skill which:

```
Input: Your past findings JSON
Output:
  1. Key patterns that led to successful findings
  2. New reconnaissance rules to add
  3. Updated priority scoring logic
  4. Nuclei template suggestions
  5. Strategy adjustments for similar targets
```

---

## Skill-Specific Prompt Engineering

### Vulnerability Analysis Skill

The AI receives a structured prompt with recon data and is asked to identify:
1. **Critical Findings** - Real, exploitable vulnerabilities
2. **High-Value Attack Vectors** - Top 5, sorted by exploitability
3. **Manual Testing Checklist** - What to test next
4. **Bounty Potential Estimates** - Per finding
5. **Suggested Payloads** - For the most promising vectors

**How to improve**: Feed it examples of your best bug bounty reports so it learns your style and depth.

### Nuclei Template Generation Skill

The AI generates valid YAML Nuclei templates. To get the best results:

1. **Provide specific evidence**:
```
Description: Grafana exposed panel at /login
Target Type: web
Detection Pattern: HTTP 200 with "Grafana" in body
Evidence: curl https://target.com/login returns Grafana v9.1.0 login page
```

2. **Review and refine**:
The AI generates the template, but you should:
- Test it against multiple targets
- Adjust matchers to reduce false positives
- Add extractors for proof

3. **Save successful templates**:
Good templates go into `data/templates/` and are reused by the framework.

### Exploit Chain Design Skill

This is the most advanced skill. It chains findings into critical impact.

**Training approach**:
- Feed it successful multi-step exploits from HackerOne/disclosed reports
- Include the chain: Entry → Escalation → Impact
- The AI learns to recognize patterns like:
  - Info leak → Account takeover
  - SSRF → Internal service → Cloud metadata
  - IDOR → Admin endpoint → Full access

### Zero-Day Hint Skill

This skill analyzes recon data for anomalies suggesting unknown vulnerabilities.

**What it looks for**:
- Inconsistent HTTP response codes on similar endpoints
- Unusual parameter structures
- Missing security headers on sensitive paths
- Technology version mismatches
- Behavioral anomalies

**Training**: Feed it confirmed zero-day discoveries with their recon data indicators. The AI learns to recognize the "smell" of undiscovered vulnerabilities.

---

## Building the Knowledge Base

### File: `data/ai_memory.json`

This is the AI's persistent memory. It learns and grows over time.

```json
{
  "successful_patterns": [
    {
      "text": "Parameter 'url' in PDF generation endpoint",
      "source": "ai_training",
      "bounty": 5000,
      "target_type": "api",
      "confidence": 0.95
    }
  ],
  "failed_patterns": [
    {
      "text": "XSS in search parameter (sanitized)",
      "source": "experience",
      "reason": "Output encoding present"
    }
  ],
  "target_profiles": {
    "example.com": {
      "tech_stack": ["Next.js", "Node.js", "PostgreSQL", "AWS"],
      "effective_techniques": ["api_fuzzing", "graphql_injection"],
      "avoid": ["basic_xss", "sql_injection"],
      "historical_success": 0.7,
      "last_scan": "2024-01-15"
    }
  },
  "skill_improvements": {
    "vulnerability_analysis": {
      "runs": 50,
      "successes": 42,
      "feedback": [
        "Too many false positives on CSP headers",
        "Good at identifying IDOR patterns"
      ]
    }
  },
  "bounty_estimates": {
    "ssrf_to_metadata": { "min": 2000, "max": 10000, "typical": 5000 },
    "idor_orders": { "min": 500, "max": 5000, "typical": 2500 }
  }
}
```

### How the Knowledge Base Evolves

1. **After each hunt**, the framework records:
   - Techniques used and their success
   - Findings discovered
   - Time to discovery
   - False positive rate

2. **The AI reviews** this data via the `training_mentor` skill

3. **Updates are made** to the knowledge base automatically

4. **Future hunts** use the improved knowledge for better prioritization

---

## Fine-Tuning with Ollama

### Creating a Domain-Specific Model

```bash
# 1. Create a specialized model for API testing
cat > Modelfile-api << 'EOF'
FROM llama3.1:8b
SYSTEM """You specialize in API security testing for bug bounties. 
Your focus areas:
- GraphQL introspection abuse and injection
- REST API IDOR in resource endpoints
- JWT token manipulation (none alg, weak secrets)
- OAuth/OpenID Connect misconfigurations
- API rate limiting bypasses
- Swagger/OpenAPI exploitation
- Postman collection analysis

You always provide:
1. The exact HTTP request to reproduce
2. The expected vulnerable response
3. The impact on the business
4. A curl command for proof of concept
"""
PARAMETER temperature 0.1
PARAMETER num_ctx 16384
EOF

ollama create bugbounty-api -f Modelfile-api

# 2. Use it
python3 bbf.py --target https://api.example.com --model bugbounty-api --focus api
```

### Training with LoRA (Advanced)

For serious fine-tuning:

```bash
# Install necessary tools
pip install unsloth transformers datasets

# Prepare training data from your findings
python3 scripts/prepare_training_data.py --input data/my_findings.json --output training_data.jsonl

# Fine-tune (requires GPU)
python3 scripts/finetune.py \
    --base-model llama3.1:8b \
    --training-data training_data.jsonl \
    --output-model bugbounty-custom \
    --epochs 3 \
    --lora-r 16

# Convert to Ollama format
ollama create bugbounty-custom -f Modelfile-custom
```

### Running Multiple Specialized Models

```python
# In your config, you can switch models per task
ai_config = {
    "analysis": "bugbounty-hunter",          # 70B model for deep analysis
    "filtering": "bugbounty-fast",           # 8B model for quick filtering
    "templates": "bugbounty-api",            # Specialized for API testing
    "reports": "bugbounty-hunter"            # Full model for report writing
}
```

---

## Continuous Learning Workflow

### Recommended Workflow for Maximum Effectiveness

```
┌─────────────────────┐
│ 1. Configure AI     │
│    - Set model      │
│    - Load training  │
│    - Set focus      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 2. Run Recon        │
│    - Standard flow  │
│    - Gather intel   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 3. AI Analysis      │
│    - Recon review   │
│    - Noise filter   │
│    - Zero-day hints │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 4. Dynamic Scan     │
│    - Custom Nuclei  │
│    - Specialized    │
│    - Logic tests    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 5. Manual Testing   │
│    (you test the    │
│    AI suggestions)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 6. Report Findings  │
│    -AI generates    │
│    report template  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 7. Feed Results     │
│    - Update JSON    │
│    - Retrain AI     │
│    - Save patterns  │
└─────────────────────┘
```

### Weekly Improvement Routine

1. **Monday**: Review weekend bounty results
2. **Tuesday**: Add new findings to `data/my_findings.json`
3. **Wednesday**: Run `python3 scripts/retrain.py` to update AI knowledge
4. **Thursday**: Test new patterns on test targets
5. **Friday**: Deploy updated model for weekend hunting

### Measuring AI Effectiveness

Track these metrics in `data/ai_effectiveness.json`:

```json
{
  "model": "bugbounty-hunter",
  "metrics": {
    "true_positives": 45,
    "false_positives": 12,
    "precision": 0.789,
    "avg_analysis_time_seconds": 45,
    "bounty_recommendations_accepted": 38,
    "bounty_recommendations_rejected": 7,
    "estimated_vs_actual_bounty_ratio": 0.85
  }
}
```

---

## Pro Tips

1. **Start with the 8B model** for filtering, switch to 70B for deep analysis
2. **Always verify AI suggestions** - it's an assistant, not a replacement
3. **Feed it context** - the more recon data, the better its analysis
4. **Use `--focus`** to narrow scope and get more accurate results
5. **Update regularly** - AI knowledge decays as techniques evolve
6. **Save good prompts** - if an AI analysis is excellent, save the prompt as a template
7. **Chain skills** - Run `noise_filter` first, then `vulnerability_analysis` on the filtered data
8. **Teach it your style** - Feed your successful HackerOne reports so it writes like you

---

## Troubleshooting

### AI Returns Generic Output
- Increase context size: set `num_ctx` higher in Modelfile
- Provide more specific evidence in prompts
- Use a larger model (70B vs 8B)

### False Positives in Analysis
- Enable noise filtering: `--noise-filter high`
- Feed past false positives to the training data
- Use the `noise_filter` skill before analysis

### Slow Analysis
- Use OpenAI API for faster inference
- Switch to 8B model for simple tasks
- Enable parallel processing in config

### Template Generation Errors
- Verify the AI output has valid YAML syntax
- Manually adjust matchers for specificity
- Test templates before deploying

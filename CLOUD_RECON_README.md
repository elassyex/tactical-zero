# 🌍 CLOUD RECON FOR ORY.COM
**Complete setup and execution guide**

---

## 📚 FILES CREATED

### **1. CLOUD_RECON_SETUP.md** (1,800+ lines)
Comprehensive guide with 6 cloud options:
- ✅ GitHub Codespaces (complete workflow)
- ✅ Google Colab (fast testing)
- ✅ AWS Lambda (serverless)
- ✅ Google Cloud Run (containers)
- ✅ PythonAnywhere (PaaS)
- ✅ Railway.app (easy setup)

### **2. QUICK_CLOUD_START.md** (300+ lines)
Quick start guides for each option with ready-to-run code:
- 2-minute Google Colab setup
- 5-minute GitHub Codespaces setup  
- 3-minute Railway.app setup

### **3. test_cloud_recon.sh** (200+ lines)
Automated test script to verify cloud environment:
- Checks Python version
- Checks all tools installed
- Checks all Python packages
- Tests subfinder, httpx, nuclei
- Shows installation commands if missing

---

## 🚀 GET STARTED IN 3 OPTIONS

### **OPTION 1: Google Colab (2 MINUTES)**
```python
# Open https://colab.research.google.com → New Notebook
# Run these cells:

# Install tools
!apt-get install -y subfinder assetfinder httpx naabu nuclei waybackurls gau katana ffuf amass findomain
!pip3 install ollama openai httpx pandas numpy transformers torch

# Clone framework
!git clone https://github.com/yourusername/bugbounty_framework.git
%cd bugbounty_framework
!pip3 install -r requirements.txt

# Run recon
import subprocess, os
ws = "/content/hunts/ory.com_" + datetime.now().strftime("%Y%m%d")
os.makedirs(ws, exist_ok=True)

subprocess.run(['subfinder', '-d', 'ory.com', '-silent', '-o', f'{ws}/subdomains.txt'])
subprocess.run(['httpx', '-l', f'{ws}/subdomains.txt', '-silent', '-o', f'{ws}/httpx.txt'])
subprocess.run(['nuclei', '-u', 'https://ory.com', '-o', f'{ws}/nuclei.txt'])

print(f"Results in {ws} - Download files from left sidebar")
```

### **OPTION 2: GitHub Codespaces (5 MINUTES)**
```bash
# Open https://github.com → New Repository → Create Codespace → Python 3
# In terminal:

cd /workspace
git clone https://github.com/yourusername/bugbounty_framework.git
cd bugbounty_framework
pip3 install -r requirements.txt

# Run recon
subfinder -d ory.com -silent -o hunts/ory.com_cloud_$(date +%Y%m%d)/subdomains.txt
httpx -l hunts/ory.com_cloud_$(date +%Y%m%d)/subdomains.txt -silent -o hunts/ory.com_cloud_$(date +%Y%m%d)/httpx.txt
nuclei -u https://ory.com -o hunts/ory.com_cloud_$(date +%Y%m%d)/nuclei.txt

# Download results from VS Code sidebar
```

### **OPTION 3: Railway.app (3 MINUTES)**
```bash
# Go to https://railway.app → Sign up with GitHub → New Project
# Select your bugbounty_framework repo → Wait for deployment

# Configure environment variables in Railway dashboard:
# - PYTHONUNBUFFERED=1
# - WORKSPACE=/app/hunts

# Deploy and it will run:
# python3 bbf_unified.py --target ory.com --mode local
```

---

## 🎯 QUICK TEST YOUR ENVIRONMENT

### **In Colab:**
```python
# Run this cell to test your environment
!bash test_cloud_recon.sh
```

### **In Codespaces:**
```bash
./test_cloud_recon.sh
```

### **In Railway:**
```bash
# Run in Railway console
bash test_cloud_recon.sh
```

---

## 📊 WHAT YOU'LL GET

### **Output Files:**
```
hunts/ory.com_cloud_20260720/
├── subdomains.txt        (all subdomains)
├── httpx.txt            (live URLs with status, title)
├── nuclei.txt           (vulnerabilities found)
├── dirb_results.txt     (directory enumeration)
├── gau_results.txt      (URL discovery)
└── full_scan.log        (detailed scan logs)
```

### **Tools Used:**
- **subfinder** - Subdomain enumeration (fast)
- **assetfinder** - Additional subdomain discovery
- **httpx** - Live HTTP checking, tech detection
- **nuclei** - Vulnerability scanning
- **ffuf** - Directory brute force
- **gau** - URL discovery from wayback machine

---

## 🔄 WORKFLOW SUMMARY

```
1. Choose cloud option (Colab > Codespaces > Railway)
2. Follow setup instructions (2-5 minutes)
3. Test environment (test_cloud_recon.sh)
4. Run recon (subfinder + httpx + nuclei)
5. Download results
6. Analyze findings
```

---

## 📝 TROUBLESHOOTING

### **If tools not installed:**
```bash
# Colab:
!apt-get install -y subfinder assetfinder httpx naabu nuclei waybackurls gau katana ffuf amass findomain

# Codespaces/Railway:
apt-get install -y subfinder assetfinder httpx naabu nuclei waybackurls gau katana ffuf amass findomain
```

### **If Python packages missing:**
```bash
pip3 install -r requirements.txt
```

### **If recon is slow:**
- Reduce timeout in commands
- Use `-timeout 30` flag
- Run in Cloud (always available internet)

---

## 🎯 RECOMMENDED SETUP

### **For Maximum Speed:**
1. **Google Colab** (2 min) → Quick testing
2. **GitHub Codespaces** (5 min) → Full features

### **For Production:**
1. **Railway.app** (3 min) → Auto-deployment
2. **Cloud Run** (15 min) → Container-based

### **For Cost-Effective:**
1. **AWS Lambda** (10 min) → Serverless
2. **Colab** (Free) → Quick testing

---

## ✅ QUICK CHECKLIST

- [ ] Choose cloud option
- [ ] Follow setup instructions
- [ ] Run test_cloud_recon.sh
- [ ] Install missing tools/packages
- [ ] Run subfinder
- [ ] Run httpx
- [ ] Run nuclei
- [ ] Download results
- [ ] Analyze findings

---

## 📁 ALL FILES LOCATION
```
/Users/mac/bugbounty_framework/
├── CLOUD_RECON_SETUP.md          ← Comprehensive guide
├── QUICK_CLOUD_START.md          ← Quick start guides
├── test_cloud_recon.sh           ← Environment test script
├── CLOUD_RECON_README.md         ← This file
└── bugsbounty_framework/
    ├── bbf_unified.py
    ├── agent_fixed.py
    ├── framework/
    └── hunts/
        └── ory.com_20260720/
            ├── ORY_ANALYSIS_REPORT.md
            ├── REAL_WORLD_TESTING.md
            └── QUICK_REFERENCE.md
```

---

## 🚀 START NOW!

```bash
# Option 1: Test your environment
./test_cloud_recon.sh

# Option 2: Read comprehensive guide
cat CLOUD_RECON_SETUP.md

# Option 3: Read quick start
cat QUICK_CLOUD_START.md
```

**Choose your cloud option and start recon on ORY.com!**

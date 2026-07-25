# 🚀 QUICK CLOUD RECON START
**Get started in 5 minutes**

---

## ⚡ OPTION 1: Google Colab (EASIEST - 2 MINUTES)

### **Step-by-Step:**

#### 1. Open Colab
```
https://colab.research.google.com → New Notebook
```

#### 2. Install Framework (One Cell)
```python
# Install bug bounty tools
!apt-get install -y subfinder assetfinder httpx naabu nuclei waybackurls gau katana ffuf amass findomain
!pip3 install ollama openai httpx pandas numpy transformers torch

# Clone your framework
!git clone https://github.com/yourusername/bugbounty_framework.git
%cd bugbounty_framework
!pip3 install -r requirements.txt

# Verify installation
!ls -la
!python3 -c "import bbf_unified; print('Framework ready!')"
```

#### 3. Run Recon (One Cell)
```python
import subprocess
import os
from datetime import datetime

# Setup workspace
ws = "/content/hunts/ory.com_" + datetime.now().strftime("%Y%m%d_%H%M%S")
os.makedirs(ws, exist_ok=True)

print(f"🚀 Running recon on: {ws}")

# Step 1: Subdomain enumeration
print("📊 Step 1: Subdomain enumeration...")
subprocess.run([
    'subfinder', '-d', 'ory.com', '-silent', '-o', f'{ws}/subdomains.txt'
])

# Step 2: HTTP enumeration
print("📊 Step 2: HTTP scanning...")
subprocess.run([
    'httpx', '-l', f'{ws}/subdomains.txt', '-silent', 
    '-title', '-status-code', '-tech-detect', '-o', f'{ws}/httpx.txt'
])

# Step 3: Nuclei scanning
print("📊 Step 3: Nuclei vulnerability scanning...")
subprocess.run([
    'nuclei', '-u', 'https://ory.com', '-o', f'{ws}/nuclei_results.txt',
    '-severity', 'critical,high,medium'
])

# Step 4: Parameter enumeration
print("📊 Step 4: Parameter discovery...")
subprocess.run([
    'ffuf', '-u', 'https://ory.com/FUZZ', '-w', '/usr/share/wordlists/dirb/common.txt',
    '-mr', '200', '-mc', '200,403,404', '-o', f'{ws}/dirb_results.txt'
])

# Step 5: Live HTTP scanning
print("📊 Step 5: Live HTTP scanning...")
subprocess.run([
    'gau', 'https://ory.com', '-subs', '-live', '-o', f'{ws}/gau_results.txt'
])

print(f"\n✅ RECON COMPLETE!")
print(f"📁 Results location: {ws}")
print(f"📊 Subdomains: $(wc -l < {ws}/subdomains.txt)")
print(f"📊 URLs: $(wc -l < {ws}/httpx.txt)")
print(f"📊 Vulns: $(wc -l < {ws}/nuclei_results.txt)")
print(f"\n📥 DOWNLOAD FILES: Click folders in left sidebar → Download .txt files")
```

#### 4. Visualize Results (Optional)
```python
# Show subdomains
with open(f'{ws}/subdomains.txt', 'r') as f:
    subs = f.read().splitlines()
    print(f"Found {len(subs)} subdomains:")
    for sub in subs[:10]:
        print(f"  • {sub}")
    if len(subs) > 10:
        print(f"  ... and {len(subs)-10} more")
```

---

## ⚡ OPTION 2: GitHub Codespaces (EASIEST - 5 MINUTES)

### **Step-by-Step:**

#### 1. Create Codespace
```
1. GitHub → New Repository → Create
2. Go to repository → Click "Code" → "Create Codespace"
3. Select "Dev Containers" → "Python 3"
4. Wait 2-3 minutes for environment to build
```

#### 2. Install Framework (Terminal)
```bash
# Clone your framework (if not already there)
cd /workspace
git clone https://github.com/yourusername/bugbounty_framework.git
cd bugbounty_framework

# Install Python packages
pip3 install -r requirements.txt

# Verify installation
python3 -c "import bbf_unified; print('✅ Framework installed')"
```

#### 3. Run Recon (Terminal)
```bash
# Create workspace
mkdir -p /workspace/hunts/ory.com_cloud_$(date +%Y%m%d)

# Run subdomain enumeration
subfinder -d ory.com -silent -o /workspace/hunts/ory.com_cloud_20260720/subdomains.txt

# Run HTTP enumeration
httpx -l /workspace/hunts/ory.com_cloud_20260720/subdomains.txt -silent -title -status-code -o /workspace/hunts/ory.com_cloud_20260720/httpx.txt

# Run nuclei
nuclei -u https://ory.com -o /workspace/hunts/ory.com_cloud_20260720/nuclei_results.txt -severity critical,high

# Run directory brute force
ffuf -u https://ory.com/FUZZ -w /usr/share/wordlists/dirb/common.txt -mr 200 -o /workspace/hunts/ory.com_cloud_20260720/dirb_results.txt

# View results
cat /workspace/hunts/ory.com_cloud_20260720/subdomains.txt | head -20
```

#### 4. Download Results
```
1. In VS Code, go to left sidebar "Explorer"
2. Navigate to /workspace/hunts/ory.com_cloud_20260720/
3. Right-click any file → "Download"
4. Or use terminal: scp -r /workspace/hunts/ory.com_cloud_20260720 username@your-machine:/path/to/destination
```

---

## ⚡ OPTION 3: Railway.app (FASTEST - 3 MINUTES)

### **Step-by-Step:**

#### 1. Create Railway Account
```
1. Go to: https://railway.app
2. Sign up with GitHub
3. Wait for dashboard to load
```

#### 2. Connect Repository
```
1. Click "New Project"
2. Select your GitHub repo
3. Wait for auto-detection
```

#### 3. Configure Environment
```json
{
  "PYTHONUNBUFFERED": "1",
  "WORKSPACE": "/app/hunts",
  "TARGET": "ory.com"
}
```

#### 4. Deploy and Run
```bash
# Add start command to process.json
{
  "start": "python3 /app/bbf_unified.py --target ory.com --mode local"
}

# Deploy
railway up

# Monitor deployment
railway logs
```

---

## 🎯 CHOOSE YOUR OPTION

### **Fastest to Test (2 minutes):**
✅ **Google Colab** - Just paste the code above and run

### **Easiest to Use (5 minutes):**
✅ **GitHub Codespaces** - VS Code in cloud, all features

### **Fastest Setup (3 minutes):**
✅ **Railway.app** - Connect repo, auto-deploy

---

## 📊 COMPARISON

| Feature | Colab | GitHub Codespaces | Railway |
|---------|-------|-------------------|---------|
| Setup Time | 2 min | 5 min | 3 min |
| Features | Basic | Complete | Good |
| GUI | Jupyter | VS Code | Dashboard |
| Cost | Free | Free | Free |
| Speed | Very Fast | Fast | Fast |
| Best For | Quick Testing | Complete Workflow | Auto-Deploy |

---

## 🚀 RECOMMENDED WORKFLOW

```
1. Try Google Colab first (2 minutes) → Quick results
2. Use GitHub Codespaces (5 minutes) → Full features
3. Deploy to Railway (3 minutes) → Auto-scaling
```

**Start now!** Choose option 1, 2, or 3 and run recon on ORY.com in the cloud.

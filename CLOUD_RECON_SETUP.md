# CLOUD RECON SETUP FOR ORY.COM
**Run Bug Bounty Framework in Cloud Environment**

---

## 🚀 OPTION 1: GitHub Codespaces (RECOMMENDED)
**Free tier available, cloud-based VS Code, built-in Python**

### Setup Instructions:

#### Step 1: Create GitHub Codespace
```
1. Go to: https://github.com
2. Create a new repository (or use existing one)
3. Click "Code" → "Create Codespace"
4. Select: "Dev Containers" → "Python 3"
5. Wait for environment to build (~2-5 minutes)
6. Opens in your browser with VS Code
```

#### Step 2: Clone Your Framework
```
# In the VS Code terminal:
cd /workspace
git clone https://github.com/yourusername/bugbounty_framework.git
cd bugbounty_framework

# Install dependencies
pip3 install -r requirements.txt
```

#### Step 3: Configure Cloud Environment
```
# Set up environment variables for cloud
export ORY_TARGET="https://ory.com"
export OLLAMA_HOST="ollama.ollama"  # Use cloud Ollama or default
export NUCLEI_TEMPLATES="/workspace/nuclei-templates"

# Verify environment
python3 -c "import sys; print(f'Python: {sys.version}')"
python3 -c "import httpx; print(f'httpx installed')"
python3 -c "import ollama; print(f'Ollama client installed')"
```

#### Step 4: Run Recon in Cloud
```
# Run unified framework
python3 bbf_unified.py \
  --target https://ory.com \
  --mode local \
  --phases discovery,scanning \
  --crucial

# Run agent_fixed.py
python3 agent_fixed.py \
  --target https://ory.com \
  --workspace /workspace/hunts/ory.com_cloud \
  --verbose
```

#### Step 5: Access Results
```
# Files are stored in /workspace/hunts/ory.com_cloud/
# You can download them:
# - Via VS Code terminal
# - Via GitHub repository
# - Via git push to share with team

# To save results to GitHub
cd /workspace/hunts/ory.com_cloud
git add .
git commit -m "ORY.com recon results"
git push
```

---

## 🚀 OPTION 2: Google Colab (EASY & FREE)
**Jupyter notebooks, cloud GPU, excellent internet**

### Setup Instructions:

#### Step 1: Create Google Colab
```
1. Go to: https://colab.research.google.com
2. Create new notebook
3. Change runtime to GPU (optional but recommended)
   Runtime → Change runtime type → GPU
```

#### Step 2: Install Dependencies
```
# Run in Colab cell:
!apt-get install -y subfinder
!apt-get install -y assetfinder
!apt-get install -y httpx
!apt-get install -y naabu
!apt-get install -y nuclei
!apt-get install -y waybackurls
!apt-get install -y gau
!apt-get install -y katana
!apt-get install -y ffuf
!apt-get install -y amass
!apt-get install -y findomain

!pip3 install ollama
!pip3 install openai
!pip3 install httpx
!pip3 install pandas
!pip3 install numpy
!pip3 install transformers
!pip3 install torch
!pip3 install requests
!pip3 install pyyaml
!pip3 install sqlalchemy
!pip3 install pydantic
```

#### Step 3: Clone Framework
```
# Clone from GitHub
!git clone https://github.com/yourusername/bugbounty_framework.git
%cd bugbounty_framework

# Install Python dependencies
!pip3 install -r requirements.txt
```

#### Step 4: Run Recon in Colab
```
# Python script to run recon
import subprocess
import os
import shutil
from datetime import datetime

# Setup workspace
ws = "/content/hunts/ory.com_cloud_" + datetime.now().strftime("%Y%m%d")
os.makedirs(ws, exist_ok=True)

print(f"Running recon on {ws}")

# Run subdomain enumeration
print("Starting subdomain enumeration...")
subprocess.run(["subfinder", "-d", "ory.com", "-silent", "-o", f"{ws}/subdomains.txt"])

# Run asset enumeration
print("Starting asset enumeration...")
subprocess.run(["assetfinder", "--subs-only", "ory.com", ">", f"{ws}/asset_subs.txt"])

# Run httpx
print("Starting httpx scan...")
subprocess.run(["httpx", "-l", f"{ws}/subdomains.txt", "-silent", "-title", "-status-code"], cwd=ws)

# Run nuclei
print("Starting nuclei scan...")
subprocess.run(["nuclei", "-u", "https://ory.com", "-o", f"{ws}/nuclei_results.txt"], cwd=ws)

print(f"Recon complete! Results in: {ws}")
print("Download files from left sidebar")
```

#### Step 5: Visual Analysis in Colab
```
# Analyze results in notebook
import pandas as pd

# Read results
df = pd.read_csv(f"{ws}/subdomains.txt", header=None, names=['domain'])
print(f"Found {len(df)} subdomains")

# Live map with folium (if available)
```

---

## 🚀 OPTION 3: AWS Lambda (PYTHON SCRIPTS)
**Serverless, cost-effective, instant scaling**

### Setup Instructions:

#### Step 1: Create AWS Account
```
1. Go to: https://aws.amazon.com/
2. Create free tier account
3. Go to AWS Lambda console
4. Create new function
```

#### Step 2: Create Lambda Function
```
1. Name: ory-recon-scanner
2. Runtime: Python 3.11
3. Role: Basic Lambda execution role
4. Memory: 1024 MB
5. Timeout: 15 minutes
```

#### Step 3: Upload Framework Code
```
# Zip your framework files
zip -r ory-recon.zip bbf_unified.py agent_fixed.py framework/

# Upload to Lambda
# Or use AWS CLI:
aws lambda create-function \
  --function-name ory-recon-scanner \
  --runtime python3.11 \
  --handler ory_recon.lambda_handler \
  --zip-file fileb://ory-recon.zip \
  --role arn:aws:iam::123456789012:role/LambdaExecutionRole
```

#### Step 4: Create Lambda Handler
```python
# ory_recon.py
import os
import subprocess
import boto3
from datetime import datetime

def lambda_handler(event, context):
    target = event.get('target', 'https://ory.com')
    workspace = f"/tmp/hunts/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(workspace, exist_ok=True)
    
    # Run subfinder
    subprocess.run([
        'subfinder', '-d', target.replace('https://', '').replace('http://', ''),
        '-silent', '-o', f'{workspace}/subdomains.txt'
    ])
    
    # Run httpx
    subprocess.run([
        'httpx', '-l', f'{workspace}/subdomains.txt',
        '-silent', '-o', f'{workspace}/httpx_results.txt'
    ])
    
    # Run nuclei
    subprocess.run([
        'nuclei', '-u', target,
        '-o', f'{workspace}/nuclei_results.txt'
    ])
    
    return {
        'statusCode': 200,
        'body': f'Recon complete! Results in {workspace}'
    }
```

#### Step 5: Test Lambda Function
```
# Test from AWS Console
{
  "target": "https://ory.com"
}

# Or use AWS CLI
aws lambda invoke \
  --function-name ory-recon-scanner \
  --payload '{"target": "https://ory.com"}' \
  response.json
```

---

## 🚀 OPTION 4: Google Cloud Run (EASY TO SETUP)
**Container-based, auto-scaling, no servers**

### Setup Instructions:

#### Step 1: Create GCP Project
```
1. Go to: https://console.cloud.google.com
2. Create new project
3. Enable Cloud Run API
```

#### Step 2: Create Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system tools
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy framework
COPY . .

# Install Python packages
RUN pip install -r requirements.txt

# Install bug bounty tools
RUN curl -fsSL https://subfinder.dev/install.sh | bash
RUN curl -fsSL https://get.oxeye.ai/katana/latest | tar -xzO katana > /usr/local/bin/katana
RUN curl -fsSL https://get.oxeye.ai/nuclei/latest | tar -xzO nuclei > /usr/local/bin/nuclei
RUN chmod +x /usr/local/bin/katana /usr/local/bin/nuclei

# Default command
CMD ["python3", "bbf_unified.py", "--target", "ory.com", "--mode", "local"]
```

#### Step 3: Build and Deploy
```bash
# Build container
gcloud builds submit --tag gcr.io/YOUR_PROJECT/ory-recon

# Deploy to Cloud Run
gcloud run deploy ory-recon-scanner \
  --source gcr.io/YOUR_PROJECT/ory-recon \
  --platform managed \
  --allow-unauthenticated
```

#### Step 4: Run Recon
```
# Get deployment URL
gcloud run services describe ory-recon-scanner

# Invoke function
curl -X POST "https://YOUR_PROJECT_REGION.run.app" \
  -H "Content-Type: application/json" \
  -d '{"target": "https://ory.com"}'
```

---

## 🚀 OPTION 5: PythonAnywhere (SIMPLE PaaS)
**Easy to use, good for scripts**

### Setup Instructions:

#### Step 1: Create PythonAnywhere Account
```
1. Go to: https://www.pythonanywhere.com
2. Sign up for free tier
3. Create a new web app (Flask recommended)
```

#### Step 2: Upload Framework
```
# Use their web file browser or SSH
scp -r /Users/mac/bugbounty_framework username@pythonanywhere.com:/home/username/
```

#### Step 3: Configure Web App
```
1. Go to "Web" tab
2. Create new web app
3. Select Python 3.11
4. Add to "WSGI custom file":
   from bugbounty_framework.bbf_unified import main
```

#### Step 4: Run Recon
```
1. Add cron job to run recon daily
2. Run from Python console
3. View results in web interface
```

---

## 🚀 OPTION 6: Railway.app (FAST SETUP)
**Free tier, good for Python projects**

### Setup Instructions:

#### Step 1: Create Railway Account
```
1. Go to: https://railway.app
2. Sign up with GitHub
3. Create new project
```

#### Step 2: Connect GitHub Repository
```
1. Connect your GitHub repo with bugbounty_framework
2. Railway auto-detects Python project
```

#### Step 3: Configure Environment
```
1. Add environment variables:
   - PYTHONUNBUFFERED=1
   - WORKSPACE=/app/hunts

2. Add build steps:
   - pip install -r requirements.txt
   - git clone nuclei-templates /app/nuclei-templates
```

#### Step 4: Deploy and Run
```
# Add a start command to process.json:
{
  "start": "python3 bbf_unified.py --target ory.com --mode local"
}

# Deploy automatically runs the command
```

---

## 📊 COMPARISON TABLE

| Option | Cost | Setup Time | Ease of Use | Internet Access | Best For |
|--------|------|------------|-------------|----------------|----------|
| GitHub Codespaces | Free tier | 5-10 min | ⭐⭐⭐⭐⭐ | ✅ Excellent | Complete workflow |
| Google Colab | Free | 2 min | ⭐⭐⭐⭐⭐ | ✅ Excellent | Fast testing |
| AWS Lambda | Free tier | 10-15 min | ⭐⭐⭐ | ✅ Good | Python scripts |
| Cloud Run | Free tier | 15-20 min | ⭐⭐⭐⭐ | ✅ Good | Containers |
| PythonAnywhere | Free | 10 min | ⭐⭐⭐⭐ | ✅ Good | Easy deployment |
| Railway.app | Free | 5 min | ⭐⭐⭐⭐⭐ | ✅ Excellent | Quick setup |

---

## 🎯 RECOMMENDED WORKFLOW

### **For Maximum Speed & Ease:**
1. **Google Colab** (for fast testing and visualization)
2. **GitHub Codespaces** (for complete framework execution)

### **For Production Use:**
1. **Railway.app** (easiest setup, auto-scaling)
2. **Cloud Run** (container-based, good scaling)

### **For Cost-Effective:**
1. **AWS Lambda** (serverless, minimal cost)
2. **Google Colab** (free tier available)

---

## 📝 QUICK START GUIDE

### **Option 1: GitHub Codespaces (Recommended)**

```bash
# 1. Open https://github.com → New Repository
# 2. Create Codespace → Select Python 3
# 3. In terminal:
cd /workspace
git clone https://github.com/yourusername/bugbounty_framework.git
cd bugbounty_framework
pip3 install -r requirements.txt

# 4. Run recon:
python3 bbf_unified.py --target https://ory.com --mode local --phases discovery,scanning

# 5. Download results from VS Code sidebar
```

### **Option 2: Google Colab**

```python
# 1. Create Colab notebook
# 2. Run these cells:

# Install tools
!apt-get install -y subfinder assetfinder httpx naabu nuclei waybackurls gau katana ffuf amass findomain
!pip3 install ollama openai httpx pandas numpy transformers torch

# Clone framework
!git clone https://github.com/yourusername/bugbounty_framework.git
%cd bugbounty_framework
!pip3 install -r requirements.txt

# Run recon
import subprocess
ws = "/content/hunts/ory.com_" + datetime.now().strftime("%Y%m%d")
os.makedirs(ws, exist_ok=True)

subprocess.run(['subfinder', '-d', 'ory.com', '-silent', '-o', f'{ws}/subdomains.txt'])
subprocess.run(['httpx', '-l', f'{ws}/subdomains.txt', '-silent', '-o', f'{ws}/httpx.txt'])
subprocess.run(['nuclei', '-u', 'https://ory.com', '-o', f'{ws}/nuclei.txt'])

print(f"Results in {ws}")
```

---

## 🚀 BEST CLOUD RECON WORKFLOW

```
1. Google Colab for quick testing → Run frameworks → Visualize results
2. GitHub Codespaces for complete workflow → Full feature access
3. Railway.app for production → Auto-deployment → Auto-scaling

Priority: GitHub Codespaces → Google Colab → Railway.app
```

---

## 📁 Files Created:
- `/Users/mac/bugbounty_framework/CLOUD_RECON_SETUP.md` - Complete cloud setup guide
- `/Users/mac/bugbounty_framework/hunts/ory.com_20260720/ORY_ANALYSIS_REPORT.md`
- `/Users/mac/bugbounty_framework/hunts/ory.com_20260720/REAL_WORLD_TESTING.md`
- `/Users/mac/bugbounty_framework/hunts/ory.com_20260720/QUICK_REFERENCE.md`

**Ready to run!** Choose your preferred cloud option and start recon on ORY.com.

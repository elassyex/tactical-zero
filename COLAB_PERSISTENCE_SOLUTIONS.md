# 🔧 GOOGLE COLAB: FILES PERSIST FOREVER (NO DELETION)
**Permanent solution - works even if Colab crashes**

---

## ⚠️ **WHY YOUR FILES GET DELETED**

Colab deletes everything in `/content/` when:
- Session disconnects
- Page refreshes
- 90 min inactivity timeout
- 12 hour session limit
- Browser closes

**Google Drive is NOT enough if you don't download files.**

---

## ✅ **SOLUTION 1: SAVE TO GITHUB (BEST - FOREVER PERSISTENCE)**

### **Step 1: Create GitHub Repository**
```
1. Go to https://github.com/new
2. Create a new repository named "bugbounty-results"
3. Make it Public
4. Do NOT initialize with README
```

### **Step 2: Install Git in Colab**
```python
!apt-get install -y git
!pip3 install gitpython

import git
import os
import shutil
```

### **Step 3: Clone Your Repository**
```python
# Clone to /content
!git clone https://github.com/YOUR_USERNAME/bugbounty-results.git
os.chdir('/content/bugbounty-results')

# Configure git
!git config user.email "your-email@example.com"
!git config user.name "Your Name"
!git branch -M main
```

### **Step 4: Run reconftw**
```python
!cd /content/reconftw && ./reconftw.sh -d ory.com -r --ai
```

### **Step 5: Save Results to GitHub (AFTER reconftw)**
```python
# Copy all results to your repo
!cp -r /content/reconftw/* .

# Commit and push
!git add .
!git commit -m "Recon results - $(date)" 
!git push

print("✅ Results saved to GitHub!")
print("🔗 https://github.com/YOUR_USERNAME/bugbounty-results")
```

### **Step 6: Download When Needed**
```
Go to: https://github.com/YOUR_USERNAME/bugbounty-results
All files will be there forever
```

---

## ✅ **SOLUTION 2: AUTOMATED GITHUB BACKUP (RUN THIS ONCE)**

```python
from google.colab import drive
import os
import git
import shutil
from datetime import datetime

# 1. Mount Google Drive
drive.mount('/content/drive', force_remount=True)

# 2. Setup paths
drive_path = '/content/drive/MyDrive/bugbounty-results'
os.makedirs(drive_path, exist_ok=True)

# 3. Create GitHub repo if it doesn't exist
GITHUB_REPO = "https://github.com/YOUR_USERNAME/bugbounty-results.git"
GIT_DIR = "/content/bugbounty-results"

if os.path.exists(GIT_DIR):
    os.system(f"cd {GIT_DIR} && git pull")
else:
    os.system(f"git clone {GITHUB_REPO} {GIT_DIR}")
    os.chdir(GIT_DIR)
    !git config user.email "your-email@example.com"
    !git config user.name "Your Name"
    !git branch -M main
else:
    os.chdir(GIT_DIR)
    !git pull

# 4. Copy reconftw results to GitHub
!cp -r /content/reconftw/* .

# 5. Commit and push
!git add .
!git commit -m f"Recon results - {datetime.now().strftime('%Y-%m-%d %H:%M')}" -m "ory.com recon"
!git push

print("✅ All results saved to GitHub!")
print(f"📁 Repository: {GITHUB_REPO}")
```

---

## ✅ **SOLUTION 3: DOWNLOAD BEFORE EACH ACTION**

### **The ONLY way to guarantee persistence:**

```python
from google.colab import files
import os

def save_and_download_all():
    """Download everything before any action"""
    
    # 1. Save to Google Drive first
    save_path = '/content/drive/MyDrive/reconftw/ory.com'
    os.makedirs(save_path, exist_ok=True)
    
    for file in os.listdir('/content/reconftw'):
        if file.endswith('.txt'):
            shutil.copy2(f'/content/reconftw/{file}', save_path)
    
    # 2. Download NOW (before you do anything else)
    !tar -czf ory-results.tar.gz -C /content/reconftw .
    files.download('ory-results.tar.gz')
    files.download('/content/drive/MyDrive/reconftw/ory-results.tar.gz')
    
    print("✅ Results downloaded - safe to continue")

# Call this BEFORE each major step
save_and_download_all()
```

---

## ✅ **SOLUTION 4: AUTOMATIC BACKUP EVERY 10 MINUTES**

```python
from google.colab import drive
import os
import shutil
from google.colab import files

def auto_backup():
    """Save and download every 10 minutes"""
    save_path = '/content/drive/MyDrive/reconftw/ory.com'
    os.makedirs(save_path, exist_ok=True)
    
    for file in os.listdir('/content/reconftw'):
        if file.endswith('.txt'):
            shutil.copy2(f'/content/reconftw/{file}', save_path)
    
    !tar -czf ory-results.tar.gz -C /content/reconftw .
    files.download('ory-results.tar.gz')

import time

print("🔄 Auto-backup every 10 minutes started...")
while True:
    try:
        auto_backup()
        print(f"✅ Backed up at {time.strftime('%H:%M:%S')}")
    except:
        pass
    time.sleep(600)  # 10 minutes
```

---

## ✅ **SOLUTION 5: GOOGLE COLAB RUNTIME (PAYMENT REQUIRED)**

### **For UNLIMITED persistence:**

```
1. Go to Runtime → Change runtime type
2. Select "High RAM" or "Pro"
3. Use "8 GB" RAM (paid)
4. Session will NOT be deleted after 12 hours
5. Files saved to /content/ will persist
```

**Cost:** ~$10/month

---

## 🎯 **THE REAL SOLUTION: USE GITHUB**

### **Why GitHub is better than Drive:**
- ✅ No download needed
- ✅ Files saved automatically
- ✅ Access from anywhere
- ✅ Never deleted
- ✅ Version history

### **One command to save everything:**
```python
!cd /content/bugbounty-results && cp -r /content/reconftw/* . && git add . && git commit -m "recon" && git push
```

---

## 🚀 **QUICK START: GITHUB SOLUTION**

```python
# 1. Install git
!apt-get install -y git
!pip3 install gitpython

# 2. Clone your GitHub repo (replace YOUR_USERNAME)
!git clone https://github.com/YOUR_USERNAME/bugbounty-results.git
%cd bugbounty-results
!git config user.email "you@example.com"
!git config user.name "Your Name"

# 3. Run reconftw
%cd /content/reconftw
!./reconftw.sh -d ory.com -r --ai

# 4. Save to GitHub (automatic)
%cd /content/bugbounty-results
!cp -r /content/reconftw/* .
!git add .
!git commit -m "ory.com recon - $(date)" 
!git push

print("✅ DONE - Check: https://github.com/YOUR_USERNAME/bugbounty-results")
```

---

## 📋 **COMPARISON TABLE**

| Solution | Persists on Disconnect? | Access | Cost |
|----------|------------------------|--------|------|
| Google Drive | ❌ Only if downloaded | ✅ Yes | Free |
| GitHub | ✅ YES | ✅ Yes | Free |
| Downloads | ✅ YES (after download) | ✅ Yes | Free |
| Runtime | ✅ YES | ✅ Yes | Paid |
| Auto-backup | ✅ YES (periodic) | ✅ Yes | Free |

---

## ✅ **FINAL ANSWER: Use GitHub**

```python
# Save everything to GitHub (forever)
!git clone https://github.com/YOUR_USERNAME/bugbounty-results.git
%cd bugbounty-results
!cp -r /content/reconftw/* .
!git add .
!git commit -m "recon results"
!git push

# Done! Files are forever saved on GitHub
```

**GitHub is the only solution that guarantees files survive disconnects.** 🔧

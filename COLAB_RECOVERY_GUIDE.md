# 🔧 COLAB RECOVERY - SAVE YOUR DELETED RESULTS
**How to save results before they're gone**

---

## 🚨 **IF YOU STILL HAVE ACCESS TO COLAB SESSION**

### **STEP 1: Check for Remaining Files**
```python
# List all files in /content
!ls -la /content/

# Check hunts directory
!ls -la /content/hunts/

# Look for your ORY.com results
!find /content -name "*ory*" -type f
!find /content -name "*20260720*" -type f
```

### **STEP 2: Download Individual Files**
```python
from google.colab import files

# Download subdomains.txt if found
!ls /content/hunts/  # See what's available

# Download each file
files.download('/content/hunts/ory.com_results/subdomains.txt')
files.download('/content/hunts/ory.com_results/httpx.txt')
files.download('/content/hunts/ory.com_results/nuclei.txt')
```

### **STEP 3: Download All as Tarball**
```python
# Create tarball of all remaining files
!tar -czf remaining-results.tar.gz /content/hunts/

# Download the tarball
files.download('remaining-results.tar.gz')
```

---

## ✅ **IF SESSION EXPIRED - USE ABOVE SCRIPTS**

### **RUN THIS SCRIPT (COPY PASTE INTO NEW COLAB)**

```python
from google.colab import drive
import os
import subprocess

# Mount Drive
drive.mount('/content/drive')

# Setup paths
drive_path = '/content/drive/MyDrive/bugbounty/ory.com'
os.makedirs(drive_path, exist_ok=True)

# Check if files exist
!ls /content/hunts/

# Save what we can
if os.path.exists('/content/hunts/ory.com_results'):
    for file in os.listdir('/content/hunts/ory.com_results'):
        src = f'/content/hunts/ory.com_results/{file}'
        dst = f'{drive_path}/{file}'
        !cp "{src}" "{dst}"
        files.download(dst)
        print(f"✅ Downloaded: {file}")

print("✅ Recovery complete! Check Google Drive.")
```

---

## 🎯 **PREVENT FUTURE DATA LOSS**

### **USE THE MASTER PERSISTENCE SCRIPT**

```python
# Run this exact script
from google.colab import drive
import os
import subprocess
import datetime

# Configuration
TARGET = "ory.com"
SAVE_FREQUENCY = 300
DRIVE_PATH = f'/content/drive/MyDrive/bugbounty/{TARGET}'

# Mount Drive
drive.mount('/content/drive')

# Create folders
os.makedirs(DRIVE_PATH, exist_ok=True)
temp_path = f'/content/hunts/{TARGET}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}'
os.makedirs(temp_path, exist_ok=True)

# Run recon
print("🎯 Running recon...")
subprocess.run(['subfinder', '-d', TARGET, '-silent', '-o', f'{temp_path}/subdomains.txt'])
subprocess.run(['httpx', '-l', f'{temp_path}/subdomains.txt', '-silent', '-o', f'{temp_path}/httpx.txt'])
subprocess.run(['nuclei', '-u', f'https://{TARGET}', '-o', f'{temp_path}/nuclei.txt'])

# Save to Drive
print("💾 Saving to Google Drive...")
for file in ['subdomains.txt', 'httpx.txt', 'nuclei.txt']:
    if os.path.exists(f'{temp_path}/{file}'):
        !cp "{temp_path}/{file}" "{DRIVE_PATH}/"
        files.download(f'{DRIVE_PATH}/{file}')

# Download all
!tar -czf ory-results.tar.gz -C {temp_path} .
files.download('ory-results.tar.gz')

print("✅ All results saved and downloaded!")
print(f"📁 Google Drive: {DRIVE_PATH}")
```

---

## 📊 **IMMEDIATE ACTION PLAN**

### **If you still have Colab access:**
1. ⚡ **Download ALL files now**
2. ⚡ **Mount Google Drive**
3. ⚡ **Save to Drive**
4. ⚡ **Download tarball**

### **If Colab is closed:**
1. ⚡ **Run master persistence script** (copy paste in new Colab)
2. ⚡ **Set up auto-save**
3. ⚡ **Use Telegram notifications**
4. ⚡ **Push to GitHub**

---

## 📝 **SUMMARY**

### **Always do this now:**
```python
from google.colab import files

# Download what you have
files.download('/content/hunts/your-results-folder/*')

# Or create tarball
!tar -czf backup.tar.gz /content/hunts/
files.download('backup.tar.gz')
```

### **Future protection:**
- ✅ Mount Google Drive before recon
- ✅ Save to Drive after each step
- ✅ Download files immediately
- ✅ Use master persistence script
- ✅ Set up auto-save loop

---

**NOW: Save your results before they're gone!**

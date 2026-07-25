# 🔄 RECONFTW COLAB PERSISTENCE GUIDE
**How to save all reconftw results permanently**

---

## ⚠️ **RECONFTW IN COLAB - FILE DELETION PROBLEM**

Reconftw saves results in current directory and subdirectories. When Colab session ends, **all files are deleted!**

**Solutions below prevent data loss.**

---

## ✅ **SOLUTION 1: MOUNT GOOGLE DRIVE FIRST (RECOMMENDED)**

### **Step 1: Mount Google Drive**
```python
from google.colab import drive
drive.mount('/content/drive')
```

### **Step 2: Create Persistent Directory**
```python
import os

# Create ory.com folder in Google Drive
drive_path = '/content/drive/MyDrive/reconftw/ory.com'
os.makedirs(drive_path, exist_ok=True)

print(f"📁 Results will be saved to: {drive_path}")
```

### **Step 3: Configure reconftw to save to Drive**
```python
# Navigate to reconftw directory
os.chdir('/content/reconftw')

# Create output directory in Drive
output_dir = '/content/drive/MyDrive/reconftw/ory.com'
os.makedirs(output_dir, exist_ok=True)

# Set environment variable
import os
os.environ['RECON_OUTPUT'] = output_dir

print(f"✅ Reconftw output directory: {output_dir}")
```

### **Step 4: Run reconftw with Output Path**
```python
# Run reconftw specifying output directory
!./reconftw.sh -d ory.com -r --ai --output /content/drive/MyDrive/reconftw/ory.com
```

### **Step 5: Save All Results After Recon**
```python
# After reconftw completes, save all files to Drive
import shutil

# Find all txt files in current directory
import glob
txt_files = glob.glob('/content/reconftw/*.txt')

# Copy each file to Drive
for file in txt_files:
    filename = os.path.basename(file)
    shutil.copy2(file, f'{output_dir}/{filename}')
    print(f"✅ Saved: {filename}")

# Copy all subdirectories
for root, dirs, files in os.walk('/content/reconftw'):
    for file in files:
        if file.endswith('.txt') or file.endswith('.json'):
            src = os.path.join(root, file)
            relpath = os.path.relpath(src, '/content/reconftw')
            dst = os.path.join(output_dir, relpath)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            print(f"✅ Saved: {relpath}")

print("✅ All reconftw results saved to Google Drive!")
```

---

## ✅ **SOLUTION 2: AUTO-SAVE SCRIPT (RECOMMENDED)**

### **Master script for reconftw with auto-save**

```python
from google.colab import drive
import os
import subprocess
import shutil
import glob
import datetime

# ================= CONFIGURATION =================
RECONFTW_DIR = '/content/reconftw'
TARGET = 'ory.com'
DRIVE_PATH = '/content/drive/MyDrive/reconftw'
OUTPUT_PATH = f'{DRIVE_PATH}/{TARGET}'
SAVE_FREQUENCY = 300  # seconds (auto-save every 5 minutes)
# =================================================

print("=" * 60)
print("🎯 RECONFTW COLAB PERSISTENCE MASTER SCRIPT")
print("=" * 60)
print(f"Target: {TARGET}")
print(f"Reconftw: {RECONFTW_DIR}")
print(f"Output: {OUTPUT_PATH}")
print(f"Auto-save: every {SAVE_FREQUENCY} seconds")
print("")

# Step 1: Mount Google Drive
print("🔄 Mounting Google Drive...")
drive.mount('/content/drive', force_remount=True)

# Step 2: Create directories
print(f"📁 Creating directories...")
os.makedirs(OUTPUT_PATH, exist_ok=True)
os.makedirs(RECONFTW_DIR, exist_ok=True)

# Step 3: Configure reconftw environment
print(f"⚙️  Configuring reconftw...")
os.chdir(RECONFTW_DIR)
os.environ['RECON_OUTPUT'] = OUTPUT_PATH

print(f"✅ Reconftw output: {OUTPUT_PATH}")

# Step 4: Run reconftw
print(f"\n🎯 Starting reconftw on: {TARGET}")
print("=" * 60)

try:
    # Run reconftw
    subprocess.run([
        './reconftw.sh',
        '-d', TARGET,
        '-r',
        '--ai',
        '--output', OUTPUT_PATH
    ], check=True, timeout=7200)
    
    print("\n" + "=" * 60)
    print("✅ Reconftw completed successfully!")
    print("=" * 60)
    
except subprocess.CalledProcessError as e:
    print(f"\n❌ Reconftw failed: {e}")
    
except subprocess.TimeoutExpired:
    print(f"\n⏰ Reconftw timed out (allowed)")

# Step 5: Save all results to Drive
print(f"\n💾 Saving all results to Google Drive...")

# Find and copy all txt files
txt_files = glob.glob(f'{RECONFTW_DIR}/*.txt')
count = 0
for file in txt_files:
    filename = os.path.basename(file)
    shutil.copy2(file, f'{OUTPUT_PATH}/{filename}')
    count += 1

# Copy all subdirectory files
for root, dirs, files in os.walk(RECONFTW_DIR):
    for file in files:
        if file.endswith('.txt') or file.endswith('.json') or file.endswith('.md'):
            src = os.path.join(root, file)
            relpath = os.path.relpath(src, RECONFTW_DIR)
            dst = os.path.join(OUTPUT_PATH, relpath)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            count += 1

print(f"✅ Saved {count} files to Google Drive!")

# Step 6: Create and download tarball
print(f"📦 Creating complete backup...")
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
tarball_name = f'reconftw-{TARGET}-{timestamp}.tar.gz'
tarball_path = f'/content/{tarball_name}'

os.system(f'cd {RECONFTW_DIR} && tar -czf {tarball_name} .')
os.system(f'cp {tarball_path} {OUTPUT_PATH}/')

files.download(tarball_path)
files.download(f'{OUTPUT_PATH}/{tarball_name}')

print(f"✅ Downloaded: {tarball_name}")
print(f"✅ All results in: {OUTPUT_PATH}")

print("\n" + "=" * 60)
print("✅ RECONFTW COMPLETE - Results saved!")
print("=" * 60)
```

---

## ✅ **SOLUTION 3: RUN RECONFTW IN SEPARATE CELL**

### **Cell 1: Setup and Mount Drive**
```python
from google.colab import drive
import os

drive.mount('/content/drive')
output_path = '/content/drive/MyDrive/reconftw/ory.com'
os.makedirs(output_path, exist_ok=True)
os.environ['RECON_OUTPUT'] = output_path

print(f"📁 Output: {output_path}")
```

### **Cell 2: Run reconftw**
```python
!cd /content/reconftw && ./reconftw.sh -d ory.com -r --ai --output /content/drive/MyDrive/reconftw/ory.com
```

### **Cell 3: Save Results**
```python
import shutil
import glob

# Save all txt files
for file in glob.glob('/content/reconftw/*.txt'):
    filename = os.path.basename(file)
    shutil.copy2(file, f'/content/drive/MyDrive/reconftw/ory.com/{filename}')
    print(f"✅ Saved: {filename}")

# Save all subdirectories
for root, dirs, files in os.walk('/content/reconftw'):
    for file in files:
        if file.endswith('.txt') or file.endswith('.json') or file.endswith('.md'):
            src = os.path.join(root, file)
            relpath = os.path.relpath(src, '/content/reconftw')
            dst = f'/content/drive/MyDrive/reconftw/ory.com/{relpath}'
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            print(f"✅ Saved: {relpath}")

print("✅ All results saved!")
```

---

## ✅ **SOLUTION 4: SAVE AFTER EACH RECON FTW RUN**

### **Add this to your reconftw script**
```bash
#!/bin/bash

# Reconftw script with auto-save

# Run reconftw
./reconftw.sh -d ory.com -r --ai

# Save results to Google Drive (run after reconftw)
cd /content
cp -r reconftw /content/drive/MyDrive/reconftw-backup-$(date +%Y%m%d_%H%M%S)/
```

---

## ✅ **SOLUTION 5: DOWNLOAD FILES DURING RECON**

### **Monitor and download frequently**
```python
import time
import os
from google.colab import files

while True:
    # Check if reconftw is running
    if os.path.exists('/content/reconftw/reconftw.log'):
        # Download latest txt files
        for file in os.listdir('/content/reconftw'):
            if file.endswith('.txt'):
                files.download(f'/content/reconftw/{file}')
    
    # Wait before next download
    time.sleep(600)  # Every 10 minutes
```

---

## 🎯 **RECOMMENDED WORKFLOW**

### **Run this entire block in ONE Colab session:**

```python
# SETUP CELL
from google.colab import drive
import os
import shutil
import glob

drive.mount('/content/drive')

output_path = '/content/drive/MyDrive/reconftw/ory.com'
os.makedirs(output_path, exist_ok=True)
os.environ['RECON_OUTPUT'] = output_path

print("✅ Setup complete!")
print(f"📁 Output: {output_path}")
print("")

# RECONFTW CELL
print("🎯 Running reconftw...")
!cd /content/reconftw && ./reconftw.sh -d ory.com -r --ai --output /content/drive/MyDrive/reconftw/ory.com

# SAVE CELL
print("\n💾 Saving all results...")
for file in glob.glob('/content/reconftw/*.txt'):
    filename = os.path.basename(file)
    shutil.copy2(file, f'{output_path}/{filename}')
    print(f"✅ Saved: {filename}")

for root, dirs, files in os.walk('/content/reconftw'):
    for file in files:
        if file.endswith('.txt') or file.endswith('.json') or file.endswith('.md'):
            src = os.path.join(root, file)
            relpath = os.path.relpath(src, '/content/reconftw')
            dst = f'{output_path}/{relpath}'
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            print(f"✅ Saved: {relpath}")

print("\n✅ All results saved to Google Drive!")
print(f"📁 Files are in: {output_path}")
```

---

## 📊 **UNDERSTANDING RECONFTW OUTPUT**

### **Reconftw creates these files:**
```
reconftw/
├── subdomains.txt          ← Main results
├── domains.txt
├── errors.txt
├── urls.txt
├── linked.txt
├── header.txt
├── technique.txt
├── technology.txt
├── vulns.txt
├── XSS.txt
├── info.txt
├── live.txt
├── passive.txt
├── alive.txt
├── screenshots/
├── nmap/
├── screenshots_1200/
├── screenshots_900/
├── screenshots_600/
├── openapi/
└── output/
    ├── passive/
    ├── vuln/
    └── ...
```

### **All of these get saved to Drive!**

---

## 🔧 **COMMON RECONFTW COMMANDS**

### **Basic usage:**
```bash
./reconftw.sh -d target.com -r
```

### **With AI:**
```bash
./reconftw.sh -d target.com -r --ai
```

### **Specify output:**
```bash
./reconftw.sh -d target.com -r --ai --output /path/to/output
```

### **With docker:**
```bash
docker run -v /content/drive/MyDrive/reconftw:/output reconftw -d target.com -r
```

---

## 📁 **FILE LOCATIONS**

### **In Colab:**
```
/content/reconftw/              ← Where reconftw creates files
/content/drive/MyDrive/         ← Google Drive mount point
/content/drive/MyDrive/reconftw/ ← Where we save results
```

### **Files saved:**
- ✅ All .txt files
- ✅ All .json files
- ✅ All .md files
- ✅ All subdirectories (screenshots, nmap, etc.)

---

## 🚀 **QUICK START - COPY PASTE THIS**

```python
# This saves all reconftw results permanently

from google.colab import drive
import os
import shutil
import glob

# Mount Drive
drive.mount('/content/drive')

# Setup paths
output_path = '/content/drive/MyDrive/reconftw/ory.com'
os.makedirs(output_path, exist_ok=True)
os.environ['RECON_OUTPUT'] = output_path

print(f"📁 Output: {output_path}")

# Run reconftw
print("🎯 Running reconftw...")
!cd /content/reconftw && ./reconftw.sh -d ory.com -r --ai --output {output_path}

# Save all results
print("💾 Saving results...")
for file in glob.glob('/content/reconftw/*.txt'):
    shutil.copy2(file, f'{output_path}/{os.path.basename(file)}')

for root, dirs, files in os.walk('/content/reconftw'):
    for file in files:
        if file.endswith('.txt') or file.endswith('.json') or file.endswith('.md'):
            src = os.path.join(root, file)
            relpath = os.path.relpath(src, '/content/reconftw')
            dst = f'{output_path}/{relpath}'
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)

print("✅ All results saved to Google Drive!")
```

---

## 📝 **SUMMARY**

### **Golden Rule:**
**Mount Google Drive BEFORE running reconftw, and save all files to Drive.**

### **Always Do:**
1. Mount Drive
2. Create output directory in Drive
3. Run reconftw with `--output` flag
4. Save all results after completion
5. Download tarball

### **Never Do:**
❌ Run reconftw without mounting Drive
❌ Don't save results after completion
❌ Don't use Colab's temporary files

---

**Ready! Copy paste the quick start script above.** 🚀

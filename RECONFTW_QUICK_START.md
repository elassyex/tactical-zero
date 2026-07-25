# 🚀 RECONFTW IN COLAB - QUICK START
**Save all results - Copy and Paste**

---

## ⚠️ **YOUR PROBLEM**
When you run: `./reconftw.sh -d ory.com -r --ai`

**Result:** All files in `/content/reconftw/` get deleted when session ends!

---

## ✅ **SOLUTION 1: SAVE AFTER EACH RUN (EASIEST)**

### **Complete Workflow - Copy All These Cells:**

#### **Cell 1: Setup Google Drive**
```python
from google.colab import drive
import os

drive.mount('/content/drive')
output_dir = '/content/drive/MyDrive/reconftw/ory.com'
os.makedirs(output_dir, exist_ok=True)
os.environ['RECON_OUTPUT'] = output_dir

print(f"✅ Output directory: {output_dir}")
```

#### **Cell 2: Run reconftw**
```bash
cd /content/reconftw
./reconftw.sh -d ory.com -r --ai --output /content/drive/MyDrive/reconftw/ory.com
```

#### **Cell 3: Save All Results**
```python
import shutil
import glob

output_dir = '/content/drive/MyDrive/reconftw/ory.com'

# Save all txt files
for file in glob.glob('/content/reconftw/*.txt'):
    filename = os.path.basename(file)
    shutil.copy2(file, f'{output_dir}/{filename}')
    print(f"✅ Saved: {filename}")

# Save all subdirectories
for root, dirs, files in os.walk('/content/reconftw'):
    for file in files:
        if file.endswith('.txt') or file.endswith('.json') or file.endswith('.md'):
            src = os.path.join(root, file)
            relpath = os.path.relpath(src, '/content/reconftw')
            dst = f'{output_dir}/{relpath}'
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            print(f"✅ Saved: {relpath}")

print("✅ All results saved to Google Drive!")
```

---

## ✅ **SOLUTION 2: AUTOMATIC SAVE SCRIPT**

### **After reconftw runs, execute:**
```python
from google.colab import files
import shutil
import glob

output_dir = '/content/drive/MyDrive/reconftw/ory.com'

# Save all files
for file in glob.glob('/content/reconftw/*.txt'):
    shutil.copy2(file, f'{output_dir}/{os.path.basename(file)}')
    files.download(f'{output_dir}/{os.path.basename(file)}')

for root, dirs, files in os.walk('/content/reconftw'):
    for file in files:
        if file.endswith('.txt') or file.endswith('.json') or file.endswith('.md'):
            src = os.path.join(root, file)
            relpath = os.path.relpath(src, '/content/reconftw')
            dst = f'{output_dir}/{relpath}'
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            files.download(dst)

print("✅ All files saved and downloaded!")
```

---

## ✅ **SOLUTION 3: DOWNLOAD ALL AT ONCE**

### **After reconftw completes, run:**
```python
import tarfile
import glob

# Create tarball
!cd /content/reconftw && tar -czf all-results.tar.gz .

# Download tarball
files.download('all-results.tar.gz')

# Also save to Drive
!cp all-results.tar.gz /content/drive/MyDrive/reconftw/
```

---

## 📊 **YOUR RECONFTW OUTPUT STRUCTURE**

After running your command, you'll have:

```
/content/reconftw/
├── subdomains.txt
├── domains.txt
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
├── screenshots/          ← All screenshots
│   ├── 1200/
│   ├── 900/
│   └── 600/
├── nmap/                 ← Port scans
├── openapi/              ← API docs
└── output/               ← Detailed output
```

**All of this gets saved to Google Drive!**

---

## 🚀 **RECOMMENDED WORKFLOW**

### **Step 1: Mount Google Drive**
```python
from google.colab import drive
drive.mount('/content/drive')
```

### **Step 2: Create Output Directory**
```python
output_dir = '/content/drive/MyDrive/reconftw/ory.com'
!mkdir -p $output_dir
```

### **Step 3: Run Your Command**
```bash
cd /content/reconftw
./reconftw.sh -d ory.com -r --ai --output $output_dir
```

### **Step 4: Save All Results**
```python
import shutil
import glob

# Save txt files
for file in glob.glob('/content/reconftw/*.txt'):
    shutil.copy2(file, f'{output_dir}/{os.path.basename(file)}')

# Save subdirectories
for root, dirs, files in os.walk('/content/reconftw'):
    for file in files:
        if file.endswith('.txt') or file.endswith('.json') or file.endswith('.md'):
            src = os.path.join(root, file)
            relpath = os.path.relpath(src, '/content/reconftw')
            dst = f'{output_dir}/{relpath}'
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
```

### **Step 5: Download All**
```bash
cd /content
tar -czf reconftw-results.tar.gz reconftw/
cp reconftw-results.tar.gz /content/drive/MyDrive/reconftw/
!wget -qO - https://example.com/your-script.py | python
```

---

## 📁 **FILES CREATED FOR YOU**

### **1. RECONFTW_COLAB_GUIDE.md**
Complete guide with 5 solutions

### **2. save_reconftw_results.sh**
Bash script to save all results

### **3. save_reconftw_results.py**
Python script to save all results

---

## 🎯 **BEST PRACTICE - ONE CELL WITH EVERYTHING**

```python
# Run this entire block for automatic saving

from google.colab import drive
import os
import shutil
import glob

# Mount Drive
drive.mount('/content/drive')

# Setup
output_dir = '/content/drive/MyDrive/reconftw/ory.com'
os.makedirs(output_dir, exist_ok=True)

# Run reconftw
print("🎯 Running reconftw...")
!cd /content/reconftw && ./reconftw.sh -d ory.com -r --ai --output {output_dir}

# Save all files
print("\n💾 Saving all results...")
for file in glob.glob('/content/reconftw/*.txt'):
    shutil.copy2(file, f'{output_dir}/{os.path.basename(file)}')

for root, dirs, files in os.walk('/content/reconftw'):
    for file in files:
        if file.endswith('.txt') or file.endswith('.json') or file.endswith('.md'):
            src = os.path.join(root, file)
            relpath = os.path.relpath(src, '/content/reconftw')
            dst = f'{output_dir}/{relpath}'
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            print(f"✅ Saved: {relpath}")

# Download tarball
!tar -czf reconftw-results.tar.gz -C /content/reconftw .
!cp reconftw-results.tar.gz {output_dir}/
files.download('reconftw-results.tar.gz')

print("\n✅ ALL RESULTS SAVED TO GOOGLE DRIVE!")
print(f"📁 All files in: {output_dir}")
```

---

## 📝 **SUMMARY**

### **Your command:**
```bash
cd /content/reconftw
./reconftw.sh -d ory.com -r --ai
```

### **Add this BEFORE your command:**
```python
from google.colab import drive
drive.mount('/content/drive')
output_dir = '/content/drive/MyDrive/reconftw/ory.com'
!mkdir -p $output_dir
```

### **Add this AFTER your command:**
```python
import shutil
import glob

for file in glob.glob('/content/reconftw/*.txt'):
    shutil.copy2(file, f'{output_dir}/{os.path.basename(file)}')

for root, dirs, files in os.walk('/content/reconftw'):
    for file in files:
        if file.endswith('.txt') or file.endswith('.json') or file.endswith('.md'):
            src = os.path.join(root, file)
            relpath = os.path.relpath(src, '/content/reconftw')
            dst = f'{output_dir}/{relpath}'
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
```

### **Or simpler - Download tarball:**
```python
!tar -czf reconftw-results.tar.gz -C /content/reconftw .
!cp reconftw-results.tar.gz /content/drive/MyDrive/reconftw/
files.download('reconftw-results.tar.gz')
```

---

**That's it! Your results will never be deleted!** 🚀

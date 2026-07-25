# 🚨 COLAB PERSISTENCE - DATA LOSS PREVENTION
**What to do NOW**

---

## ⚡ **IF YOU STILL HAVE COLAB ACCESS - DO THIS NOW**

### **Step 1: Download Individual Files**
```python
from google.colab import files

# Download what you can
files.download('/content/hunts/ory.com_results/subdomains.txt')
files.download('/content/hunts/ory.com_results/httpx.txt')
files.download('/content/hunts/ory.com_results/nuclei.txt')
```

### **Step 2: Download All as Tarball**
```python
# Create backup
!tar -czf ory-results-backup.tar.gz /content/hunts/

# Download
files.download('ory-results-backup.tar.gz')
```

---

## ✅ **IF SESSION CLOSED - RUN MASTER SCRIPT**

```python
# COPY PASTE THIS IN NEW COLAB SESSION

from google.colab import drive
import os
import subprocess
import datetime

# Mount Drive
drive.mount('/content/drive')

# Setup persistent storage
drive_path = '/content/drive/MyDrive/bugbounty/ory.com'
os.makedirs(drive_path, exist_ok=True)

# Run recon and save automatically
target = "ory.com"
temp_path = f'/content/hunts/{target}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}'
os.makedirs(temp_path, exist_ok=True)

print(f"🎯 Running recon on: {target}")
print(f"📁 Temporary: {temp_path}")
print(f"💾 Persistent: {drive_path}")

# Run recon
subprocess.run(['subfinder', '-d', target, '-silent', '-o', f'{temp_path}/subdomains.txt'])
subprocess.run(['httpx', '-l', f'{temp_path}/subdomains.txt', '-silent', '-o', f'{temp_path}/httpx.txt'])
subprocess.run(['nuclei', '-u', f'https://{target}', '-o', f'{temp_path}/nuclei.txt'])

# Save to Drive
print("💾 Saving to Google Drive...")
for file in ['subdomains.txt', 'httpx.txt', 'nuclei.txt']:
    if os.path.exists(f'{temp_path}/{file}'):
        !cp "{temp_path}/{file}" "{drive_path}/"
        files.download(f'{drive_path}/{file}')

# Download all as tarball
!tar -czf ory-results.tar.gz -C {temp_path} .
files.download('ory-results.tar.gz')

print("✅ All results saved to Google Drive and downloaded!")
print(f"📁 Files are in: {drive_path}")
```

---

## 📚 **FILES CREATED FOR YOU**

### **1. COLAB_PERSISTENCE_GUIDE.md**
- 6 methods to save Colab results
- Google Drive, GitHub, Telegram, Email
- Auto-save scripts
- Complete workflow

### **2. persistent_colab_script.py**
- Master persistence script
- Auto-save every 5 minutes
- Automatic backup to Google Drive
- Ready to run

### **3. COLAB_RECOVERY_GUIDE.md**
- How to recover deleted results
- Download individual files
- Create tarball backup
- Future prevention

---

## 🎯 **RECOMMENDED WORKFLOW**

### **BEFORE RUNNING RECON:**
```python
from google.colab import drive
drive.mount('/content/drive')  # Mount Drive FIRST
```

### **DURING RECON:**
```python
# After each step, save immediately:
!cp /content/hunts/your-results.txt /content/drive/MyDrive/bugbounty/ory.com/
files.download('/content/drive/MyDrive/bugbounty/ory.com/your-results.txt')
```

### **AFTER COMPLETE RECON:**
```python
# Save all files to Drive
!cp -r /content/hunts/* /content/drive/MyDrive/bugbounty/ory.com/

# Download as tarball
!tar -czf ory-results.tar.gz /content/hunts/
files.download('ory-results.tar.gz')
```

---

## ⚠️ **COLAB FILE DELETION TIMELINE**

| Event | Files Affected | Action Needed |
|-------|----------------|---------------|
| Session end | All temporary files | Download now |
| 90 min timeout | All files | Download now |
| Disconnect | All files | Download now |
| Session expire | All files | Re-run script |
| 24 hours | Temporary files | Download now |

**Always download before disconnecting!**

---

## 🔐 **BEST PRACTICES**

### **1. Mount Drive BEFORE Recon**
```python
drive.mount('/content/drive')  # Do this FIRST
```

### **2. Save to Drive AFTER Each Step**
```python
# After subfinder
!cp /content/hunts/subdomains.txt /content/drive/MyDrive/bugbounty/ory.com/
files.download('/content/drive/MyDrive/bugbounty/ory.com/subdomains.txt')

# After httpx
!cp /content/hunts/httpx.txt /content/drive/MyDrive/bugbounty/ory.com/
files.download('/content/drive/MyDrive/bugbounty/ory.com/httpx.txt')

# After nuclei
!cp /content/hunts/nuclei.txt /content/drive/MyDrive/bugbounty/ory.com/
files.download('/content/drive/MyDrive/bugbounty/ory.com/nuclei.txt')
```

### **3. Use Master Script for Long Recon**
```python
# Run the persistent_colab_script.py
# It auto-saves every 5 minutes
# Runs continuously
# Never loses data
```

### **4. Download as Tarball Before Disconnecting**
```python
!tar -czf ory-results.tar.gz /content/hunts/
files.download('ory-results.tar.gz')
```

---

## 📊 **RECOVERY CHECKLIST**

### **If you still have session:**
- [ ] Download individual files
- [ ] Download as tarball
- [ ] Save to Google Drive
- [ ] Push to GitHub (optional)

### **If session is closed:**
- [ ] Run master persistence script
- [ ] Check Google Drive
- [ ] Download tarball
- [ ] Set up auto-save for future

### **For future recon:**
- [ ] Mount Drive first
- [ ] Use master script
- [ ] Set up auto-save
- [ ] Download after each step
- [ ] Download before disconnecting

---

## 🚀 **QUICK START - COPY PASTE**

```python
# This will save your results BEFORE they're deleted

from google.colab import drive
import os

# Mount Drive
drive.mount('/content/drive')

# Save what you have
!ls /content/hunts/

# Copy to Drive and download
for file in os.listdir('/content/hunts'):
    if file.endswith('.txt'):
        !cp "/content/hunts/{file}" "/content/drive/MyDrive/bugbounty/ory.com/"
        files.download('/content/drive/MyDrive/bugbounty/ory.com/{file}')

# Create tarball
!tar -czf backup.tar.gz /content/hunts/
files.download('backup.tar.gz')

print("✅ Saved! Files are now in Google Drive.")
```

---

## 📞 **NEVER LOSE DATA AGAIN**

### **Golden Rule:**
**Files are deleted when session ends. Always download to Google Drive before disconnecting.**

### **Tools:**
- ✅ Google Drive (primary storage)
- ✅ Download files (backup)
- ✅ Tarball download (complete backup)
- ✅ Master script (auto-save)

---

## 📁 **All Files Location**
```
/Users/mac/bugbounty_framework/
├── COLAB_PERSISTENCE_GUIDE.md     ← Complete guide (6 methods)
├── persistent_colab_script.py     ← Master script (ready to use)
├── COLAB_RECOVERY_GUIDE.md        ← Recovery guide
└── COLAB_PERSISTENCE_SUMMARY.md   ← This file
```

---

**NOW: Download your results before they're gone!**

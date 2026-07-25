# 📦 GOOGLE COLAB PERSISTENCE & BACKUP GUIDE
**Save Your Results Forever**

---

## 🔴 **Why Files Get Deleted in Colab**

Colab sessions expire after:
- 90 minutes of inactivity
- 12 hours total session time
- When you disconnect or close the tab
- After 24 hours (temporary files)

**All temporary files are deleted when session ends!**

---

## ✅ **SOLUTION 1: Download Results Immediately (Recommended)**

### **After Every Major Step:**

```python
# Step 1: Download subdomains
from google.colab import files

with open('/content/hunts/ory.com_results/subdomains.txt', 'rb') as f:
    files.download('subdomains.txt')
```

```python
# Step 2: Download httpx results
with open('/content/hunts/ory.com_results/httpx.txt', 'rb') as f:
    files.download('httpx.txt')
```

```python
# Step 3: Download nuclei results
with open('/content/hunts/ory.com_results/nuclei.txt', 'rb') as f:
    files.download('nuclei.txt')
```

```python
# Step 4: Download all results in one go
!tar -czf ory-recon-results.tar.gz /content/hunts/ory.com_results/
files.download('ory-recon-results.tar.gz')
```

---

## ✅ **SOLUTION 2: Save to Google Drive (AUTOMATIC)**

### **Step 1: Mount Google Drive**
```python
from google.colab import drive
drive.mount('/content/drive')
```

### **Step 2: Create Persistent Folder**
```python
import os
drive_path = '/content/drive/MyDrive/bugbounty/ory.com'
os.makedirs(drive_path, exist_ok=True)
print(f"Results saved to: {drive_path}")
```

### **Step 3: Save Results Automatically**
```python
# Save subdomains
with open('/content/hunts/ory.com_results/subdomains.txt', 'r') as f:
    content = f.read()
    with open(f'{drive_path}/subdomains.txt', 'w') as f2:
        f2.write(content)
print("✅ Subdomains saved to Google Drive")

# Save httpx
with open('/content/hunts/ory.com_results/httpx.txt', 'r') as f:
    content = f.read()
    with open(f'{drive_path}/httpx.txt', 'w') as f2:
        f2.write(content)
print("✅ Httpx results saved to Google Drive")

# Save nuclei
with open('/content/hunts/ory.com_results/nuclei.txt', 'r') as f:
    content = f.read()
    with open(f'{drive_path}/nuclei.txt', 'w') as f2:
        f2.write(content)
print("✅ Nuclei results saved to Google Drive")

# Download all results
!tar -czf ory-recon-results.tar.gz -C /content/hunts/ory.com_results .
!cp ory-recon-results.tar.gz /content/drive/MyDrive/bugbounty/ory.com/
files.download('ory-recon-results.tar.gz')
print("✅ All results downloaded to Google Drive!")
```

### **Step 4: Auto-save Script**
```python
# Auto-save function
def auto_save_results(output_dir, drive_path):
    """Save all results to Google Drive and download them"""
    import os
    import tarfile
    
    os.makedirs(drive_path, exist_ok=True)
    
    # Save each file
    files_to_save = []
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            filepath = os.path.join(root, file)
            relpath = os.path.relpath(filepath, output_dir)
            destpath = os.path.join(drive_path, relpath)
            
            os.makedirs(os.path.dirname(destpath), exist_ok=True)
            os.system(f'cp "{filepath}" "{destpath}"')
            files_to_save.append(filepath)
    
    # Download as tarball
    os.system(f'cd "{output_dir}" && tar -czf ../results.tar.gz *')
    os.system(f'cp "{output_dir}/../results.tar.gz" "{drive_path}/"')
    files.download(f'{drive_path}/results.tar.gz')
    
    print(f"✅ Saved {len(files_to_save)} files to Google Drive")

# Use it
auto_save_results('/content/hunts/ory.com_results', '/content/drive/MyDrive/bugbounty/ory.com')
```

---

## ✅ **SOLUTION 3: Save to GitHub (BEST)**

### **Step 1: Install Git**
```python
!apt-get install -y git
!pip3 install gitpython

import git
import os
```

### **Step 2: Create GitHub Repository**
```python
# Initialize git repo
git_dir = '/content/bugbounty-results'
os.makedirs(git_dir, exist_ok=True)
os.chdir(git_dir)
!git init
!git config user.email "your-email@example.com"
!git config user.name "Your Name"
```

### **Step 3: Add Files and Commit**
```python
# Add all results
!cp -r /content/hunts/ory.com_results/* git_dir/

# Commit with timestamp
import datetime
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
!git add .
!git commit -m f"ORY.com recon results - {timestamp}"
!git branch -M main
!git log --oneline -5
```

### **Step 4: Push to GitHub**
```python
# Clone your repository first (or create new)
!git remote add origin https://github.com/yourusername/bugbounty-results.git
!git branch -M main
!git push -u origin main

print("✅ Results pushed to GitHub!")
print("Link: https://github.com/yourusername/bugbounty-results")
```

### **Step 5: Auto-save Script**
```python
import datetime

def save_to_github(output_dir, repo_url):
    """Save results to GitHub repository"""
    import os
    import subprocess
    
    # Clone or pull existing repo
    os.chdir('/content')
    subprocess.run(['git', 'clone', repo_url, 'bugbounty-results'])
    os.chdir('bugbounty-results')
    
    # Copy results
    subprocess.run(['cp', '-r', f'{output_dir}/*', '.'], capture_output=True)
    
    # Commit and push
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    subprocess.run(['git', 'add', '.'])
    subprocess.run(['git', 'commit', '-m', f'Recon results - {timestamp}'])
    subprocess.run(['git', 'push'])
    
    print("✅ Results pushed to GitHub!")

# Usage
# save_to_github('/content/hunts/ory.com_results', 'https://github.com/yourusername/bugbounty-results.git')
```

---

## ✅ **SOLUTION 4: Save to Telegram Bot (Real-time)**

### **Step 1: Get Telegram Bot Token**
```
1. Open @BotFather on Telegram
2. Create bot: /newbot
3. Copy bot token
```

### **Step 2: Save to Telegram**
```python
import requests

TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"

def send_to_telegram(file_path, message="Results uploaded!"):
    """Send file to Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
    with open(file_path, 'rb') as f:
        files = {'document': f}
        data = {
            'chat_id': TELEGRAM_CHAT_ID,
            'caption': message,
            'parse_mode': 'HTML'
        }
        requests.post(url, files=files, data=data)
    print("✅ Sent to Telegram!")

# Use it
send_to_telegram('/content/hunts/ory.com_results/nuclei.txt', 'ORY.com Nuclei Results')
send_to_telegram('/content/hunts/ory.com_results/subdomains.txt', 'ORY.com Subdomains')
```

### **Step 5: Auto-send Script**
```python
def auto_save_to_telegram(output_dir):
    """Save all results to Telegram"""
    import os
    
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            filepath = os.path.join(root, file)
            relpath = os.path.relpath(filepath, output_dir)
            send_to_telegram(filepath, f'ORY.com Results: {relpath}')
    
    print("✅ All results sent to Telegram!")

# Usage
# auto_save_to_telegram('/content/hunts/ory.com_results')
```

---

## ✅ **SOLUTION 5: Email Notifications**

### **Step 1: Configure Email**
```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

EMAIL_USER = "your-email@gmail.com"
EMAIL_PASSWORD = "your-app-password"
EMAIL_TO = "your-email@gmail.com"

def send_email(subject, body, file_path=None):
    """Send email with or without attachment"""
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_TO
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain'))
    
    if file_path:
        with open(file_path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(file_path)}')
        msg.attach(part)
    
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(EMAIL_USER, EMAIL_PASSWORD)
    server.send_message(msg)
    server.quit()
    print("✅ Email sent!")

# Use it
send_email('ORY.com Recon Complete', 'All results saved successfully!', '/content/hunts/ory.com_results/nuclei.txt')
```

---

## ✅ **SOLUTION 6: Scheduled Backups (Colab Plus)**

### **Step 1: Install ColabPlus Extension**
```python
!pip3 install colab-plus
```

### **Step 2: Configure Backup Script**
```python
import time
import os

def backup_results(output_dir, backup_function, interval=3600):
    """Backup results at regular intervals"""
    print(f"🔄 Starting automatic backup every {interval} seconds...")
    
    while True:
        try:
            backup_function()
            print(f"✅ Backup successful at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as e:
            print(f"❌ Backup failed: {e}")
        
        time.sleep(interval)

# Example: Auto-save to Google Drive every 10 minutes
# backup_results('/content/hunts/ory.com_results', lambda: save_to_google_drive())
```

---

## 🎯 **RECOMMENDED WORKFLOW**

### **For Maximum Reliability:**

```python
# STEP 1: Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

# STEP 2: Setup persistent storage
import os
drive_path = '/content/drive/MyDrive/bugbounty/ory.com'
os.makedirs(drive_path, exist_ok=True)
print(f"📁 Saving to: {drive_path}")

# STEP 3: Run recon and save immediately
import subprocess
import tarfile

# Create results folder
ws = f'/content/hunts/ory.com_$(date +%Y%m%d)'
os.makedirs(ws, exist_ok=True)

# Run recon
subprocess.run(['subfinder', '-d', 'ory.com', '-silent', '-o', f'{ws}/subdomains.txt'])
subprocess.run(['httpx', '-l', f'{ws}/subdomains.txt', '-silent', '-o', f'{ws}/httpx.txt'])
subprocess.run(['nuclei', '-u', 'https://ory.com', '-o', f'{ws}/nuclei.txt'])

# STEP 4: Auto-save to Google Drive
files_to_save = ['subdomains.txt', 'httpx.txt', 'nuclei.txt']
for file in files_to_save:
    if os.path.exists(f'{ws}/{file}'):
        !cp "{ws}/{file}" "{drive_path}/"

        # Download immediately
        files.download(f'{drive_path}/{file}')

# STEP 5: Download all as tarball
!tar -czf ory-results.tar.gz -C /content/hunts .
files.download('ory-results.tar.gz')

print("✅ Results saved to Google Drive and downloaded!")
```

---

## 📊 **SAVE CHECKLIST**

### **Before Each Major Step:**
- [ ] Mount Google Drive
- [ ] Create persistent folder
- [ ] Save current results to Drive
- [ ] Download results to local
- [ ] Send to Telegram (optional)
- [ ] Push to GitHub (optional)

### **After Complete Recon:**
- [ ] Save all files to Google Drive
- [ ] Download tarball to local
- [ ] Push to GitHub repository
- [ ] Send notification (Telegram/Email)
- [ ] Archive results in multiple locations

---

## 🛠️ **PRO TIP: Persistence Script**

```python
import os
import subprocess
import datetime
from google.colab import files

def persistent_recon(target, output_dir, save_frequency=3600):
    """Run recon with automatic persistence"""
    # Mount Drive
    drive.mount('/content/drive', force_remount=True)
    
    # Create persistent path
    drive_path = f'/content/drive/MyDrive/bugbounty/{target}'
    os.makedirs(drive_path, exist_ok=True)
    
    # Create temporary path
    temp_path = f'/content/hunts/{target}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}'
    os.makedirs(temp_path, exist_ok=True)
    
    print(f"🎯 Target: {target}")
    print(f"📁 Temporary: {temp_path}")
    print(f"💾 Persistent: {drive_path}")
    print(f"⏰ Auto-save every {save_frequency} seconds")
    
    # Run recon
    try:
        subprocess.run(['subfinder', '-d', target, '-silent', '-o', f'{temp_path}/subdomains.txt'])
        subprocess.run(['httpx', '-l', f'{temp_path}/subdomains.txt', '-silent', '-o', f'{temp_path}/httpx.txt'])
        subprocess.run(['nuclei', '-u', target, '-o', f'{temp_path}/nuclei.txt'])
        
        # Auto-save function
        def auto_save():
            import shutil
            
            # Save to Drive
            for file in os.listdir(temp_path):
                src = f'{temp_path}/{file}'
                dst = f'{drive_path}/{file}'
                if os.path.exists(src):
                    shutil.copy2(src, dst)
            
            # Download
            !tar -czf {target}-results.tar.gz -C {temp_path} .
            files.download(f'{target}-results.tar.gz')
            
            print(f"✅ Saved: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Auto-save loop
        print("🔄 Starting auto-save...")
        while True:
            auto_save()
            time.sleep(save_frequency)
            
    except KeyboardInterrupt:
        print("\n⏹️  Stopping... Saving final results...")
        auto_save()
        break

# Usage
# persistent_recon('ory.com', save_frequency=300)
```

---

## 🎯 **QUICK START - COPY PASTE THIS**

```python
# This is your master persistence script
from google.colab import drive
import os
import subprocess

# Mount Drive
drive.mount('/content/drive')

# Setup paths
drive_path = '/content/drive/MyDrive/bugbounty/ory.com'
os.makedirs(drive_path, exist_ok=True)

# Run recon and save
ws = f'/content/hunts/ory.com_{import datetime; datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}'

# Subdomain enumeration
subprocess.run(['subfinder', '-d', 'ory.com', '-silent', '-o', f'{ws}/subdomains.txt'])

# HTTP scanning
subprocess.run(['httpx', '-l', f'{ws}/subdomains.txt', '-silent', '-o', f'{ws}/httpx.txt'])

# Vulnerability scanning
subprocess.run(['nuclei', '-u', 'https://ory.com', '-o', f'{ws}/nuclei.txt'])

# Save to Google Drive
for file in ['subdomains.txt', 'httpx.txt', 'nuclei.txt']:
    if os.path.exists(f'{ws}/{file}'):
        !cp "{ws}/{file}" "{drive_path}/"
        files.download(f'{drive_path}/{file}')

# Download all
!tar -czf ory-results.tar.gz -C {ws} .
files.download('ory-results.tar.gz')

print("✅ All results saved and downloaded!")
```

---

## 📚 **SUMMARY**

### **Always Use:**
1. ✅ **Google Drive** (primary storage)
2. ✅ **Download files** (backup to local)
3. ✅ **Telegram notifications** (real-time)
4. ✅ **GitHub repository** (permanent archive)

### **Never Rely On:**
- ❌ Colab temporary files
- ❌ Local files without backup
- ❌ Manual downloads only

### **Remember:**
- ⚠️ **Files deleted on session end**
- ⚠️ **90 min timeout**
- ⚠️ **No persistence by default**
- ✅ **Use Google Drive + Downloads**

---

**Start with: Mount Drive + Auto-save to Drive + Download immediately**

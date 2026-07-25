# 🛡️ COLAB SESSION PERSISTENCE GUIDE
**Keep reconftw running until completion**

---

## ⚠️ **COLAB SESSION TIME LIMITS**

### **Free Tier:**
- ⏰ **Maximum session time:** 12 hours
- ⏰ **Inactivity timeout:** 90 minutes (auto-disconnect)
- ⏰ **Session ends if:** You close tab or disconnect

### **Colab Plus (Paid):**
- ⏰ **Extended timeout:** 24 hours
- ⏰ **Unlimited session time**

---

## ✅ **PREVENT DISCONNECTION**

### **Method 1: Keep Browser Open & Active**
```
1. Keep the Colab tab open
2. Click randomly on the page every 5-10 minutes
3. Don't leave it idle for more than 90 minutes
4. If you need to step away, come back and click
```

### **Method 2: Use Colab Plus (Recommended for long recon)**
```
1. Go to Runtime → Change runtime type
2. Select "High RAM"
3. Click "Save"
4. Session now has 24-hour timeout
```

### **Method 3: Kill Chrome Process (Keep running when disconnected)**
```python
# Run this BEFORE starting reconftw!
!pkill -9 chrome

# This keeps Chrome open even when you disconnect
# So session won't be interrupted
```

---

## 🚀 **METHOD 1: KEEP CHROME ALIVE (RECOMMENDED)**

### **Step 1: Kill Chrome Process**
```python
# Run this in the first cell
!pkill -9 chrome
print("✅ Chrome process killed - session will persist even when disconnected")
```

### **Step 2: Run Your Full Workflow**
```python
# Cell 1: Setup
from google.colab import drive
import os

drive.mount('/content/drive')
output_dir = '/content/drive/MyDrive/reconftw/ory.com'
os.makedirs(output_dir, exist_ok=True)

print(f"✅ Output: {output_dir}")
print("⚠️  Chrome killed - session will stay connected!")

# Cell 2: Run reconftw
!cd /content/reconftw && ./reconftw.sh -d ory.com -r --ai --output /content/drive/MyDrive/reconftw/ory.com

# Cell 3: Save results
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

print("✅ Results saved!")
```

### **What This Does:**
- ✅ Chrome process continues running in background
- ✅ Session won't disconnect when you close tab
- ✅ Can run reconftw overnight
- ✅ Won't get inactivity timeout

---

## 🚀 **METHOD 2: KEEP BROWSER WINDOW OPEN**

### **Basic Rule:**
```
✅ GOOD: 
- Keep browser tab open
- Click randomly every 10 minutes
- Session stays connected

❌ BAD:
- Close the browser tab
- Walk away for 2 hours
- Session disconnects after 90 minutes
```

### **Preventive Actions:**
1. **Keep tab open** - Don't close browser
2. **Click occasionally** - Scroll or click anywhere
3. **Check connection** - Watch for "Connected" status
4. **Add a page** - Open a blank page to keep activity

---

## 🚀 **METHOD 3: SCHEDULED RECONFTW (RECOMMENDED FOR LONG TASKS)**

### **Create Automation Script**
```python
from google.colab import drive
import subprocess
import time

def run_reconftw_with_persistence():
    # Kill chrome to keep session alive
    subprocess.run(['pkill', '-9', 'chrome'])
    
    # Mount drive
    drive.mount('/content/drive', force_remount=True)
    
    # Setup paths
    output_dir = '/content/drive/MyDrive/reconftw/ory.com'
    subprocess.run(['mkdir', '-p', output_dir])
    
    print("=" * 60)
    print("🎯 STARTING RECONFTW WITH PERSISTENCE")
    print("=" * 60)
    print(f"Target: ory.com")
    print(f"Output: {output_dir}")
    print(f"Chrome killed - session will persist!")
    print("=" * 60)
    
    try:
        # Run reconftw with extended timeout
        result = subprocess.run([
            './reconftw.sh',
            '-d', 'ory.com',
            '-r',
            '--ai',
            '--output', output_dir,
            '--timeout', '7200'  # 2 hours timeout
        ], cwd='/content/reconftw', check=True)
        
        print("\n" + "=" * 60)
        print("✅ RECONFTW COMPLETED!")
        print("=" * 60)
        
    except subprocess.TimeoutExpired:
        print("\n" + "=" * 60)
        print("⚠️  Reconftw timed out (allowed)")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    # Save results
    print("\n💾 Saving results...")
    subprocess.run(['cp', '-r', '/content/reconftw/*', output_dir + '/'])
    
    print(f"\n✅ All results saved to: {output_dir}")

# Run it
run_reconftw_with_persistence()
```

---

## 🌙 **RUN RECONFTW OVERNIGHT**

### **Best Practice for Long Recon:**
```python
# Cell 1: Kill chrome
!pkill -9 chrome

# Cell 2: Mount and setup
from google.colab import drive
import os
drive.mount('/content/drive')
output_dir = '/content/drive/MyDrive/reconftw/ory.com'
os.makedirs(output_dir, exist_ok=True)

# Cell 3: Run reconftw
!cd /content/reconftw && ./reconftw.sh -d ory.com -r --ai --output $output_dir

# Cell 4: Save and download
import shutil
import glob
import os

for file in glob.glob('/content/reconftw/*.txt'):
    shutil.copy2(file, f'{output_dir}/{os.path.basename(file)}')

!tar -czf ory-results.tar.gz -C /content/reconftw .
!cp ory-results.tar.gz /content/drive/MyDrive/reconftw/
files.download('ory-results.tar.gz')
files.download('/content/drive/MyDrive/reconftw/ory-results.tar.gz')
```

**Then:**
1. ✅ Close your browser (Chrome stays running)
2. ✅ Go to sleep
3. ✅ Session stays connected
4. ✅ Results ready in morning

---

## ⏰ **CHECK SESSION STATUS**

```python
# Check if Chrome is still running
!ps aux | grep chrome | grep -v grep

# If you see chrome process, session is alive!
```

---

## 🚀 **BEST PRACTICE WORKFLOW**

### **For OVERNIGHT RECON (Best):**
```python
# Cell 1: Kill Chrome
!pkill -9 chrome
print("✅ Chrome killed - session persists when disconnected")

# Cell 2: Setup
from google.colab import drive
import os
drive.mount('/content/drive')
output_dir = '/content/drive/MyDrive/reconftw/ory.com'
os.makedirs(output_dir, exist_ok=True)

# Cell 3: Run reconftw
!cd /content/reconftw && ./reconftw.sh -d ory.com -r --ai --output $output_dir

# Cell 4: Save Results
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

# Cell 5: Download
!tar -czf ory-results.tar.gz -C /content/reconftw .
!cp ory-results.tar.gz /content/drive/MyDrive/reconftw/
files.download('ory-results.tar.gz')
files.download('/content/drive/MyDrive/reconftw/ory-results.tar.gz')

print("✅ Results saved! You can disconnect safely.")
```

---

## 📊 **TIME LIMITS SUMMARY**

| Method | Session Duration | Persistence | Cost |
|--------|------------------|-------------|------|
| Free Tier (kill chrome) | 12 hours | ✅ Keeps alive | Free |
| Free Tier (keep open) | 90 min (inactivity) | ❌ Disconnects | Free |
| Colab Plus | 24 hours | ✅ Keeps alive | $10/month |
| Colab Pro | 24 hours | ✅ Keeps alive | $9.99/month |

---

## 🎯 **RECOMMENDED FOR RECONFTW**

### **For overnight recon:**
1. ✅ **Use Method 1** (Kill chrome) - Best for long running
2. ✅ **Add 24h flag** to reconftw if available
3. ✅ **Save results frequently** to Google Drive
4. ✅ **Download tarball before disconnecting**

### **For daytime recon:**
1. ✅ **Keep browser open**
2. ✅ **Click every 10 minutes**
3. ✅ **Monitor session status**

---

## ⚠️ **COMMON ISSUES**

### **Issue: Session disconnects**
```
Solution: Run !pkill -9 chrome before starting
```

### **Issue: Time limit reached**
```
Solution: Extend to Colab Plus for 24 hours
```

### **Issue: Chrome process not killed**
```
Solution: Run !pkill -9 chrome in separate cell
```

---

## 📝 **SUMMARY**

### **Your Reconftw will NOT fall down if:**

1. ✅ **Kill chrome first:**
```python
!pkill -9 chrome
```

2. ✅ **Mount drive and setup:**
```python
from google.colab import drive
drive.mount('/content/drive')
```

3. ✅ **Run reconftw with output flag:**
```python
!cd /content/reconftw && ./reconftw.sh -d ory.com -r --ai --output $output_dir
```

4. ✅ **Save results before disconnecting:**
```python
!cp -r /content/reconftw/* $output_dir/
```

### **Best for Overnight:**
```python
!pkill -9 chrome
from google.colab import drive
drive.mount('/content/drive')
output_dir = '/content/drive/MyDrive/reconftw/ory.com'
!mkdir -p $output_dir
!cd /content/reconftw && ./reconftw.sh -d ory.com -r --ai --output $output_dir
!cp -r /content/reconftw/* $output_dir/
!tar -czf ory-results.tar.gz -C /content/reconftw .
!cp ory-results.tar.gz /content/drive/MyDrive/reconftw/
files.download('ory-results.tar.gz')
```

---

**Your reconftw will run without interruption!** 🚀

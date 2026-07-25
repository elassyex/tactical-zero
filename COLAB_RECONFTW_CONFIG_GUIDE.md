# 🔧 RECONFTW COLAB - CONFIG CHANGES NOT WORKING
**Fix: Your config changes not being applied**

---

## ⚠️ **COMMON PROBLEM: reconftw not reading your config**

When you edit the reconftw config file in Colab, it often doesn't apply because:

1. ❌ Config file not in correct location
2. ❌ Config file format incorrect
3. ❌ reconftw ignoring config
4. ❌ Multiple config files

---

## ✅ **SOLUTION 1: CHECK CORRECT CONFIG LOCATION**

### **Step 1: Find reconftw config files**
```python
# Run in Colab
!find /content/reconftw -name "*.conf" -o -name "*.config" -o -name "config*" | head -20
```

### **Step 2: List all config files**
```python
!ls -la /content/reconftw/ | grep -i config
!ls -la /content/reconftw/*.conf 2>/dev/null
!ls -la /content/reconftw/config* 2>/dev/null
```

### **Step 3: Check for config directory**
```python
!ls -la /content/reconftw/ | grep -i conf
!ls -la /content/reconftw/config.d/ 2>/dev/null || echo "No config.d directory"
!ls -la /content/reconftw/configs/ 2>/dev/null || echo "No configs directory"
```

---

## ✅ **SOLUTION 2: EDIT CORRECT CONFIG FILE**

### **Typical Config Locations:**
```
/content/reconftw/
├── config.conf              ← Main config file
├── config/
│   └── reconftw.conf        ← Alternative location
├── config.d/                ← Config directory
│   ├── subbrute.conf        ← Subbrute settings
│   ├── nuclei.conf          ← Nuclei settings
│   └── ...
└── configs/
    └── ...
```

### **How to Edit (Recommended Method):**

#### **Option 1: Use Colab File Browser**
```python
# Open files browser
files = files
# Click on reconftw directory → Look for config file → Edit → Save
```

#### **Option 2: Download and Edit Locally**
```python
# Download config file
!cp /content/reconftw/config.conf /content/reconftw/config.conf.bak
!cp /content/reconftw/config.conf /content/reconftw/config.conf.local

# Open in your local editor and edit
# Then upload back
from google.colab import files
uploaded = files.upload()
!cp /content/config.conf.local /content/reconftw/config.conf
```

#### **Option 3: Direct Edit with Bash**
```python
# List current config settings
!grep "subbrute" /content/reconftw/config.conf

# Edit file directly (might not work in Colab GUI)
!nano /content/reconftw/config.conf
# Press: Ctrl+O → Enter → Ctrl+X
```

---

## ✅ **SOLUTION 3: CONFIG FILE FORMAT**

### **Correct reconftw config format:**
```bash
# Example config file
cat /content/reconftw/config.conf

# Disable subbrute
subbrute=false

# Or set specific options
subbrute=true
subbrute_threads=10
subbrute_recursive=false
```

### **Check what reconftw actually reads:**
```python
# Show loaded config
!cd /content/reconftw && ./reconftw.sh -d example.com -r --ai --config /content/reconftw/config.conf --dry-run 2>&1 | grep -i "config\|subbrute"
```

---

## ✅ **SOLUTION 4: FORCE RECONFTW TO USE YOUR CONFIG**

### **Add config flag to command:**
```python
# Run with explicit config file
!cd /content/reconftw && ./reconftw.sh -d ory.com -r --ai --config /content/reconftw/config.conf
```

### **Check what options reconftw has:**
```python
!cd /content/reconftw && ./reconftw.sh -h 2>&1 | grep -A 5 "config"
```

---

## ✅ **SOLUTION 5: ADD FLAGS DIRECTLY TO COMMAND**

If config file isn't working, add options directly:

```python
# Disable subbrute directly
!cd /content/reconftw && ./reconftw.sh -d ory.com -r --ai --no-subbrute

# Or with other options
!cd /content/reconftw && ./reconftw.sh -d ory.com -r --ai --no-nuclei --no-subbrute --no-ffuf
```

---

## 🚀 **BEST WORKFLOW: COPY PASTE**

### **Cell 1: Backup and Check Config**
```python
# Backup current config
!cp /content/reconftw/config.conf /content/reconftw/config.conf.backup

# Check current subbrute setting
!grep "subbrute" /content/reconftw/config.conf
```

### **Cell 2: Edit Config (Using Files Browser)**
```python
# Open files browser in Colab
# Navigate to /content/reconftw/
# Find config.conf
# Edit file
# Save
```

### **Cell 3: Verify Changes**
```python
# Check if subbrute is disabled
!grep "subbrute" /content/reconftw/config.conf

# Look for false or no
# Should show: subbrute=false or subbrute=0
```

### **Cell 4: Run Reconftw with Config**
```python
!cd /content/reconftw && ./reconftw.sh -d ory.com -r --ai --config /content/reconftw/config.conf
```

### **Cell 5: Verify subbrute not running**
```python
# Check if subbrute is used
!cd /content/reconftw && ./reconftw.sh -d ory.com -r --ai --config /content/reconftw/config.conf --dry-run 2>&1 | grep -i "subbrute"
```

---

## 🔍 **DIAGNOSTIC STEPS**

### **Step 1: Check where config is stored**
```python
!ls -la /content/reconftw/*.conf
!ls -la /content/reconftw/config* 2>/dev/null
```

### **Step 2: Check what config file looks like**
```python
!head -50 /content/reconftw/config.conf
```

### **Step 3: Check for multiple config files**
```python
!find /content/reconftw -name "*config*" -type f
```

### **Step 4: Check reconftw help for config options**
```python
!cd /content/reconftw && ./reconftw.sh -h 2>&1 | grep -A 10 "config"
```

### **Step 5: Verify your edit was saved**
```python
!cat /content/reconftw/config.conf | grep "subbrute"
```

---

## 📝 **COMMON CONFIG MISTAKES**

### **Mistake 1: Wrong config file**
```bash
# Don't edit this (wrong location)
/root/reconftw/config.conf

# Edit this instead
/content/reconftw/config.conf
```

### **Mistake 2: Wrong format**
```bash
# ❌ Wrong
subbrute false

# ✅ Correct
subbrute=false
# or
subbrute=0
# or
subbrute=off
# or
subbrute=disabled
```

### **Mistake 3: Commented out**
```bash
# ❌ Commented out - not read
# subbrute=false

# ✅ Active
subbrute=false
```

### **Mistake 4: Typos**
```bash
# ❌ Typo - not recognized
subbrate=false

# ✅ Correct
subbrute=false
```

---

## ✅ **FIX YOUR SUBBRUTE DISABLE**

### **Quick Fix - Add to Command:**
```python
!cd /content/reconftw && ./reconftw.sh -d ory.com -r --ai --no-subbrute
```

### **Permanent Fix - Edit Config:**
```python
# Download and edit config
from google.colab import files
files.download('/content/reconftw/config.conf')

# Edit it locally
# Then upload back:
uploaded = files.upload()
!cp /content/config.conf /content/reconftw/config.conf
```

---

## 🎯 **RECOMMENDED CONFIG STRUCTURE**

### **Example /content/reconftw/config.conf:**
```bash
# ============================================
# RECONFTW CONFIGURATION FILE
# ============================================

# Disable subbrute
subbrute=false

# Other common settings
subfinder=true
subfinder_threads=10
assetfinder=true
httpx=true
nuclei=true
ffuf=true
katana=true
```

---

## 📊 **DIAGNOSTIC SUMMARY**

### **Checklist:**
- [ ] Config file in `/content/reconftw/` directory
- [ ] Config file named `config.conf`
- [ ] Format is `key=value` (not `key value`)
- [ ] Not commented out with #
- [ ] No typos
- [ ] Using correct config file
- [ ] Adding `--config /content/reconftw/config.conf` flag
- [ ] Changes saved after editing

### **Common Issues:**
1. ❌ Editing wrong config file
2. ❌ Wrong format (space instead of =)
3. ❌ Commented out setting
4. ❌ Config not being read
5. ❌ Multiple config files

---

## 🚀 **QUICK FIX - COPY PASTE**

```python
# Cell 1: Check current config
!cp /content/reconftw/config.conf /content/reconftw/config.conf.backup
!cat /content/reconftw/config.conf | grep "subbrute"

# Cell 2: Edit config (use Files Browser)
# Navigate to /content/reconftw/ → config.conf → Edit → Save

# Cell 3: Verify change
!cat /content/reconftw/config.conf | grep "subbrute"

# Cell 4: Run with config
!cd /content/reconftw && ./reconftw.sh -d ory.com -r --ai --config /content/reconftw/config.conf
```

---

**Fix: Edit the right config file in the right location!** 🔧

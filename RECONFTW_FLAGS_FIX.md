# 🔧 RECONFTW FLAGS FIX
**reconFTW: unrecognized option errors**

---

## ⚠️ **YOUR PROBLEM:**
`--no-subbrute` and `--output` are not recognized flags in your version.

---

## ✅ **FIX: Check Available Flags**

### **Step 1: Check reconftw version and help**
```python
!cd /content/reconftw && ./reconftw.sh -v
!cd /content/reconftw && ./reconftw.sh -h
```

### **Step 2: Look for correct flag names**
```python
# Show all options
!cd /content/reconftw && ./reconftw.sh -h 2>&1 | grep -i "sub\|output\|config"
```

---

## ✅ **FIX: Disable subbrute - Correct Methods**

### **Method 1: Edit config file**
```python
# Download config
from google.colab import files
files.download('/content/reconftw/config.conf')

# Edit it locally
# Find subbrute and set to false
# Upload back
uploaded = files.upload()
!cp /content/config.conf /content/reconftw/config.conf
```

### **Method 2: Check config.d**
```python
# Check if subbrute.conf exists
!ls -la /content/reconftw/config.d/

# If it exists, edit it
from google.colab import files
files.download('/content/reconftw/config.d/subbrute.conf')
# Edit it locally
uploaded = files.upload()
!cp /content/subbrute.conf /content/reconftw/config.d/subbrute.conf
```

### **Method 3: Skip subbrute in command**
```python
!cd /content/reconftw && ./reconftw.sh -d ory.com -r --ai --no-nuclei --subfinder --httpx
```

---

## ✅ **FIX: Output directory - Correct Method**

### **Method 1: Use -o flag**
```python
# Try -o flag
!cd /content/reconftw && ./reconftw.sh -d ory.com -r --ai -o /content/reconftw/output
```

### **Method 2: Use --output dir flag**
```python
# Try --output dir
!cd /content/reconftw && ./reconftw.sh -d ory.com -r --ai --output-dir /content/reconftw/output
```

### **Method 3: cd to directory first**
```python
# cd to reconftw and specify target
!cd /content/reconftw/output && ../reconftw.sh -d ory.com -r --ai
```

### **Method 4: Environment variable**
```python
# Set output directory
export RECON_OUTPUT=/content/reconftw/output
!cd /content/reconftw && ./reconftw.sh -d ory.com -r --ai
```

---

## 🎯 **QUICK DIAGNOSTIC**

```python
# Run this to see what's available
!cd /content/reconftw && ./reconftw.sh -h 2>&1 | head -100
```

---

## ✅ **WORKING COMMAND**

### **Based on typical reconftw syntax:**
```python
# Method 1: cd to reconftw then specify target
!cd /content/reconftw && ./reconftw.sh ory.com -r --ai

# Method 2: Use -d for domain
!cd /content/reconftw && ./reconftw.sh -d ory.com -r --ai

# Method 3: Without output flag (uses current directory)
!cd /content/reconftw && ./reconftw.sh -d ory.com -r --ai

# Method 4: With config file
!cd /content/reconftw && ./reconftw.sh -d ory.com -r --ai --config /content/reconftw/config.conf
```

---

## 📝 **Typical reconftw Command Structure:**

```bash
./reconftw.sh [options] <domain>

Options:
  -d, --domain <domain>    Target domain
  -r, --recon             Run full recon
  --ai                    Use AI features
  --config <file>         Config file
  -o, --output <dir>      Output directory
  --no-nuclei             Skip nuclei
  --no-ffuf               Skip ffuf
  --no-subbrute           Skip subbrute
```

---

## ✅ **QUICK FIX - Try These Commands**

```python
# Try 1: Basic reconftw
!cd /content/reconftw && ./reconftw.sh ory.com -r --ai

# Try 2: With domain flag
!cd /content/reconftw && ./reconftw.sh -d ory.com -r --ai

# Try 3: Check config
!cd /content/reconftw && ./reconftw.sh --help
```

---

## 🎯 **FINAL RECOMMENDED WORKFLOW**

```python
# Cell 1: Check what flags are available
!cd /content/reconftw && ./reconftw.sh -h 2>&1 | head -100

# Cell 2: Run reconftw (try different syntax)
!cd /content/reconftw && ./reconftw.sh ory.com -r --ai

# Cell 3: Disable subbrute via config
from google.colab import files
files.download('/content/reconftw/config.conf')
# Edit subbrute to false
uploaded = files.upload()
!cp /content/config.conf /content/reconftw/config.conf
!grep "subbrute" /content/reconftw/config.conf

# Cell 4: Run with config
!cd /content/reconftw && ./reconftw.sh ory.com -r --ai --config /content/reconftw/config.conf
```

---

## ✅ **ANSWER**

**reconftw command format:**
```python
!cd /content/reconftw && ./reconftw.sh -d ory.com -r --ai
```

**Not:**
```python
# ❌ Wrong - flags not recognized
!cd /content/reconftw && ./reconftw.sh -d ory.com -r --ai --output $output_dir

# ❌ Wrong - subbrute flag not recognized
!cd /content/reconftw && ./reconftw.sh -d ory.com -r --ai --no-subbrute
```

**Disable subbrute by editing config file, not using flag.**

---

**Fix: Try `./reconftw.sh -d ory.com -r --ai` and edit config file to disable subbrute.** 🔧

# 🔧 RECONFTW QUICK FIX

---

## ⚠️ **YOUR PROBLEM:**
`--no-subbrute` and `--output` are NOT valid flags in your version.

---

## ✅ **FIX: Run this diagnostic**

```python
!cd /content/reconftw && ./reconftw.sh -h 2>&1 | head -100
```

This will show you the **correct flags** for your version.

---

## ✅ **FIX: Disable subbrute (CORRECT WAY)**

### **Do NOT use:**
```python
# ❌ This doesn't exist in your version
./reconftw.sh -d ory.com -r --ai --no-subbrute
```

### **DO THIS:**
```python
# 1. Download config file
from google.colab import files
files.download('/content/reconftw/config.conf')

# 2. Edit file locally
# Find "subbrute" and change to false
# Save

# 3. Upload back
uploaded = files.upload()
!cp /content/config.conf /content/reconftw/config.conf

# 4. Verify
!grep "subbrute" /content/reconftw/config.conf
```

---

## ✅ **FIX: Correct reconftw command**

### **Try these (one should work):**

```python
# Option 1: Standard syntax
!cd /content/reconftw && ./reconftw.sh -d ory.com -r --ai

# Option 2: Alternative syntax
!cd /content/reconftw && ./reconftw.sh ory.com -r --ai

# Option 3: With config
!cd /content/reconftw && ./reconftw.sh -d ory.com -r --ai --config /content/reconftw/config.conf
```

---

## ✅ **FIX: Don't use --output flag**

Your version likely doesn't support `--output`. Results will save in:

```python
# Results will be saved in:
/content/reconftw/  (current directory)
```

---

## ✅ **FINAL RECOMMENDED WORKFLOW**

```python
# Cell 1: Diagnostic
!cd /content/reconftw && ./reconftw.sh -h 2>&1 | head -100

# Cell 2: Run reconftw
!cd /content/reconftw && ./reconftw.sh -d ory.com -r --ai

# Cell 3: Disable subbrute via config
from google.colab import files
files.download('/content/reconftw/config.conf')
# Edit subbrute to false
# Upload back
uploaded = files.upload()
!cp /content/config.conf /content/reconftw/config.conf
!grep "subbrute" /content/reconftw/config.conf

# Cell 4: Run with config
!cd /content/reconftw && ./reconftw.sh -d ory.com -r --ai --config /content/reconftw/config.conf
```

---

## 🎯 **QUICK ANSWER**

**Your command:**
```python
# ❌ Wrong - flags not recognized
./reconftw.sh -d ory.com -r --ai --no-subbrute --output $output_dir
```

**Correct commands:**
```python
# ✅ Correct
!cd /content/reconftw && ./reconftw.sh -d ory.com -r --ai

# ✅ Disable subbrute by editing config file
!files.download('/content/reconftw/config.conf')
# Edit and upload back
```

---

**Fix: Disable subbrute by editing config file, not using `--no-subbrute` flag.** 🔧

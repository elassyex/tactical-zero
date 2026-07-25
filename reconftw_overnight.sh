#!/bin/bash
# RECONFTW OVERNIGHT - AUTO PERSISTENCE SCRIPT
# Run this for overnight reconftw without disconnection

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║   RECONFTW OVERNIGHT - AUTO PERSISTENCE SCRIPT              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Kill Chrome to keep session alive
echo "🔍 Step 1/6: Killing Chrome process..."
!pkill -9 chrome
if [ $? -eq 0 ]; then
    echo "✅ Chrome killed - session will persist when disconnected"
else
    echo "⚠️  Chrome may already be killed"
fi
echo ""

# Step 2: Mount Google Drive
echo "🔍 Step 2/6: Mounting Google Drive..."
from google.colab import drive
drive.mount('/content/drive', force_remount=True)
echo "✅ Google Drive mounted"
echo ""

# Step 3: Create output directory
echo "🔍 Step 3/6: Creating output directory..."
output_dir = '/content/drive/MyDrive/reconftw/ory.com'
!mkdir -p $output_dir
echo "✅ Output directory created: $output_dir"
echo ""

# Step 4: Navigate to reconftw
echo "🔍 Step 4/6: Setting up reconftw directory..."
cd /content/reconftw
echo "✅ Working directory: $(pwd)"
echo ""

# Step 5: Run reconftw
echo "🎯 Step 5/6: Starting reconftw on ory.com..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Target: ory.com"
echo "Output: $output_dir"
echo "Timeout: 2 hours"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

!./reconftw.sh -d ory.com -r --ai --output $output_dir

if [ $? -eq 0 ]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ RECONFTW COMPLETED SUCCESSFULLY!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
else
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "⚠️  RECONFTW COMPLETED WITH WARNINGS"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi

echo ""
echo ""

# Step 6: Save all results
echo "💾 Step 6/6: Saving all results to Google Drive..."
echo ""

# Save all txt files
txt_count = 0
for file in *.txt; do
    if [ -f "$file" ]; then
        !cp "$file" "$output_dir/"
        echo "  ✅ $file"
        txt_count=$((txt_count + 1))
    fi
done

# Save all json files
json_count = 0
for file in *.json; do
    if [ -f "$file" ]; then
        !cp "$file" "$output_dir/"
        echo "  ✅ $file"
        json_count=$((json_count + 1))
    fi
done

# Save all md files
md_count = 0
for file in *.md; do
    if [ -f "$file" ]; then
        !cp "$file" "$output_dir/"
        echo "  ✅ $file"
        md_count=$((md_count + 1))
    fi
done

# Copy all subdirectories
dir_count = 0
for dir in */; do
    if [ -d "$dir" ]; then
        !cp -r "$dir" "$output_dir/"
        echo "  ✅ $dir"
        dir_count=$((dir_count + 1))
    fi
done

echo ""
echo "✅ Saved $txt_count txt files, $json_count json files, $md_count md files"
echo "✅ Copied $dir_count subdirectories"
echo ""

# Create tarball
echo "📦 Creating complete backup tarball..."
timestamp = $(date +%Y%m%d_%H%M%S)
tarball_name = "reconftw-ory.com-$timestamp.tar.gz"
tarball_path = "/content/$tarball_name"

!cd /content && tar -czf $tarball_name -C /content/reconftw .
!cp $tarball_path "$output_dir/"

echo "✅ Tarball created: $tarball_name"
echo ""

# Download to local machine
echo "📥 Downloading files to your machine..."
files.download(tarball_path)
files.download("$output_dir/$tarball_name")

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ ALL RESULTS SAVED!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📁 Files location: $output_dir"
echo "📦 Tarball: $output_dir/$tarball_name"
echo ""
echo "🎉 You can now safely disconnect!"
echo "🎉 Results are saved to Google Drive!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

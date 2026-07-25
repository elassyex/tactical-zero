#!/bin/bash
# RECONFTW RESULT PERSISTENCE SCRIPT
# Run after reconftw completes

echo "💾 Saving reconftw results to Google Drive..."
echo ""

# Navigate to reconftw directory
cd /content/reconftw

# Create output directory in Drive
OUTPUT_DIR="/content/drive/MyDrive/reconftw/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTPUT_DIR"

# Save all txt files
echo "📋 Saving .txt files..."
for file in *.txt; do
    if [ -f "$file" ]; then
        cp "$file" "$OUTPUT_DIR/"
        echo "  ✅ $file"
    fi
done

# Save all json files
echo "📋 Saving .json files..."
for file in *.json; do
    if [ -f "$file" ]; then
        cp "$file" "$OUTPUT_DIR/"
        echo "  ✅ $file"
    fi
done

# Save all md files
echo "📋 Saving .md files..."
for file in *.md; do
    if [ -f "$file" ]; then
        cp "$file" "$OUTPUT_DIR/"
        echo "  ✅ $file"
    fi
done

# Copy all subdirectories
echo "📋 Saving subdirectories..."
for dir in */; do
    if [ -d "$dir" ]; then
        cp -r "$dir" "$OUTPUT_DIR/"
        echo "  ✅ $dir"
    fi
done

# Create tarball
echo "📦 Creating backup tarball..."
cd /content
tar -czf "reconftw-backup-$(date +%Y%m%d_%H%M%S).tar.gz" reconftw/
cp "reconftw-backup-$(date +%Y%m%d_%H%M%S).tar.gz" "$OUTPUT_DIR/"

# Download to local machine
echo "📥 Downloading files..."
gdown -q "$OUTPUT_DIR"
files.download "$OUTPUT_DIR/*"

echo ""
echo "✅ ALL RESULTS SAVED!"
echo "📁 Location: $OUTPUT_DIR"
echo "📦 Tarball: $OUTPUT_DIR/reconftw-backup-*.tar.gz"

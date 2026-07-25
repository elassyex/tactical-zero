#!/usr/bin/env python3
"""
RECONFTW RESULTS SAVE SCRIPT
Run this AFTER reconftw completes
"""

import os
import shutil
import glob
from google.colab import files

def save_reconftw_results():
    """Save all reconftw results to Google Drive"""
    
    print("💾 Saving reconftw results to Google Drive...")
    print("=" * 60)
    
    # Navigate to reconftw directory
    reconftw_dir = '/content/reconftw'
    os.chdir(reconftw_dir)
    
    # Create output directory with timestamp
    timestamp = __import__('datetime').datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f'/content/drive/MyDrive/reconftw/{timestamp}'
    
    os.makedirs(output_dir, exist_ok=True)
    print(f"📁 Output directory: {output_dir}")
    print(f"📁 Reconftw directory: {reconftw_dir}")
    print("")
    
    # Save all txt files
    print("📋 Saving .txt files...")
    txt_files = glob.glob(f'{reconftw_dir}/*.txt')
    saved = 0
    
    for file in txt_files:
        if file.endswith('.txt'):
            filename = os.path.basename(file)
            shutil.copy2(file, f'{output_dir}/{filename}')
            saved += 1
            print(f"  ✅ {filename}")
    
    # Save all json files
    print("\n📋 Saving .json files...")
    json_files = glob.glob(f'{reconftw_dir}/*.json')
    
    for file in json_files:
        if file.endswith('.json'):
            filename = os.path.basename(file)
            shutil.copy2(file, f'{output_dir}/{filename}')
            saved += 1
            print(f"  ✅ {filename}")
    
    # Save all md files
    print("\n📋 Saving .md files...")
    md_files = glob.glob(f'{reconftw_dir}/*.md')
    
    for file in md_files:
        if file.endswith('.md'):
            filename = os.path.basename(file)
            shutil.copy2(file, f'{output_dir}/{filename}')
            saved += 1
            print(f"  ✅ {filename}")
    
    # Copy all subdirectories
    print("\n📋 Saving subdirectories...")
    for root, dirs, files in os.walk(reconftw_dir):
        for file in files:
            if file.endswith('.txt') or file.endswith('.json') or file.endswith('.md'):
                src = os.path.join(root, file)
                relpath = os.path.relpath(src, reconftw_dir)
                dst = f'{output_dir}/{relpath}'
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
                saved += 1
                print(f"  ✅ {relpath}")
    
    print(f"\n✅ Saved {saved} files to Google Drive!")
    print(f"📁 All files are in: {output_dir}")
    print("")
    
    # Create and download tarball
    print("📦 Creating tarball...")
    tarball_name = f'reconftw-results-{timestamp}.tar.gz'
    tarball_path = f'/content/{tarball_name}'
    
    os.system(f'cd /content/reconftw && tar -czf {tarball_name} .')
    os.system(f'cp {tarball_path} {output_dir}/')
    
    # Download files
    print("📥 Downloading files...")
    files.download(tarball_path)
    files.download(f'{output_dir}/{tarball_name}')
    
    print(f"\n✅ Downloaded: {tarball_name}")
    print("")
    print("=" * 60)
    print("✅ ALL RECONFTW RESULTS SAVED!")
    print("=" * 60)

if __name__ == "__main__":
    save_reconftw_results()

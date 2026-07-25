#!/usr/bin/env python3
"""
COLAB PERSISTENCE MASTER SCRIPT
Run this for bug bounty recon with automatic backup
"""

from google.colab import drive
import os
import subprocess
import datetime
import shutil
from google.colab import files

# ================= CONFIGURATION =================
TARGET = "ory.com"
SAVE_FREQUENCY = 300  # seconds (auto-save every 5 minutes)
DRIVE_PATH = f'/content/drive/MyDrive/bugbounty/{TARGET}'
# =================================================

def mount_drive():
    """Mount Google Drive"""
    print("🔄 Mounting Google Drive...")
    drive.mount('/content/drive', force_remount=True)
    print("✅ Drive mounted")

def create_folders():
    """Create persistent and temporary folders"""
    print(f"📁 Creating folders...")
    
    # Create persistent folder
    os.makedirs(DRIVE_PATH, exist_ok=True)
    
    # Create temporary folder with timestamp
    temp_path = f'/content/hunts/{TARGET}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}'
    os.makedirs(temp_path, exist_ok=True)
    
    return temp_path

def run_recon(target, temp_path):
    """Run bug bounty recon"""
    print(f"🎯 Running recon on: {target}")
    print(f"📁 Temporary path: {temp_path}")
    print(f"💾 Persistent path: {DRIVE_PATH}")
    print("")
    
    # Step 1: Subdomain enumeration
    print("📊 Step 1/4: Subdomain enumeration (subfinder)...")
    try:
        subprocess.run(['subfinder', '-d', target, '-silent', '-o', f'{temp_path}/subdomains.txt'], 
                      check=True, timeout=600)
        print(f"✅ Found {len(open(f'{temp_path}/subdomains.txt').readlines())} subdomains")
    except subprocess.CalledProcessError as e:
        print(f"❌ Subfinder failed: {e}")
    except Exception as e:
        print(f"❌ Error running subfinder: {e}")
    
    # Step 2: HTTP enumeration
    print("\n📊 Step 2/4: HTTP scanning (httpx)...")
    try:
        subprocess.run(['httpx', '-l', f'{temp_path}/subdomains.txt', '-silent', 
                      '-title', '-status-code', '-o', f'{temp_path}/httpx.txt'], 
                      check=True, timeout=600)
        print(f"✅ Found {len(open(f'{temp_path}/httpx.txt').readlines())} live URLs")
    except subprocess.CalledProcessError as e:
        print(f"❌ Httpx failed: {e}")
    except Exception as e:
        print(f"❌ Error running httpx: {e}")
    
    # Step 3: Vulnerability scanning
    print("\n📊 Step 3/4: Vulnerability scanning (nuclei)...")
    try:
        subprocess.run(['nuclei', '-u', f'https://{target}', '-o', f'{temp_path}/nuclei.txt',
                      '-severity', 'critical,high,medium'], 
                      check=True, timeout=600)
        vulns = len(open(f'{temp_path}/nuclei.txt').readlines())
        print(f"✅ Found {vulns} vulnerabilities")
    except subprocess.CalledProcessError as e:
        print(f"❌ Nuclei failed: {e}")
    except Exception as e:
        print(f"❌ Error running nuclei: {e}")
    
    # Step 4: Directory brute force
    print("\n📊 Step 4/4: Directory brute force (ffuf)...")
    try:
        subprocess.run(['ffuf', '-u', f'https://{target}/FUZZ', '-w', '/usr/share/wordlists/dirb/common.txt',
                      '-mr', '200', '-mc', '200,403,404', '-o', f'{temp_path}/dirb.txt'], 
                      check=True, timeout=600)
        dirs = len(open(f'{temp_path}/dirb.txt').readlines())
        print(f"✅ Found {dirs} directories")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ffuf failed: {e}")
    except Exception as e:
        print(f"❌ Error running ffuf: {e}")
    
    print(f"\n✅ Recon complete!")

def save_to_drive(temp_path):
    """Save all results to Google Drive"""
    print(f"💾 Saving results to Google Drive...")
    
    files_saved = 0
    for file in os.listdir(temp_path):
        if file.endswith('.txt'):
            src = os.path.join(temp_path, file)
            dst = os.path.join(DRIVE_PATH, file)
            
            # Copy file
            shutil.copy2(src, dst)
            files_saved += 1
            
            # Download immediately
            files.download(dst)
    
    print(f"✅ Saved {files_saved} files to Google Drive and downloaded!")

def create_tarball(temp_path):
    """Create tarball and download"""
    print(f"📦 Creating tarball...")
    
    tarball_name = f"{TARGET}-results-{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz"
    tarball_path = f"/content/{tarball_name}"
    
    # Create tarball
    os.system(f'cd /content/hunts && tar -czf {tarball_name} {TARGET}*')
    
    # Copy to Drive
    !cp "{tarball_path}" "{DRIVE_PATH}/"
    
    # Download
    files.download(tarball_path)
    files.download(f"{DRIVE_PATH}/{tarball_name}")
    
    print(f"✅ Tarball created and downloaded: {tarball_name}")

def auto_save_loop(temp_path):
    """Auto-save loop for long-running recon"""
    print(f"⏰ Auto-save enabled every {SAVE_FREQUENCY} seconds")
    print("Press Ctrl+C to stop...")
    
    try:
        while True:
            save_to_drive(temp_path)
            print(f"⏰ Next auto-save in {SAVE_FREQUENCY} seconds...")
            time.sleep(SAVE_FREQUENCY)
    except KeyboardInterrupt:
        print(f"\n⏹️  Stopping... Saving final results...")
        save_to_drive(temp_path)
        create_tarball(temp_path)
        print("✅ Results saved!")

def main():
    """Main function"""
    print("=" * 60)
    print("🎯 COLAB PERSISTENCE MASTER SCRIPT")
    print("=" * 60)
    print(f"Target: {TARGET}")
    print(f"Save frequency: {SAVE_FREQUENCY} seconds")
    print("")
    
    # Mount drive
    mount_drive()
    
    # Create folders
    temp_path = create_folders()
    
    # Run recon
    run_recon(TARGET, temp_path)
    
    # Initial save
    save_to_drive(temp_path)
    
    # Create tarball
    create_tarball(temp_path)
    
    # Ask if user wants auto-save
    print("\n" + "=" * 60)
    print("⚙️  Options:")
    print("=" * 60)
    print("1. Auto-save loop (continuously backup every X minutes)")
    print("2. Just exit (all results saved)")
    print("")
    
    choice = input("Enter choice (1 or 2): ")
    
    if choice == "1":
        import time
        auto_save_loop(temp_path)
    else:
        print("\n✅ All results saved! You can now disconnect safely.")
        print("📁 Files are in: " + DRIVE_PATH)

if __name__ == "__main__":
    main()

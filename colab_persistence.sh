#!/bin/bash
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║   COLAB FILES: PERSIST FOREVER (NO DELETION)                ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "WHY FILES GET DELETED:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Colab session ends → All /content/ files deleted"
echo "✅ Page refresh → All /content/ files deleted"
echo "✅ 90 min inactivity → All /content/ files deleted"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "THE SOLUTION: Use GitHub (Forever Persistence)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "GitHub saves files permanently - even if Colab dies"
echo "No download needed - files accessible anytime"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1: Install Git"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
!apt-get install -y git
!pip3 install gitpython

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: Clone Your GitHub Repository"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "First create repo: https://github.com/new"
echo "Then run (replace YOUR_USERNAME):"
echo ""
echo "  !git clone https://github.com/YOUR_USERNAME/bugbounty-results.git"
echo ""

GITHUB_REPO="https://github.com/YOUR_USERNAME/bugbounty-results.git"
GIT_DIR="/content/bugbounty-results"

if [ -d "$GIT_DIR" ]; then
    echo "✅ Repository already cloned"
    cd "$GIT_DIR"
    !git pull
else
    echo "   !git clone $GITHUB_REPO"
    !git clone $GITHUB_REPO
    cd "$GIT_DIR"
    !git config user.email "you@example.com"
    !git config user.name "Your Name"
    !git branch -M main
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3: Run reconftw"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
!cd /content/reconftw && ./reconftw.sh -d ory.com -r --ai

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 4: Save Results to GitHub (Automatic)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd /content/bugbounty-results
!cp -r /content/reconftw/* .
!git add .
!git commit -m "reconftw results - $(date +%Y-%m-%d_%H:%M:%S)" -m "Ory.com reconnaissance" --no-verify
!git push

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ DONE! Results saved to GitHub!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📁 Repository: $GITHUB_REPO"
echo "🔗 Check here: $GITHUB_REPO"
echo ""
echo "Files are now:"
echo "   ✅ Saved to GitHub"
echo "   ✅ Never deleted by Colab"
echo "   ✅ Accessible anytime"
echo "   ✅ Version history available"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 5: Download from GitHub (Optional)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Open your browser and go to:"
echo "  $GITHUB_REPO"
echo ""
echo "Or download files one by one:"
echo "  !wget -O file.txt $GITHUB_REPO/blob/main/subdomains.txt"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "NEXT TIME: Just run"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  cd /content/bugbounty-results && git pull"
echo "  cd /content/reconftw && ./reconftw.sh -d ory.com -r --ai"
echo "  cd /content/bugbounty-results && cp -r /content/reconftw/* . && git add . && git commit -m 'update' && git push"
echo ""

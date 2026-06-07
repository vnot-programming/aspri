#!/usr/bin/env python3
import os
import subprocess
import argparse
import sys

def run_cmd(cmd, cwd=None):
    """Utility function to execute shell commands and handle errors."""
    print(f"Executing: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, text=True, capture_output=True)
    if result.returncode != 0:
        print(f"Error executing command: {result.stderr}", file=sys.stderr)
        sys.exit(result.returncode)
    if result.stdout:
        print(result.stdout.strip())
    return result.stdout

def main():
    parser = argparse.ArgumentParser(description="Git Sparse-Checkout Deployment Helper")
    parser.add_argument(
        "--repo-url", 
        default="git@github.com:vnot-programming/aspri.git", 
        help="Git repository SSH/HTTPS URL"
    )
    parser.add_argument(
        "--branch", 
        default="main", 
        choices=["main", "desk/dev", "core/dev"],
        help="Target branch to checkout/pull (default: main)"
    )
    parser.add_argument(
        "--target-dir", 
        default="/home/my/AspriAI", 
        help="Target directory on the server"
    )
    parser.add_argument(
        "--folder", 
        default="aspri-desk", 
        help="The specific folder to checkout via sparse-checkout (default: aspri-desk)"
    )
    
    args = parser.parse_args()
    
    target_dir = os.path.abspath(args.target_dir)
    git_dir = os.path.join(target_dir, ".git")
    
    # Create target directory if it doesn't exist
    if not os.path.exists(target_dir):
        print(f"📁 Creating target directory: {target_dir}")
        os.makedirs(target_dir)
        
    if not os.path.exists(git_dir):
        print(f"🚀 Initializing repository with sparse-checkout on branch '{args.branch}'...")
        # 1. Clone the repository without checking out files
        run_cmd(f"git clone --filter=blob:none --no-checkout -b {args.branch} {args.repo_url} {target_dir}")
        
        # 2. Configure sparse-checkout to only include the target folder
        run_cmd(f"git sparse-checkout set {args.folder}", cwd=target_dir)
        
        # 3. Checkout the target branch
        run_cmd(f"git checkout {args.branch}", cwd=target_dir)
    else:
        print(f"🔄 Repository already exists at {target_dir}. Syncing branch '{args.branch}'...")
        # 1. Ensure sparse-checkout is correctly configured
        run_cmd(f"git sparse-checkout set {args.folder}", cwd=target_dir)
        
        # 2. Fetch origin updates
        run_cmd("git fetch origin", cwd=target_dir)
        
        # 3. Checkout target branch (force if necessary)
        run_cmd(f"git checkout {args.branch}", cwd=target_dir)
        
        # 4. Pull latest changes
        run_cmd(f"git pull origin {args.branch}", cwd=target_dir)
        
    print(f"✅ Deployment of '{args.folder}' on branch '{args.branch}' completed successfully!")

if __name__ == "__main__":
    main()

# Deployment Scripts & Utilities

This folder contains Python scripts and wrapper scripts to manage deployment, including git sparse checkouts.

## File Structure

- `deploy_helper.py`: Python script utilizing `git sparse-checkout` to pull only a specific subfolder (e.g. `aspri-desk`) from the repository on a target branch.
- `run_deploy.sh`: Bash wrapper script that automatically manages a Python virtual environment (`.venv`), installs dependencies, and runs the helper script.
- `requirements.txt`: Python package dependencies (currently empty, using core libraries only).

## Usage

You can run the script via SSH on the target server.

### 1. Deploy `aspri-desk` using branch `main` (Option 1)
```bash
./scripts/run_deploy.sh --branch main
```

### 2. Deploy `aspri-desk` using branch `desk/dev` (Option 2)
```bash
./scripts/run_deploy.sh --branch desk/dev
```

### Options list

- `--repo-url`: Repository URL (Default: `git@github.com:vnot-programming/aspri.git`)
- `--branch`: Target branch to pull (`main`, `desk/dev`, `core/dev`) (Default: `main`)
- `--target-dir`: Target directory on the server (Default: `/home/my/apps/AspriAI`)
- `--folder`: Subfolder to checkout via sparse-checkout (Default: `aspri-desk`)

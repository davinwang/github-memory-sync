#!/usr/bin/env python3
"""
GitHub Memory Sync - OpenClaw 完整配置备份与迁移工具

同步所有记忆和配置文件到 GitHub，支持服务器迁移。

用法:
    python sync_to_github.py init      # 初始化仓库
    python sync_to_github.py push      # 推送到 GitHub
    python sync_to_github.py pull      # 从 GitHub 拉取
    python sync_to_github.py status    # 查看状态
    python sync_to_github.py migrate   # 迁移模式（拉取到新目录）

环境变量:
    GITHUBTOKEN: GitHub Personal Access Token
    GITHUB_REPO: GitHub 仓库 (username/repo-name)
    GITHUB_BRANCH: 分支名 (默认：main)
    WORKSPACE_DIR: OpenClaw workspace 目录 (默认：~/.openclaw/workspace)
    BACKUP_DIR: 备份目录 (迁移模式使用)
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

# 文件配置
SYNC_FILES = [
    # 核心记忆文件（必须同步）
    "SOUL.md",
    "IDENTITY.md",
    "USER.md",
    "MEMORY.md",
    "TOOLS.md",
    "HEARTBEAT.md",
    "AGENTS.md",
]

SYNC_DIRS = [
    "memory/",      # 日常记忆
    "skills/",      # 自定义技能
    "avatars/",     # 头像图片
]

EXCLUDE_PATTERNS = [
    ".git/",
    "node_modules/",
    "*.log",
    "*.tmp",
    "*.bak",
    "sessions/",
    "__pycache__/",
    "*.pyc",
]


def get_env_config():
    """获取环境变量配置"""
    config = {
        "token": os.environ.get("GITHUBTOKEN"),
        "repo": os.environ.get("GITHUB_REPO"),
        "branch": os.environ.get("GITHUB_BRANCH", "main"),
        "workspace": os.environ.get("WORKSPACE_DIR", str(Path.home() / ".openclaw" / "workspace")),
        "backup_dir": os.environ.get("BACKUP_DIR"),
    }
    
    if not config["token"]:
        print("❌ 错误：缺少 GITHUBTOKEN 环境变量")
        sys.exit(1)
    
    if not config["repo"]:
        print("❌ 错误：缺少 GITHUB_REPO 环境变量")
        sys.exit(1)
    
    return config


def run_command(cmd, cwd=None, check=True):
    """运行 shell 命令"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=check
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.CalledProcessError as e:
        return "", e.stderr, e.returncode


def init_repo(config):
    """初始化 Git 仓库并推送到 GitHub"""
    workspace = config["workspace"]
    token = config["token"]
    repo = config["repo"]
    branch = config["branch"]
    
    print(f"📁 工作目录：{workspace}")
    print(f"📦 GitHub 仓库：{repo}")
    print(f"🌿 分支：{branch}")
    print()
    
    # 检查 workspace 是否存在
    if not os.path.exists(workspace):
        print(f"❌ 工作目录不存在：{workspace}")
        sys.exit(1)
    
    # 初始化 Git（如果还没有）
    git_dir = os.path.join(workspace, ".git")
    if not os.path.exists(git_dir):
        print("🔧 初始化 Git 仓库...")
        stdout, stderr, code = run_command("git init", cwd=workspace)
        if code != 0:
            print(f"❌ Git 初始化失败：{stderr}")
            sys.exit(1)
    
    # 创建 .gitignore
    gitignore_path = os.path.join(workspace, ".gitignore")
    gitignore_content = """# OpenClaw Git Ignore

# Dependencies
node_modules/

# Logs
*.log

# Temporary files
*.tmp
*.bak
__pycache__/
*.pyc

# Sessions (optional, can be large)
sessions/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""
    
    if not os.path.exists(gitignore_path):
        print("📝 创建 .gitignore...")
        with open(gitignore_path, "w") as f:
            f.write(gitignore_content)
    
    # 配置 Git 用户（如果还没有）
    stdout, stderr, code = run_command('git config user.name', cwd=workspace, check=False)
    if not stdout:
        print("🔧 配置 Git 用户...")
        run_command('git config user.name "OpenClaw"', cwd=workspace)
        run_command('git config user.email "openclaw@localhost"', cwd=workspace)
    
    # 添加远程仓库
    remote_url = f"https://{token}@github.com/{repo}.git"
    stdout, stderr, code = run_command("git remote -v", cwd=workspace, check=False)
    if "origin" not in stdout:
        print("🔗 添加远程仓库...")
        run_command(f"git remote add origin {remote_url}", cwd=workspace)
    else:
        print("🔗 更新远程仓库...")
        run_command(f"git remote set-url origin {remote_url}", cwd=workspace)
    
    # 添加文件
    print("📂 添加文件...")
    run_command("git add .", cwd=workspace)
    
    # 提交
    print("💾 提交更改...")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    run_command(f'git commit -m "Backup: {timestamp}"', cwd=workspace, check=False)
    
    # 推送
    print(f"📤 推送到 GitHub ({branch} 分支)...")
    stdout, stderr, code = run_command(f"git push -u origin {branch} --force", cwd=workspace)
    
    if code != 0:
        # 如果远程分支不存在，尝试创建
        if "couldn't find remote ref" in stderr.lower() or "does not match" in stderr.lower():
            print("🌿 创建新分支...")
            run_command(f"git push -u origin {branch}", cwd=workspace)
        else:
            print(f"⚠️ 推送警告：{stderr}")
    
    print()
    print("✅ 初始化完成！")
    print(f"📦 仓库：https://github.com/{repo}")
    print()
    print("下次使用:")
    print("  python sync_to_github.py push   # 推送更新")
    print("  python sync_to_github.py pull   # 拉取更新")
    print("  python sync_to_github.py status # 查看状态")


def push_to_github(config):
    """推送到 GitHub"""
    workspace = config["workspace"]
    branch = config["branch"]
    
    print("📤 推送到 GitHub...")
    print()
    
    # 添加文件
    run_command("git add .", cwd=workspace)
    
    # 检查是否有更改
    stdout, stderr, code = run_command("git status --porcelain", cwd=workspace)
    if not stdout:
        print("✅ 没有更改，无需推送")
        return
    
    # 提交
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"💾 提交更改 ({timestamp})...")
    run_command(f'git commit -m "Backup: {timestamp}"', cwd=workspace, check=False)
    
    # 推送
    print(f"📤 推送到 {branch} 分支...")
    stdout, stderr, code = run_command(f"git push origin {branch}", cwd=workspace)
    
    if code != 0:
        print(f"⚠️ 推送警告：{stderr}")
        # 尝试 force push
        print("🔄 尝试 force push...")
        run_command(f"git push origin {branch} --force", cwd=workspace)
    
    print()
    print("✅ 推送完成！")


def pull_from_github(config):
    """从 GitHub 拉取"""
    workspace = config["workspace"]
    branch = config["branch"]
    
    print("📥 从 GitHub 拉取...")
    print()
    
    # 获取最新
    print("🔄 获取最新提交...")
    run_command("git fetch origin", cwd=workspace)
    
    # 重置本地更改（谨慎操作）
    print("🔄 重置本地更改...")
    run_command("git reset --hard origin/" + branch, cwd=workspace)
    
    # 清理未跟踪文件（可选）
    # run_command("git clean -fd", cwd=workspace)
    
    print()
    print("✅ 拉取完成！")
    print("⚠️ 注意：本地未提交的更改已被覆盖")


def show_status(config):
    """显示状态"""
    workspace = config["workspace"]
    
    print("📊 Git 状态...")
    print()
    
    # Git status
    stdout, stderr, code = run_command("git status", cwd=workspace)
    print(stdout)
    
    # 最近提交
    print("\n📜 最近提交:")
    stdout, stderr, code = run_command("git log --oneline -5", cwd=workspace)
    print(stdout)
    
    # 远程信息
    print("\n🔗 远程仓库:")
    stdout, stderr, code = run_command("git remote -v", cwd=workspace)
    print(stdout)


def migrate_mode(config):
    """迁移模式 - 拉取到新目录"""
    backup_dir = config.get("backup_dir")
    token = config["token"]
    repo = config["repo"]
    branch = config["branch"]
    
    if not backup_dir:
        print("❌ 错误：迁移模式需要 BACKUP_DIR 环境变量")
        sys.exit(1)
    
    print(f"🚀 迁移模式：克隆到 {backup_dir}")
    print()
    
    # 创建备份目录
    os.makedirs(backup_dir, exist_ok=True)
    
    # 克隆仓库
    repo_url = f"https://{token}@github.com/{repo}.git"
    print(f"📥 克隆仓库...")
    stdout, stderr, code = run_command(f"git clone {repo_url} {backup_dir}")
    
    if code != 0:
        print(f"❌ 克隆失败：{stderr}")
        sys.exit(1)
    
    print()
    print("✅ 迁移完成！")
    print(f"📁 备份位置：{backup_dir}")
    print()
    print("下一步:")
    print(f"1. 将 {backup_dir} 中的文件复制到新服务器的 workspace")
    print("2. 保留新服务器的通道配置（openclaw.json 中的凭证）")
    print("3. 运行 openclaw gateway restart 重启服务")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("可用命令:")
        print("  init    - 初始化仓库")
        print("  push    - 推送到 GitHub")
        print("  pull    - 从 GitHub 拉取")
        print("  status  - 查看状态")
        print("  migrate - 迁移模式")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    config = get_env_config()
    
    if command == "init":
        init_repo(config)
    elif command == "push":
        push_to_github(config)
    elif command == "pull":
        pull_from_github(config)
    elif command == "status":
        show_status(config)
    elif command == "migrate":
        migrate_mode(config)
    else:
        print(f"❌ 未知命令：{command}")
        sys.exit(1)


if __name__ == "__main__":
    main()

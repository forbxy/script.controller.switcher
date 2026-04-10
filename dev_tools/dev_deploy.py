"""快速将当前插件代码部署到 Kodi Addons 目录进行测试"""

import os
import sys
import shutil
from pathlib import Path

REMOTE=True

ADDON_ID = "script.controller.switcher"

EXCLUDE_DIRS = {".git", ".idea", "__pycache__", ".vscode", "venv", "dist"}
EXCLUDE_FILES = {"dev_deploy.ps1", ".gitignore", ".DS_Store"}
EXCLUDE_EXTS = {".pyc", ".pyo"}

POSSIBLE_PATHS = [
    Path(os.environ.get("APPDATA", ""), "Kodi", "addons"),
    Path(
        os.environ.get("LOCALAPPDATA", ""),
        "Packages",
        "XBMCFoundation.Kodi_4n2hpmxwrvr6p",
        "LocalCache",
        "Roaming",
        "Kodi",
        "addons",
    ),
]


def find_kodi_addons_path():
    for p in POSSIBLE_PATHS:
        if p.is_dir():
            print(f"\033[32mFound Kodi addons directory at: {p}\033[0m")
            return p
    return None


def should_exclude(entry_name, is_dir):
    if is_dir:
        return entry_name in EXCLUDE_DIRS
    if entry_name in EXCLUDE_FILES:
        return True
    return Path(entry_name).suffix in EXCLUDE_EXTS


def sync_directory(src: Path, dst: Path):
    """镜像同步 src 到 dst，类似 robocopy /MIR"""
    dst.mkdir(parents=True, exist_ok=True)

    src_names = set()
    for entry in src.iterdir():
        if should_exclude(entry.name, entry.is_dir()):
            continue
        src_names.add(entry.name)
        dst_entry = dst / entry.name
        if entry.is_dir():
            sync_directory(entry, dst_entry)
        else:
            if not dst_entry.exists() or entry.stat().st_mtime != dst_entry.stat().st_mtime:
                shutil.copy2(entry, dst_entry)

    # 删除目标中多余的文件/目录（镜像模式）
    if dst.exists():
        for entry in list(dst.iterdir()):
            if entry.name not in src_names:
                if entry.is_dir():
                    shutil.rmtree(entry)
                else:
                    entry.unlink()


def main():
    source = Path(__file__).resolve().parent.parent
    
    if REMOTE or (len(sys.argv) > 1 and sys.argv[1] == "remote"):
        addons_path = Path(r"F:\storage\.kodi\addons")
        print(f"\033[32mUsing remote Kodi addons directory at: {addons_path}\033[0m")
    else:
        addons_path = find_kodi_addons_path()
        if addons_path is None:
            print("\033[31mCould not find Kodi addons directory at any known location.\033[0m", file=sys.stderr)
            sys.exit(1)

    dest = addons_path / ADDON_ID
    print("\033[36m============================\033[0m")
    print(f"\033[36mDeploying {ADDON_ID} to Kodi\033[0m")
    print(f"\033[90mSource: {source}\033[0m")
    print(f"\033[90mDest:   {dest}\033[0m")
    print("\033[36m============================\033[0m")

    print("\033[32mSyncing files...\033[0m")
    try:
        sync_directory(source, dest)
        print("\n\033[32mDeployment Success!\033[0m")
    except Exception as e:
        print(f"\n\033[31mDeployment Failed: {e}\033[0m", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

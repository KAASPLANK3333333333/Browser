#!/usr/bin/env python3
import os
import sys
import zipfile
import shutil
import tempfile
from urllib.request import urlretrieve
from pathlib import Path
import subprocess

# === CONFIGUREER HIER ===
# Een betrouwbare Windows ZIP van een Chromium build (portable) of ungoogled build.
# Vervang deze door de URL die je wilt gebruiken, of laat leeg als je alleen de repo wilt.
CHROMIUM_ZIP_URL = ""  # bijv. "https://example.com/chromium-win.zip"

# Optioneel: repo-zip (rebrand branch)
REPO_ZIP_URL = "https://github.com/KAASPLANK3333333333/Browser/archive/refs/heads/rebrand-and-release.zip"

# Installatiepad (per gebruiker)
TARGET_DIR = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "BrowserPortable"
DESKTOP = Path(os.path.join(os.environ.get("USERPROFILE", Path.home()), "Desktop"))

# Launcher instellingen
LAUNCHER_NAME = "Browser"  # zichtbare naam (niet Google/Chrome)
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"

def download(url, dest):
    print(f"Downloading {url} -> {dest}")
    urlretrieve(url, dest)
    print("Download complete")

def extract(zip_path, dest_dir):
    print(f"Extracting {zip_path} -> {dest_dir}")
    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(dest_dir)
    print("Extract complete")

def find_executable(search_dir):
    # probeer typische locaties te vinden met chrome/chromium exe
    for root, dirs, files in os.walk(search_dir):
        for name in files:
            if name.lower() in ("chrome.exe", "chromium.exe", "browser.exe"):
                return Path(root) / name
    return None

def make_launcher(chromium_exe: Path, target_dir: Path):
    bin_dir = target_dir / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    launcher_bat = bin_dir / f"{LAUNCHER_NAME}.bat"
    # Start-commando met user-agent override en enkele veilige flags
    cmd = f'"{chromium_exe}" --user-agent="{USER_AGENT}" --no-first-run --disable-default-apps %*'
    with open(launcher_bat, "w", encoding="utf-8") as f:
        f.write(f'@echo off\n{cmd}\n')
    # Maak een .lnk snelkoppeling op Desktop (optioneel)
    try:
        create_shortcut(str(launcher_bat), DESKTOP / f"{LAUNCHER_NAME}.lnk", description=f"{LAUNCHER_NAME} browser")
        print("Desktop shortcut created.")
    except Exception as e:
        print("Could not create .lnk shortcut (pywin32 may be required). Created BAT launcher instead.")
    return launcher_bat

def create_shortcut(target, shortcut_path, description=""):
    # maak Windows .lnk, vereist pywin32 (pip install pywin32)
    try:
        import pythoncom
        from win32com.shell import shell, shellcon
        from win32com.client import Dispatch
    except Exception as e:
        raise RuntimeError("pywin32 not installed; install with: pip install pywin32") from e

    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(str(shortcut_path))
    shortcut.Targetpath = str(target)
    shortcut.WorkingDirectory = str(Path(target).parent)
    shortcut.Description = description
    shortcut.save()

def main():
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="browser_dl_"))

    try:
        # 1) download optional chromium build
        if CHROMIUM_ZIP_URL:
            chromium_zip = tmp / "chromium.zip"
            download(CHROMIUM_ZIP_URL, chromium_zip)
            extract(chromium_zip, TARGET_DIR)
        else:
            print("Geen CHROMIUM_ZIP_URL opgegeven — sla chromium build over.")

        # 2) download repo (optioneel) en plaats in target
        repo_zip = tmp / "repo.zip"
        download(REPO_ZIP_URL, repo_zip)
        extract(repo_zip, TARGET_DIR / "source")

        # 3) probeer de exe te vinden
        exe = find_executable(TARGET_DIR)
        if not exe:
            print("Geen chrome/chromium exe gevonden in de uitgepakte bestanden.")
            print("Plaats handmatig een Chromium build in:", TARGET_DIR)
            return 1

        print("Gevonden browser-executable:", exe)
        launcher = make_launcher(exe, TARGET_DIR)
        print("Launcher aangemaakt:", launcher)

        print("\nKlaar. Start de browser via de snelkoppeling op je bureaublad of via:")
        print(launcher)
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

if __name__ == "__main__":
    sys.exit(main())

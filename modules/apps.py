import os
import platform
import subprocess
import json

def get_installed_apps_windows():
    try:
        import winreg
    except ImportError:
        return ["winreg not available, not a Windows system?"]

    apps = []
    reg_paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]

    for root in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
        for path in reg_paths:
            try:
                with winreg.OpenKey(root, path) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, subkey_name) as subkey:
                                name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                apps.append(name)
                        except FileNotFoundError:
                            continue
                        except Exception:
                            continue
            except Exception:
                continue
    return apps

def get_installed_apps_linux():
    apps = set()
    try:
        # Debian/Ubuntu
        result = subprocess.run(['dpkg-query', '-W', '-f=${binary:Package}\n'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        apps.update(result.stdout.strip().split('\n'))
    except Exception:
        pass
    try:
        # RedHat/Fedora
        result = subprocess.run(['rpm', '-qa'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        apps.update(result.stdout.strip().split('\n'))
    except Exception:
        pass
    try:
        # Flatpak
        result = subprocess.run(['flatpak', 'list'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        for line in result.stdout.splitlines():
            apps.add(line.split()[0])
    except Exception:
        pass
    return sorted(apps)

def main():
    system = platform.system()
    print(f"🔍 OS détecté : {system}\n")
    if system == "Windows":
        apps = get_installed_apps_windows()
    elif system == "Linux":
        apps = get_installed_apps_linux()
    else:
        print("❌ OS non supporté.")
        return

    print(f"📦 Applications installées ({len(apps)} trouvées) :\n")
    for i, app in enumerate(apps, 1):
        print(f"{i:03d}. {app}")

if __name__ == "__main__":
    main()

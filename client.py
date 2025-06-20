import os
import sys
import time
import json
import glob
import threading
import shutil

try:
    import msvcrt
except ImportError:
    import termios, tty

DEV_MODE = False

def check_for_updates():
    import urllib.request
    url = "https://raw.githubusercontent.com/exil3net/exilenet-client/main/version.txt"
    try:
        with urllib.request.urlopen(url, timeout=3) as response:
            latest = response.read().decode().strip()
            if latest != "1.00":
                print("\n[UPDATE AVAILABLE] A newer version is available on GitHub. Visit https://github.com/exil3net/exilenet-client\n")
    except:
        print("[INFO] Unable to check for updates. Running in offline mode.\n")

COLORS = {
    "neon_blue": "\033[96m",
    "cyan": "\033[36m",
    "gold": "\033[93m",
    "pink": "\033[95m",
    "red": "\033[91m",
    "reset": "\033[0m"
}

def glitch_effect():
    print(COLORS["red"] + "~" * 40 + COLORS["reset"])
    time.sleep(0.2)

def print_centered(text, color="reset"):
    columns = shutil.get_terminal_size().columns
    print(COLORS[color] + text.center(columns) + COLORS["reset"])

def pause(ms):
    time.sleep(ms / 1000)

def show_splash():
    splash_path = "splash.txt"
    if os.path.exists(splash_path):
        with open(splash_path, "r", encoding="utf-8") as f:
            for line in f:
                print(COLORS["neon_blue"] + line.rstrip() + COLORS["reset"])
                time.sleep(0.005)
    else:
        print("[INFO] splash.txt not found.\n")

def load_motd():
    motd_url = "https://raw.githubusercontent.com/exil3net/exilenet-client/main/motd.txt"
    fallback_path = "motd.txt"
    try:
        import urllib.request
        with urllib.request.urlopen(motd_url, timeout=3) as response:
            msg = response.read().decode().strip()
            print(COLORS["gold"] + "[MOTD] " + msg + COLORS["reset"])
    except:
        if os.path.exists(fallback_path):
            with open(fallback_path, "r", encoding="utf-8") as f:
                print(COLORS["gold"] + "[MOTD] " + f.read().strip() + COLORS["reset"])

paused = False
stop_listener = False

def typewriter(text):
    global paused
    for char in text:
        while paused:
            time.sleep(0.1)
        print(char, end='', flush=True)
        time.sleep(0.01)
    print()

def listen_for_keys():
    global paused, stop_listener
    while not stop_listener:
        if msvcrt.kbhit():
            key = msvcrt.getch().decode('utf-8').lower()
            if key == 'p':
                paused = not paused
                print("\n[" + ("PAUSED" if paused else "RESUMED") + "]\n")
            elif key == 'q':
                print("\n[SESSION TERMINATED]\n")
                os._exit(0)
            elif key == 'h':
                print("\n[HELP] p=pause, q=quit, s=skip, b=back (WIP)\n")
            elif key == 's':
                print("\n[SKIP]\n")
                break
        time.sleep(0.05)

def render_module(content_path):
    global stop_listener
    stop_listener = False

    with open(content_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    print(COLORS['cyan'] + ">>> TRANSMISSION BEGINS <<<" + COLORS['reset'])
    print("[Controls: p=pause, q=quit, h=help]\n")
    time.sleep(1)

    threading.Thread(target=listen_for_keys, daemon=True).start()

    type_mode = True

    for line in lines:
        line = line.strip()
        if line.startswith("[PAUSE:"):
            ms = int(line.replace("[PAUSE:", "").replace("]", ""))
            pause(ms)
        elif line.startswith("[GLITCH"):
            glitch_effect()
        elif "[COLOR:" in line:
            for color in COLORS:
                tag = f"[COLOR:{color}]"
                if tag in line:
                    line = line.replace(tag, COLORS[color])
            line = line.replace("[/COLOR]", COLORS["reset"])
            print(line)
        elif line.startswith("[CENTER]"):
            print_centered(line.replace("[CENTER]", "").strip())
        elif line.startswith("[SCENE:"):
            scene = line.replace("[SCENE:", "").replace("]", "").replace("_", " ").upper()
            print(COLORS["pink"] + f"--- {scene} ---" + COLORS["reset"])
            time.sleep(0.3)
        elif line.strip() == "[TYPEWRITER]":
            type_mode = True
        elif line.strip() == "[/TYPEWRITER]":
            type_mode = False
        elif line.startswith("[HOOK:"):
            hook_name = line.replace("[HOOK:", "").replace("]", "").strip()
            hook_path = os.path.join("hooks", f"{hook_name}.txt")
            if os.path.exists(hook_path):
                with open(hook_path, "r", encoding="utf-8") as hf:
                    for hline in hf:
                        print(COLORS["neon_blue"] + hline.rstrip() + COLORS["reset"])
                        time.sleep(0.002)
            else:
                print(f"[HOOK MISSING: {hook_name}]")
        else:
            if type_mode:
                typewriter(line)
            else:
                print(line)
        time.sleep(0.05)

    stop_listener = True
    time.sleep(0.2)
    print()
    print_centered("“The signal ends... but you're still listening.”", "pink")
    print()
    print(COLORS["gold"] + "[RETURNING TO NODE INTERFACE...]" + COLORS["reset"])
    pause(2000)

def load_modules():
    base = "modules"
    entries = sorted(glob.glob(os.path.join(base, "*")))
    modules = []
    for i, path in enumerate(entries, 1):
        mod_path = os.path.join(path, "module.info")
        try:
            with open(mod_path, "r", encoding="utf-8") as f:
                info = json.load(f)
            modules.append((i, path, info))
        except Exception as e:
            print(f"[ERROR] Skipping {path}: {e}")
    return modules

def main():
    show_splash()
    pause(1500)
    check_for_updates()
    load_motd()

    print(COLORS["cyan"] + "EXILENET CLIENT v1.00" + COLORS["reset"])

    while True:
        modules = load_modules()

        if not modules:
            print("No modules found.")
            return

        print("\nAvailable Modules:")
        for i, _, info in modules:
            title = info.get("title", "Untitled")
            version = info.get("version", "1.0")
            tags = info.get("tags", [])
            mod_type = info.get("module_type", "")
            tag_str = f" [{', '.join(tags)}]" if tags else ""
            print(f"[{i}] {title} (v{version}){tag_str}")

            if DEV_MODE:
                print(f"     ↳ ID: {info.get('id')}, Series: {info.get('series')}, Type: {mod_type}, Timestamp: {info.get('timestamp')}")

        try:
            choice = int(input("\nSelect a module to run (or 0 to exit): "))
            if choice == 0:
                print(COLORS["red"] + "\n[SESSION CLOSED]\n" + COLORS["reset"])
                break
            selected = modules[choice - 1]
            entry_file = selected[2].get("entry", "content.txt")
            content_path = os.path.join(selected[1], entry_file)
            render_module(content_path)
        except (IndexError, ValueError):
            print("Invalid selection. Please try again.")

if __name__ == "__main__":
    main()

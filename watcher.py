import mss
import os
import sys
import time
import threading
import subprocess
import requests

import pytesseract
from PIL import Image


# WATCHER INITIALIZATION
print("==========================================")
print("          WATCHER INITIALIZED")
print("==========================================")


# FIND WATCHER'S FOLDER
if getattr(sys, "frozen", False):
    # PyInstaller one-file extraction directory
    BASE_DIR = sys._MEIPASS
    EXE_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    EXE_DIR = BASE_DIR


# CLOUDFLARE WORKER
WORKER_URL = "https://floral-fire-333b.jsmith0420.workers.dev/"

print("[+] Cloudflare Worker configured")
print(f"    URL: {WORKER_URL}")


# PLATFORM
IS_WINDOWS = sys.platform.startswith("win")
IS_LINUX = sys.platform.startswith("linux")

if IS_WINDOWS:
    print("[+] Platform: Windows")
elif IS_LINUX:
    print("[+] Platform: Linux")
else:
    print(f"[+] Platform: {sys.platform}")


# AUDIO
START_SOUND_PATHS = [
    os.path.join(BASE_DIR, "start_sound.wav"),
    os.path.join(EXE_DIR, "start_sound.wav"),
    os.path.join(BASE_DIR, "_internal", "start_sound.wav"),
    os.path.join(EXE_DIR, "_internal", "start_sound.wav")
]

START_SOUND_PATH = None

for path in START_SOUND_PATHS:
    if os.path.exists(path):
        START_SOUND_PATH = path
        break

if START_SOUND_PATH:
    print("[+] Lizard sound found")
    print(f"    Path: {START_SOUND_PATH}")
else:
    print("[-] Lizard sound not found")


def play_start_sound():
    if not START_SOUND_PATH:
        return

    try:
        if IS_WINDOWS:
            import winsound

            winsound.PlaySound(
                START_SOUND_PATH,
                winsound.SND_FILENAME | winsound.SND_ASYNC
            )

        elif IS_LINUX:
            try:
                result = subprocess.run(
                    ["paplay", START_SOUND_PATH],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

                if result.returncode != 0:
                    subprocess.run(
                        ["aplay", "-q", START_SOUND_PATH],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )

            except FileNotFoundError:
                print("[-] No Linux audio player found")

    except Exception as error:
        print(f"[-] Audio error: {error}")


def play_stop_sound():
    try:
        if IS_WINDOWS:
            import winsound
            winsound.Beep(500, 150)

        elif IS_LINUX:
            print("[+] Scanner stopped")

    except Exception as error:
        print(f"[-] Stop sound error: {error}")


def play_quit_sound():
    try:
        if IS_WINDOWS:
            import winsound
            winsound.Beep(300, 250)

        elif IS_LINUX:
            print("[+] Watcher shutting down")

    except Exception as error:
        print(f"[-] Quit sound error: {error}")


# TESSERACT OCR
if IS_WINDOWS:
    TESSERACT_PATHS = [
        os.path.join(
            BASE_DIR,
            "tesseract",
            "tesseract.exe"
        ),
        os.path.join(
            EXE_DIR,
            "tesseract",
            "tesseract.exe"
        ),
        os.path.join(
            BASE_DIR,
            "_internal",
            "tesseract",
            "tesseract.exe"
        ),
        os.path.join(
            EXE_DIR,
            "_internal",
            "tesseract",
            "tesseract.exe"
        ),
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    ]

else:
    TESSERACT_PATHS = [
        "/usr/bin/tesseract",
        "/usr/local/bin/tesseract"
    ]


TESSERACT_PATH = None

for path in TESSERACT_PATHS:
    if os.path.isfile(path):
        TESSERACT_PATH = path
        break


if TESSERACT_PATH:

    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

    # Tell Tesseract where its language data is.
    tesseract_directory = os.path.dirname(
        TESSERACT_PATH
    )

    tessdata_directory = os.path.join(
        tesseract_directory,
        "tessdata"
    )

    if os.path.isdir(tessdata_directory):
        os.environ["TESSDATA_PREFIX"] = tessdata_directory

        print("[+] Tesseract language data found")
        print(f"    Path: {tessdata_directory}")

    print("[+] Tesseract found")
    print(f"    Path: {TESSERACT_PATH}")

else:

    print("[-] Tesseract not found")
    print("    Checked:")

    for path in TESSERACT_PATHS:
        print(f"    {path}")


# TARGET ITEMS
ETERNAL_ITEMS = [
    "Oni Tiger",
    "Ice Dragon",
    "Fire Dragon",
    "Gorilla King",
    "Eternal Lunar Dragon",
    "Mosasaurus",
    "Phoenix",
    "El Maja",
    "Pegasus",
    "Skeleton Horse"
]

DIVINE_ITEMS = [
    "World Burner",
    "Archangel",
    "Unicorn",
    "Kitsune",
    "Nightflame"
]

TARGETS = {
    "Eternal": ETERNAL_ITEMS,
    "Divine": DIVINE_ITEMS
}


# FIND TARGET
def find_target(text):
    text_lower = text.lower()

    for rarity, items in TARGETS.items():

        rarity_lower = rarity.lower()

        if rarity_lower not in text_lower:
            continue

        for item in items:

            if item.lower() in text_lower:
                return rarity, item

    return None, None


# SEND DISCORD ALERT THROUGH CLOUDFLARE
def send_alert(rarity, item):

    message = (
        f"🚨 {rarity} detected!\n"
        f"**{item}**"
    )

    payload = {
        "message": message
    }

    try:

        response = requests.post(
            WORKER_URL,
            json=payload,
            timeout=10
        )

        if response.ok:

            print(
                "[+] Discord alert sent successfully"
            )

        else:

            print(
                "[-] Cloudflare returned "
                f"HTTP {response.status_code}"
            )

            print(
                f"    Response: {response.text}"
            )

    except requests.RequestException as error:

        print(
            f"[-] Alert request failed: {error}"
        )


# SCANNER CONTROL
scanning = threading.Event()
running = True
last_detected_target = None


def start_scanning():

    if not scanning.is_set():

        scanning.set()

        print("[+] Scanner started")

        play_start_sound()


def stop_scanning():

    if scanning.is_set():

        scanning.clear()

        print("[-] Scanner stopped")

        play_stop_sound()


def quit_program():

    global running

    print("[+] Watcher shutting down...")

    play_quit_sound()

    running = False
    scanning.clear()


# SCANNER
def scan_screen():

    global last_detected_target

    try:

        with mss.MSS() as sct:

            if len(sct.monitors) < 2:

                print(
                    "[-] No display monitor available"
                )

                return

            monitor = sct.monitors[1]

            crop_box = {
                "top": int(
                    monitor["height"] * 0.3
                ),
                "left": int(
                    monitor["width"] * 0.3
                ),
                "width": int(
                    monitor["width"] * 0.4
                ),
                "height": int(
                    monitor["height"] * 0.4
                )
            }

            while running:

                if not scanning.is_set():

                    time.sleep(0.1)
                    continue

                try:

                    screenshot = sct.grab(
                        crop_box
                    )

                    img = Image.frombytes(
                        "RGB",
                        screenshot.size,
                        screenshot.rgb
                    )

                    text = pytesseract.image_to_string(
                        img
                    )

                    rarity, item = find_target(
                        text
                    )

                    if rarity and item:

                        current_target = (
                            rarity,
                            item
                        )

                        print(
                            f"[!!!] {rarity} "
                            f"{item} detected!"
                        )

                        if (
                            current_target
                            != last_detected_target
                        ):

                            send_alert(
                                rarity,
                                item
                            )

                            last_detected_target = (
                                current_target
                            )

                    else:

                        last_detected_target = None

                    time.sleep(2)

                except Exception as error:

                    print(
                        "[-] Error in scan loop: "
                        f"{error}"
                    )

                    time.sleep(2)

    except Exception as error:

        print(
            "[-] Screen capture initialization "
            f"failed: {error}"
        )


# ==========================================================
# KEYBOARD CONTROL
# ==========================================================

def setup_windows_keyboard():

    try:

        import keyboard

        keyboard.add_hotkey(
            "=",
            start_scanning
        )

        keyboard.add_hotkey(
            "-",
            stop_scanning
        )

        keyboard.add_hotkey(
            "q",
            quit_program
        )

        print("[+] Global hotkeys enabled")
        print("    =  START")
        print("    -  STOP")
        print("    Q  QUIT")

        return keyboard

    except Exception as error:

        print(
            "[-] Windows global hotkeys "
            f"unavailable: {error}"
        )

        return None


def terminal_keyboard_loop():

    global running

    import termios
    import tty

    if not sys.stdin.isatty():

        print(
            "[-] Linux terminal input "
            "is unavailable"
        )

        return

    old_settings = termios.tcgetattr(
        sys.stdin
    )

    try:

        tty.setcbreak(
            sys.stdin.fileno()
        )

        print()
        print("[+] Terminal controls enabled")
        print("    =  START")
        print("    -  STOP")
        print("    Q  QUIT")
        print()

        while running:

            key = sys.stdin.read(1)

            if key == "=":

                start_scanning()

            elif key == "-":

                stop_scanning()

            elif key.lower() == "q":

                quit_program()

    except Exception as error:

        print(
            f"[-] Terminal keyboard error: "
            f"{error}"
        )

    finally:

        try:

            termios.tcsetattr(
                sys.stdin,
                termios.TCSADRAIN,
                old_settings
            )

        except Exception:
            pass


def setup_linux_keyboard():

    try:

        import keyboard

        print(
            "[+] Attempting Linux global hotkeys..."
        )

        keyboard.add_hotkey(
            "=",
            start_scanning
        )

        keyboard.add_hotkey(
            "-",
            stop_scanning
        )

        keyboard.add_hotkey(
            "q",
            quit_program
        )

        print(
            "[+] Linux global hotkeys enabled"
        )

        print("    =  START")
        print("    -  STOP")
        print("    Q  QUIT")

        return keyboard, False

    except Exception as error:

        print(
            "[-] Linux global hotkeys "
            "unavailable"
        )

        print(
            f"    Reason: {error}"
        )

        print(
            "[+] Falling back to "
            "terminal controls"
        )

        return None, True


# ==========================================================
# START KEYBOARD SYSTEM
# ==========================================================

keyboard_module = None
terminal_mode = False


if IS_WINDOWS:

    keyboard_module = (
        setup_windows_keyboard()
    )

    if keyboard_module is None:

        print(
            "[-] Watcher cannot start "
            "keyboard controls"
        )

        running = False


elif IS_LINUX:

    (
        keyboard_module,
        terminal_mode
    ) = setup_linux_keyboard()


else:

    print(
        "[-] Unsupported platform "
        "for keyboard controls"
    )

    running = False


# ==========================================================
# START SCANNER THREAD
# ==========================================================

if running:

    scanner_thread = threading.Thread(
        target=scan_screen,
        daemon=True
    )

    scanner_thread.start()


# ==========================================================
# MAIN PROGRAM LOOP
# ==========================================================

try:

    if running and terminal_mode:

        terminal_keyboard_loop()

    else:

        while running:

            time.sleep(1)

except KeyboardInterrupt:

    print("\nWatcher stopped.")

    quit_program()

finally:

    scanning.clear()

    if keyboard_module is not None:

        try:

            keyboard_module.unhook_all()

        except Exception:

            pass

    print("[+] Watcher stopped.")

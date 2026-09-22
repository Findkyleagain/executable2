import mss
import os
import sys
import time
import threading
import subprocess
import requests

import keyboard
import pytesseract
from PIL import Image


# ==========================================
# WATCHER INITIALIZATION
# ==========================================

print("==========================================")
print("          WATCHER INITIALIZED")
print("==========================================")


# ==========================================
# FIND WATCHER'S FOLDER
# ==========================================

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# ==========================================
# CLOUDFLARE WORKER
# ==========================================

WORKER_URL = (
    "https://floral-fire-333b.jsmith0420.workers.dev/"
)

print("[+] Cloudflare Worker configured")
print(f"    URL: {WORKER_URL}")


# ==========================================
# PLATFORM
# ==========================================

IS_WINDOWS = sys.platform.startswith("win")
IS_LINUX = sys.platform.startswith("linux")


if IS_WINDOWS:

    print("[+] Platform: Windows")

elif IS_LINUX:

    print("[+] Platform: Linux")

else:

    print(f"[+] Platform: {sys.platform}")


# ==========================================
# AUDIO
# ==========================================

START_SOUND_PATHS = [
    os.path.join(
        BASE_DIR,
        "start_sound.wav"
    ),
    os.path.join(
        BASE_DIR,
        "_internal",
        "start_sound.wav"
    )
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

            result = subprocess.run(
                [
                    "paplay",
                    START_SOUND_PATH
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            if result.returncode != 0:

                subprocess.run(
                    [
                        "aplay",
                        "-q",
                        START_SOUND_PATH
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

    except Exception as error:

        print(
            f"[-] Audio error: {error}"
        )


def play_stop_sound():

    try:

        if IS_WINDOWS:

            import winsound

            winsound.Beep(
                500,
                150
            )

        elif IS_LINUX:

            print("[+] Scanner stopped")

    except Exception as error:

        print(
            f"[-] Stop sound error: {error}"
        )


def play_quit_sound():

    try:

        if IS_WINDOWS:

            import winsound

            winsound.Beep(
                300,
                250
            )

        elif IS_LINUX:

            print("[+] Watcher shutting down")

    except Exception as error:

        print(
            f"[-] Quit sound error: {error}"
        )


# ==========================================
# TESSERACT OCR
# ==========================================

if IS_WINDOWS:

    TESSERACT_PATHS = [
        os.path.join(
            BASE_DIR,
            "_internal",
            "tesseract",
            "tesseract.exe"
        ),
        os.path.join(
            BASE_DIR,
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

    if os.path.exists(path):

        TESSERACT_PATH = path
        break


if TESSERACT_PATH:

    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

    print("[+] Tesseract found")
    print(f"    Path: {TESSERACT_PATH}")

else:

    print("[-] Tesseract not found")
    print("    Checked:")

    for path in TESSERACT_PATHS:

        print(f"    {path}")


# ==========================================
# TARGET ITEMS
# ==========================================

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


# ==========================================
# FIND TARGET
# ==========================================

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


# ==========================================
# SEND DISCORD ALERT THROUGH CLOUDFLARE
# ==========================================

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


# ==========================================
# SCANNER CONTROL
# ==========================================

scanning = threading.Event()
running = True

# Prevent the same visible target from
# triggering an alert every scan cycle.
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


# ==========================================
# SCANNER
# ==========================================

def scan_screen():

    global last_detected_target

    with mss.MSS() as sct:

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
                        f"[!!!] {rarity} {item} detected!"
                    )

                    # Only alert when this target was
                    # not already detected.
                    if current_target != last_detected_target:

                        send_alert(
                            rarity,
                            item
                        )

                        last_detected_target = (
                            current_target
                        )

                else:

                    # Target disappeared from the screen.
                    # The next appearance can trigger
                    # another notification.
                    last_detected_target = None

                time.sleep(2)

            except Exception as error:

                print(
                    f"[-] Error in scan loop: {error}"
                )

                time.sleep(2)


# ==========================================
# KEYBINDS
# ==========================================

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


print("[+] Keybinds ready")
print("    =  START")
print("    -  STOP")
print("    Q  QUIT")


# ==========================================
# START SCANNER THREAD
# ==========================================

scanner_thread = threading.Thread(
    target=scan_screen,
    daemon=True
)

scanner_thread.start()


# ==========================================
# KEEP WATCHER RUNNING
# ==========================================

try:

    while running:

        time.sleep(1)

except KeyboardInterrupt:

    print("\nWatcher stopped.")

finally:

    scanning.clear()

    keyboard.unhook_all()

    print("[+] Watcher stopped.")

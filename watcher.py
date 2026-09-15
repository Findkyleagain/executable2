import mss
import os
import sys
import time
import threading
import winsound

import keyboard
import pytesseract
from PIL import Image
from mss import mss


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
# START / LIZARD SOUND
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


# ==========================================
# TESSERACT OCR
# ==========================================

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
    )
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
# SCANNER CONTROL
# ==========================================

scanning = threading.Event()
running = True


def start_scanning():

    if not scanning.is_set():

        scanning.set()

        print("[+] Scanner started")

        if START_SOUND_PATH:

            winsound.PlaySound(
                START_SOUND_PATH,
                winsound.SND_FILENAME | winsound.SND_ASYNC
            )


def stop_scanning():

    if scanning.is_set():

        scanning.clear()

        print("[-] Scanner stopped")

        winsound.Beep(
            500,
            150
        )


def quit_program():

    global running

    print("[+] Watcher shutting down...")

    winsound.Beep(
        300,
        250
    )

    running = False
    scanning.clear()


# ==========================================
# SCANNER
# ==========================================

def scan_screen():

    with mss.MSS() as sct:

        monitor = sct.monitors[1]

        crop_box = {
            "top": int(monitor["height"] * 0.3),
            "left": int(monitor["width"] * 0.3),
            "width": int(monitor["width"] * 0.4),
            "height": int(monitor["height"] * 0.4)
        }

        while running:

            if not scanning.is_set():

                time.sleep(0.1)

                continue

            try:

                # Play lizard sound for every scan
                if START_SOUND_PATH:

                    winsound.PlaySound(
                        START_SOUND_PATH,
                        winsound.SND_FILENAME | winsound.SND_ASYNC
                    )

                screenshot = sct.grab(crop_box)

                img = Image.frombytes(
                    "RGB",
                    screenshot.size,
                    screenshot.rgb
                )

                text = pytesseract.image_to_string(img)

                rarity, item = find_target(text)

                if rarity and item:

                    print(
                        f"[!!!] {rarity} {item} detected!"
                    )

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
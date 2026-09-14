import os
import sys
import time
import threading

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
    # TESSERACT OCR
    # ==========================================

TESSERACT_PATH = os.path.join(
    BASE_DIR,
    "tesseract",
    "tesseract.exe"
)

if os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    print("[+] Tesseract found")
else:
    print("[-] Tesseract not found")
    print(f"    Expected: {TESSERACT_PATH}")


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
# SCANNER
# ==========================================

def scan_screen():
    with mss() as sct:

        monitor = sct.monitors[1]

        crop_box = {
            "top": int(monitor["height"] * 0.3),
            "left": int(monitor["width"] * 0.3),
            "width": int(monitor["width"] * 0.4),
            "height": int(monitor["height"] * 0.4)
        }

        print("[+] Scanner started")

        while True:
            try:
                screenshot = sct.grab(crop_box)

                img = Image.frombytes(
                    "RGB",
                    screenshot.size,
                    screenshot.rgb
                )

                text = pytesseract.image_to_string(img)

                rarity, item = find_target(text)

                if rarity and item:
                    print(f"[!!!] {rarity} {item} detected!")

                time.sleep(2)

            except Exception as error:
                print(f"[-] Error in scan loop: {error}")
                time.sleep(2)


# ==========================================
# START SCANNER
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
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\nWatcher stopped.")
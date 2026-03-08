"""
OW2 Scout - Region Calibrator (Manual Crop)
============================================
1. Drop your Overwatch hero-select screenshot into this folder
2. Run: python calibrate.py yourscreenshot.png
3. A window opens — draw a rectangle over the hero-select area
4. Press ENTER to confirm, R to redraw, ESC to cancel
5. Paste the printed CAPTURE_REGION dict into capture.py

Requires: pip install opencv-python
"""

import sys
import cv2
from pathlib import Path

# ── State ─────────────────────────────────────────────────────────────────────
drawing = False
start_x = start_y = end_x = end_y = 0
original_img = None
display_img = None


def draw_callback(event, x, y, flags, param):
    global drawing, start_x, start_y, end_x, end_y, display_img

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        start_x, start_y = x, y
        end_x, end_y = x, y

    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        end_x, end_y = x, y
        display_img = original_img.copy()
        cv2.rectangle(display_img, (start_x, start_y), (end_x, end_y), (0, 255, 80), 2)
        w, h = abs(end_x - start_x), abs(end_y - start_y)
        cv2.putText(display_img, f"{w} x {h}",
                    (min(start_x, end_x), min(start_y, end_y) - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 80), 2)
        cv2.imshow("OW2 Scout Calibrator", display_img)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        end_x, end_y = x, y
        display_img = original_img.copy()
        cv2.rectangle(display_img, (start_x, start_y), (end_x, end_y), (0, 255, 80), 2)
        cv2.putText(display_img, "ENTER=confirm  R=redraw  ESC=cancel",
                    (10, display_img.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 80), 2)
        cv2.imshow("OW2 Scout Calibrator", display_img)


def main():
    global original_img, display_img, start_x, start_y, end_x, end_y

    if len(sys.argv) < 2:
        print("Usage: python calibrate.py <screenshot.png>")
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}")
        sys.exit(1)

    original_img = cv2.imread(str(path))
    if original_img is None:
        print("Could not load image — make sure it's a valid PNG/JPG.")
        sys.exit(1)

    h, w = original_img.shape[:2]
    print(f"[Calibrator] Image loaded: {w}x{h}")
    print("[Calibrator] Draw a rectangle over the hero-select area.")
    print("  ENTER = confirm | R = redraw | ESC = cancel\n")

    display_img = original_img.copy()
    cv2.putText(display_img, "Draw a rectangle over the hero-select area",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 80), 2)

    cv2.namedWindow("OW2 Scout Calibrator", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("OW2 Scout Calibrator", min(w, 1600), min(h, 900))
    cv2.setMouseCallback("OW2 Scout Calibrator", draw_callback)
    cv2.imshow("OW2 Scout Calibrator", display_img)

    while True:
        key = cv2.waitKey(20) & 0xFF

        if key == 13:  # ENTER — confirm
            if start_x == end_x or start_y == end_y:
                print("[Calibrator] No region drawn yet!")
                continue

            left   = min(start_x, end_x)
            top    = min(start_y, end_y)
            width  = abs(end_x - start_x)
            height = abs(end_y - start_y)
            region = {"top": top, "left": left, "width": width, "height": height}

            cropped = original_img[top:top+height, left:left+width]
            preview_path = path.parent / "calibration_crop.png"
            cv2.imwrite(str(preview_path), cropped)
            print(f"[Calibrator] Crop preview saved → {preview_path}")

            print("\n✅  Paste this into capture.py → CAPTURE_REGION:")
            print(f"\nCAPTURE_REGION = {region}\n")
            break

        elif key == ord('r'):  # R — redraw
            display_img = original_img.copy()
            cv2.imshow("OW2 Scout Calibrator", display_img)
            start_x = start_y = end_x = end_y = 0

        elif key == 27:  # ESC — cancel
            print("[Calibrator] Cancelled.")
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
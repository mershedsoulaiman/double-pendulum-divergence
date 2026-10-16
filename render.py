"""Render figures/svg/*.svg to figures/png/*.png with headless Chrome, at 3x.

    python render.py            # all
    python render.py book-01    # only names containing this
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
SVG, PNG = ROOT / "figures" / "svg", ROOT / "figures" / "png"
SCALE = 3
CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "google-chrome", "chromium", "chrome",
]


def chrome():
    for c in CANDIDATES:
        if Path(c).exists() or shutil.which(c):
            return c
    sys.exit("Chrome not found; add its path to CANDIDATES in render.py")


def main():
    exe = chrome()
    PNG.mkdir(parents=True, exist_ok=True)
    want = sys.argv[1] if len(sys.argv) > 1 else ""
    for f in sorted(SVG.glob("*.svg")):
        if want not in f.name:
            continue
        head = f.read_text(encoding="utf-8")[:300]
        w, h = (int(v) for v in re.search(r'width="(\d+)" height="(\d+)"', head).groups())
        out = PNG / (f.stem + ".png")
        subprocess.run([exe, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        f"--force-device-scale-factor={SCALE}", f"--window-size={w},{h}",
                        "--default-background-color=FFFFFFFF", f"--screenshot={out}",
                        f.resolve().as_uri()], check=True, capture_output=True)
        print("rendered", out.relative_to(ROOT), f"{w * SCALE}x{h * SCALE}")


if __name__ == "__main__":
    main()

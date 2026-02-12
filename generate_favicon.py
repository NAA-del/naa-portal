import os
import sys
from PIL import Image

TARGET_SIZE = 512
OUTPUT_REL_PATH = os.path.join("static", "images", "favicon_bg.png")

def find_logo(images_dir, provided_path=None):
    if provided_path:
        if not os.path.isabs(provided_path):
            provided_path = os.path.join(images_dir, provided_path)
        if os.path.isfile(provided_path):
            return provided_path
        raise FileNotFoundError(provided_path)
    names = ("logo", "brand", "icon", "favicon", "mark")
    exts = (".png", ".jpg", ".jpeg", ".webp")
    preferred = []
    others = []
    for entry in os.listdir(images_dir):
        path = os.path.join(images_dir, entry)
        if not os.path.isfile(path):
            continue
        _, ext = os.path.splitext(entry)
        if ext.lower() in exts:
            base = os.path.splitext(entry)[0].lower()
            if any(base.startswith(n) for n in names):
                preferred.append(path)
            else:
                others.append(path)
    if preferred:
        return sorted(preferred)[0]
    if others:
        return sorted(others)[0]
    raise FileNotFoundError(images_dir)

def open_image(path):
    img = Image.open(path)
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    return img

def create_favicon(img, size):
    w, h = img.size
    scale = min(size / w, size / h)
    new_w = max(1, int(round(w * scale)))
    new_h = max(1, int(round(h * scale)))
    resized = img.resize((new_w, new_h), Image.LANCZOS)
    bg = Image.new("RGB", (size, size), (255, 255, 255))
    x = (size - new_w) // 2
    y = (size - new_h) // 2
    bg.paste(resized, (x, y), resized)
    return bg

def main():
    project_root = os.path.dirname(os.path.abspath(__file__))
    images_dir = os.path.join(project_root, "static", "images")
    provided = sys.argv[1] if len(sys.argv) > 1 else None
    logo_path = find_logo(images_dir, provided)
    img = open_image(logo_path)
    out = create_favicon(img, TARGET_SIZE)
    out_path = os.path.join(project_root, OUTPUT_REL_PATH)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    out.save(out_path, format="PNG")
    print(out_path)

if __name__ == "__main__":
    main()

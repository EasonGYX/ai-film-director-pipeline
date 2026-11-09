# 封面生成：墨底 + 竖排标题 + 朱印 + 署名/落款（可配置）+ 英文；输出 JPG
import os, sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
try:
    from PIL import Image, ImageDraw, ImageFont, ImageEnhance
except ImportError:
    sys.exit("缺少依赖 Pillow：pip install -r requirements.txt")

# ===== 改这里：文案 =====
TITLE = os.environ.get("COVER_TITLE", "作品标题")     # 竖排标题，2–7 字最佳
BYLINE = os.environ.get("BYLINE", "")                  # 例：制作：某某（留空则不画）
SCHOOL = os.environ.get("SCHOOL", "")                  # 例：某某大学（留空则不画）
ENGLISH = os.environ.get("COVER_EN", "")               # 例：TITLE IN ENGLISH（留空则不画）

# ===== 改这里：目录与字体 =====
ROOT = os.path.dirname(os.path.abspath(__file__))
WS = os.environ.get("PROJECT_DIR", os.getcwd())          # 默认当前目录（含 生成/ 与 封面/）
OUT = os.path.join(WS, "封面")
FONT_DIR = os.environ.get("FONT_DIR", "C:/Windows/Fonts/")
FONT_KAI = os.environ.get("FONT_KAI", "")    # 中文楷体完整路径（可选）
FONT_SONG = os.environ.get("FONT_SONG", "")  # 中文宋体完整路径（可选）
FONT_EN = os.environ.get("FONT_EN", "")      # 英文衬线完整路径（可选）
COVER_BG = os.environ.get("COVER_BG", os.path.join(WS, "生成", "bg.png"))  # 背景图，缺省纯墨底
os.makedirs(OUT, exist_ok=True)
W, H = 1920, 1080

_missing = set()
def resolve(env_path, filename):
    if env_path and os.path.exists(env_path):
        return env_path
    p = os.path.join(FONT_DIR, filename)
    if os.path.exists(p):
        return p
    _missing.add(filename)
    for fb in ("msyh.ttc", "NotoSansCJK-Regular.ttc", "NotoSansCJKsc-Regular.otf", "wqy-microhei.ttc"):
        fp = os.path.join(FONT_DIR, fb)
        if os.path.exists(fp):
            return fp
    sys.exit(f"找不到字体 {filename}。请设置 FONT_DIR，或用 FONT_KAI / FONT_SONG / FONT_EN 指定字体文件完整路径。")

def font(name, size):
    table = {"simkai.ttf": FONT_KAI, "simsun.ttc": FONT_SONG, "garamond.ttf": FONT_EN}
    return ImageFont.truetype(resolve(table.get(name, ""), name), size)

def draw_ls(d, x, y, t, f, fill, sp):
    for c in t:
        d.text((x, y), c, font=f, fill=fill)
        x += d.textlength(c, font=f) + sp

def backdrop():
    """有背景图就用（裁干净区域），没有就纯墨底"""
    if os.path.exists(COVER_BG):
        im = Image.open(COVER_BG).convert("RGB")
        w, h = im.size
        im = im.crop((int(w * 0.08), int(h * 0.12), int(w * 0.95), int(h * 0.96))).resize((W, H), Image.LANCZOS)
        im = ImageEnhance.Contrast(im).enhance(1.08)
        return ImageEnhance.Brightness(im).enhance(0.82)
    return Image.new("RGB", (W, H), (10, 12, 14))

img = backdrop()
d = ImageDraw.Draw(img)

# 竖排标题：按字数自适应，防止溢出
n = max(1, len(TITLE))
size = min(140, int((H - 380) / (n * 1.12)))
step = int(size * 1.12)
kai = font("simkai.ttf", size)
x_title = 1560
y_start = max(180, (H - n * step) // 2)
cy = y_start
for ch in TITLE:
    d.text((x_title, cy), ch, font=kai, fill=(238, 233, 224))
    cy += step
d.rectangle([x_title - 44, y_start + 12, x_title - 40, cy - 24], fill=(170, 150, 110))
seal_y = min(cy + 8, H - 100)
d.rectangle([x_title, seal_y, x_title + 88, seal_y + 88], fill=(150, 40, 30))
d.text((x_title + 13, seal_y + 6), "记", font=font("simkai.ttf", 62), fill=(245, 240, 230))

# 左下：细线 + 署名/落款（有值才画）+ 英文（限宽自适应）
d.rectangle([150, 826, 560, 829], fill=(150, 140, 120))
y_txt = 852
if BYLINE:
    draw_ls(d, 150, y_txt, BYLINE, font("simsun.ttc", 46), (212, 207, 194), 4)
    y_txt += 66
if SCHOOL:
    draw_ls(d, 150, y_txt, SCHOOL, font("simkai.ttf", 40), (188, 180, 164), 10)
    y_txt += 72
if ENGLISH:
    esz = 26
    while esz > 16 and len(ENGLISH) * esz * 0.62 + 6 * len(ENGLISH) > 1300:
        esz -= 2
    draw_ls(d, 150, max(y_txt, 960), ENGLISH, font("garamond.ttf", esz), (152, 147, 137), 6)

img.save(os.path.join(OUT, "封面_定稿.jpg"), quality=95, subsampling=0)
img.save(os.path.join(OUT, "封面_定稿.png"))
if _missing:
    print("[WARN] 缺少字体，已回退雅黑：", ", ".join(sorted(_missing)), "；非 Windows 请设置 FONT_DIR")
print("OK ->", OUT)

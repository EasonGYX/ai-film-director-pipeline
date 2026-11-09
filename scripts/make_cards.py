# 生成 1080p 卷目卡×N + 引文卡（动态排版：按字数自适应字号/居中/限宽防撞车）
import os, sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("缺少依赖 Pillow：pip install -r requirements.txt")

# ===== 改这里 =====
PROJECT_DIR = os.environ.get("PROJECT_DIR", os.getcwd())          # 与 post_make / make_cover 一致
OUT = os.environ.get("CARDS_DIR", os.path.join(PROJECT_DIR, "后期"))
os.makedirs(OUT, exist_ok=True)
FONT_DIR = os.environ.get("FONT_DIR", "C:/Windows/Fonts/")   # 字体目录，非 Windows 请改
# 字体可分别指定完整路径（优先级高于 FONT_DIR 里的同名文件）
FONT_KAI = os.environ.get("FONT_KAI", "")    # 中文楷体（标题/落款）
FONT_SONG = os.environ.get("FONT_SONG", "")  # 中文宋体（正文/引文）
FONT_EN = os.environ.get("FONT_EN", "")      # 英文衬线（Garamond 等）
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
    sys.exit(f"找不到字体 {filename}。请设置 FONT_DIR 指向中文字体目录，或直接用 FONT_KAI / FONT_SONG / FONT_EN 指定字体文件完整路径。")

def font(name, size):
    table = {"simkai.ttf": FONT_KAI, "simsun.ttc": FONT_SONG, "garamond.ttf": FONT_EN}
    return ImageFont.truetype(resolve(table.get(name, ""), name), size)

def ls_w(d, t, f, sp):
    return sum(d.textlength(c, font=f) + sp for c in t) - sp

def draw_ls(d, x, y, t, f, fill, sp):
    for c in t:
        d.text((x, y), c, font=f, fill=fill)
        x += d.textlength(c, font=f) + sp

def card(cn, en, path):
    img = Image.new("RGB", (W, H), (8, 10, 12))
    d = ImageDraw.Draw(img)
    cx = 1240          # 竖排列
    right_limit = cx - 120  # 英文最大右边界
    left = 210
    max_w = right_limit - left

    # ---- 竖排：字号/步距按可容纳高度自适应 ----
    n = len(cn)
    size = 132
    while True:
        step = int(size * 1.14)
        total = n * step
        if total <= H - 240:  # 上下各留 120
            break
        size -= 6
        if size < 60:
            break
    kai = font("simkai.ttf", size)
    cy = max(120, (H - n * step) // 2)
    y0 = cy
    for ch in cn:
        d.text((cx, cy), ch, font=kai, fill=(235, 230, 220))
        cy += step
    # 竖线：贯穿整列
    d.rectangle([cx - 60, y0 + 12, cx - 55, cy - 24], fill=(170, 150, 110))

    # ---- 英文：限宽自适应，超宽就缩字号 ----
    esz = 45
    while esz > 30:
        e_f = font("garamond.ttf", esz)
        if ls_w(d, en, e_f, 9) <= max_w:
            break
        esz -= 2
    e_f = font("garamond.ttf", esz)
    draw_ls(d, left, 900, en, e_f, (190, 180, 160), 9)

    # ---- 朱印：放在整列下方，不与字重叠，且不越界 ----
    seal_y = cy + 24
    if seal_y + 96 > H - 10:
        seal_y = H - 110
    d.rectangle([cx, seal_y, cx + 96, seal_y + 88], fill=(150, 40, 30))
    d.text((cx + 15, seal_y + 7), "记", font=font("simkai.ttf", 66), fill=(245, 240, 230))
    img.save(path)

# ===== 改这里：章节卡与引文 =====
CHAPTERS = [
    ("卷一·出发", "BOOK ONE · THE ROAD OUT"),
    ("卷二·高昌", "BOOK TWO · GAOCHANG"),
    ("卷三·雪山以西", "BOOK THREE · BEYOND THE SNOWS"),
]
QUOTE_EN = ["From one region, glimpse the whole world;",
            "record the lands beyond, and hold a mirror to China."]
QUOTE_CN = "以一域窥全世，录西域，鉴中华。"
SOURCE = "——《出处》"

for i, (cn, en) in enumerate(CHAPTERS, 1):
    card(cn, en, os.path.join(OUT, f"卡{i}.png"))

# 引文卡：限宽两行 + 中文 + 出处
img = Image.new("RGB", (W, H), (8, 10, 12))
d = ImageDraw.Draw(img)
en_lines = QUOTE_EN
e_f = font("garamond.ttf", 52)
c_f = font("simsun.ttc", 46)
s_f = font("simsun.ttc", 34)
for i, line in enumerate(en_lines):
    while ls_w(d, line, e_f, 6) > W - 400 and e_f.size > 30:
        e_f = font("garamond.ttf", e_f.size - 2)
    w = ls_w(d, line, e_f, 6)
    draw_ls(d, (W - w) / 2, 430 + i * 80, line, e_f, (225, 220, 210), 6)
w = ls_w(d, QUOTE_CN, c_f, 10)
draw_ls(d, (W - w) / 2, 620, QUOTE_CN, c_f, (205, 200, 190), 10)
w = ls_w(d, SOURCE, s_f, 4)
draw_ls(d, (W - w) / 2, 720, SOURCE, s_f, (150, 145, 138), 4)
img.save(os.path.join(OUT, "卡B.png"))
if SOURCE == "——《出处》":
    print("[提醒] 引文卡的出处仍是占位符，请修改脚本顶部的 SOURCE / QUOTE_CN / QUOTE_EN")
if _missing:
    print("[WARN] 缺少字体，已回退：", ", ".join(sorted(_missing)))
    print("       非 Windows 请设置 FONT_DIR，或用 FONT_KAI / FONT_SONG / FONT_EN 指定字体文件")
print("OK", sorted(os.listdir(OUT)))

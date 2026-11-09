# 接触表：把一组图拼成一张审查图（等比缩放 + 黑边填充，不变形）
# 用法：python contact_sheet.py 输出.png 图1.png 图2.png ...
import sys, os

try:
    from PIL import Image
except ImportError:
    sys.exit("缺少依赖 Pillow：pip install -r requirements.txt")

def main():
    if len(sys.argv) < 3:
        print("用法: python contact_sheet.py out.png img1.png img2.png ...")
        return
    out, names = sys.argv[1], sys.argv[2:]
    cols = 3 if len(names) <= 6 else 4
    W, H = 500, 281          # 单格尺寸（16:9）
    rows = (len(names) + cols - 1) // cols
    sheet = Image.new("RGB", (W * cols, H * rows), (20, 20, 20))
    for i, n in enumerate(names):
        if not os.path.exists(n):
            print("跳过（不存在）：", n)
            continue
        im = Image.open(n).convert("RGB")
        # 等比缩放，长边贴合，剩余用深灰填充（letterbox）
        iw, ih = im.size
        s = min(W / iw, H / ih)
        nw, nh = max(1, int(iw * s)), max(1, int(ih * s))
        im = im.resize((nw, nh), Image.LANCZOS)
        cell = Image.new("RGB", (W, H), (12, 12, 12))
        cell.paste(im, ((W - nw) // 2, (H - nh) // 2))
        sheet.paste(cell, ((i % cols) * W, (i // cols) * H))
    sheet.save(out)
    print("OK", out, f"({len(names)} 张)")

if __name__ == "__main__":
    main()

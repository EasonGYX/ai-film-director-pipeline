# 后期合成：归一化片段 + 卡段 -> 拼接 -> 无音轨中间片（声音交给剪映）
# 设计：所有中间片段统一"无音轨"；非 16:9 素材等比缩放 + 黑边，不拉伸。
# 用法：把本文件放到你的项目目录下运行（或设 PROJECT_DIR 指向项目目录）
import os, subprocess, sys, shutil

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# ===== 改这里 =====
WS = os.environ.get("PROJECT_DIR", os.getcwd())          # 项目目录：含 生成/ 与 后期/
FF = os.environ.get("FFMPEG") or shutil.which("ffmpeg")  # 优先环境变量，其次 PATH
G = os.path.join(WS, "生成")      # 视频片段目录
H = os.path.join(WS, "后期")      # 输出目录
TMP = os.path.join(H, "seg")

# 等比缩放 + 黑边（不拉伸），统一 1080p/30fps，加调色与颗粒
VF = ("scale=1920:1080:force_original_aspect_ratio=decrease:flags=lanczos,"
      "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1,fps=30,"
      "eq=saturation=0.92:contrast=1.06,"
      "colorbalance=rs=-0.04:bs=0.06:rh=0.03:bh=-0.02,"
      "unsharp=5:5:0.4,noise=alls=5:allf=t,format=yuv420p")

# 片段清单：(路径, 截取秒数, 输出名)  —— 改这里换成你的镜头列表
SEGS = [
    (os.path.join(G, "clip01.mp4"), 8, "s01"),
    (os.path.join(H, "卡1.png"),    3, "s02"),
    (os.path.join(G, "clip02.mp4"), 8, "s03"),
    (os.path.join(H, "卡B.png"),    6, "s04"),
]

def die(msg):
    print("ERROR:", msg)
    sys.exit(1)

def check_env():
    if not FF:
        die("找不到 ffmpeg。请安装 ffmpeg 并加入 PATH，或用环境变量 FFMPEG 指向可执行文件（macOS/Linux：brew/apt install ffmpeg）")
    if not os.path.isdir(G):
        die(f"找不到视频片段目录：{G}\n请在项目目录下运行（或设置 PROJECT_DIR），脚本从 <项目>/生成/ 读取片段")

def concat_quote(path):
    p = os.path.abspath(path).replace("\\", "/")
    return "file '" + p.replace("'", "'\\''") + "'"

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    if r.returncode != 0:
        die("ffmpeg 失败：\n" + (r.stdout or "")[-400:] + "\n" + (r.stderr or "")[-800:])

def main():
    check_env()
    print("项目目录：", WS)
    print("将按以下清单拼接（顺序即成片顺序，改脚本顶部 SEGS 可调整）：")
    for src, dur, name in SEGS:
        print(f"  {name}: {os.path.basename(src)} / {dur}s")
    os.makedirs(TMP, exist_ok=True)
    lines = []
    for src, dur, name in SEGS:
        if not os.path.exists(src):
            die(f"缺少素材：{src}")
        out = os.path.join(TMP, name + ".mp4")
        if src.lower().endswith(".png"):
            run([FF, "-y", "-loop", "1", "-t", str(dur), "-i", src,
                 "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,"
                        "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1,fps=30,"
                        "noise=alls=4:allf=t,format=yuv420p",
                 "-an", "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", out])
        else:
            run([FF, "-y", "-t", str(dur), "-i", src, "-vf", VF, "-an",
                 "-c:v", "libx264", "-crf", "18", "-preset", "veryfast",
                 "-r", "30", "-pix_fmt", "yuv420p", out])
        print(name, "OK")
        lines.append(concat_quote(out))

    list_path = os.path.join(TMP, "list.txt")
    with open(list_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    out_final = os.path.join(H, "成片_无音轨中间片.mp4")
    run([FF, "-y", "-f", "concat", "-safe", "0", "-i", list_path, "-c", "copy", out_final])
    print("CONCAT OK ->", out_final)
    print("SIZE_MB", round(os.path.getsize(out_final) / 1048576, 1))
    print("提醒：此文件无音轨。配音/字幕/BGM 请在剪映完成后再导出终版。")

if __name__ == "__main__":
    main()

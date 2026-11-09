# 冒烟测试：验证四个脚本与环境（无需真实素材）
# 用法：python examples/smoke_test/smoke.py
# 说明：生成 2 段 3 秒测试片段 + 4 张卡 + 1 张接触表 + 1 张封面，最后拼接并断言输出规格
import os, sys, subprocess, shutil

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(os.path.dirname(ROOT))
SCRIPTS = os.path.join(SKILL, "scripts")
FF = os.environ.get("FFMPEG") or shutil.which("ffmpeg")
if not FF:
    sys.exit("找不到 ffmpeg：请把 ffmpeg 加入 PATH，或设置环境变量 FFMPEG")
BIN = os.path.dirname(FF)
FPROBE = os.path.join(BIN, "ffprobe.exe") if FF.lower().endswith(".exe") else os.path.join(BIN, "ffprobe")
if not os.path.exists(FPROBE):
    FPROBE = shutil.which("ffprobe") or "ffprobe"
PY = sys.executable
FAILS = []

def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore", **kw)
    if r.returncode != 0:
        print("FAIL:", " ".join(map(str, cmd)))
        print((r.stdout or "")[-500:])
        print((r.stderr or "")[-700:])
        FAILS.append(" ".join(map(str, cmd))[:80])
        return None
    return r

def main():
    work = os.path.join(ROOT, "work")
    shutil.rmtree(work, ignore_errors=True)
    gen, post = os.path.join(work, "生成"), os.path.join(work, "后期")
    os.makedirs(gen); os.makedirs(post)

    print("[1/5] 生成两段 3 秒测试片段")
    run([FF, "-y", "-f", "lavfi", "-i", "testsrc=size=640x360:rate=30", "-t", "3",
         "-pix_fmt", "yuv420p", os.path.join(gen, "clip01.mp4")])
    run([FF, "-y", "-f", "lavfi", "-i", "color=c=0x334455:size=854x480:rate=30", "-t", "3",
         "-pix_fmt", "yuv420p", os.path.join(gen, "clip02.mp4")])

    print("[2/5] 卷目卡与引文卡（make_cards.py）")
    run([PY, os.path.join(SCRIPTS, "make_cards.py")], env=dict(os.environ, CARDS_DIR=post))

    print("[3/5] 接触表（contact_sheet.py，横图+方图混排）")
    run([FF, "-y", "-f", "lavfi", "-i", "testsrc=size=1920x1080:rate=1", "-frames:v", "1", os.path.join(work, "wide.png")])
    run([FF, "-y", "-f", "lavfi", "-i", "testsrc=size=1080x1080:rate=1", "-frames:v", "1", os.path.join(work, "square.png")])
    run([PY, os.path.join(SCRIPTS, "contact_sheet.py"), os.path.join(work, "sheet.png"),
         os.path.join(work, "wide.png"), os.path.join(work, "square.png")])

    print("[4/5] 封面（make_cover.py）")
    run([PY, os.path.join(SCRIPTS, "make_cover.py")],
        env=dict(os.environ, PROJECT_DIR=work, COVER_TITLE="测试标题", BYLINE="BY", COVER_EN="SMOKE TEST"))

    print("[5/5] 拼接（post_make.py）")
    run([PY, os.path.join(SCRIPTS, "post_make.py")], env=dict(os.environ, PROJECT_DIR=work, FFMPEG=FF))

    out = os.path.join(post, "成片_无音轨中间片.mp4")
    for f in ("卡1.png", "卡B.png"):
        if not os.path.exists(os.path.join(post, f)):
            FAILS.append(f"未生成 {f}")
    if not os.path.exists(os.path.join(work, "sheet.png")):
        FAILS.append("未生成接触表 sheet.png")
    if not os.path.exists(os.path.join(work, "封面", "封面_定稿.jpg")):
        FAILS.append("未生成封面 封面_定稿.jpg")
    if not os.path.exists(out):
        FAILS.append("未生成成片")
    else:
        r = run([FPROBE, "-v", "error", "-select_streams", "v:0",
                 "-show_entries", "stream=codec_type,width,height,r_frame_rate", "-of", "csv=p=0", out])
        r2 = run([FPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out])
        if r:
            stream = r.stdout.strip().splitlines()[0] if r.stdout.strip() else ""
            print("视频流：", stream)
            if "1920" not in stream or "1080" not in stream:
                FAILS.append(f"分辨率不是 1920x1080：{stream}")
            if "30/1" not in stream:
                FAILS.append(f"帧率不是 30/1：{stream}")
        if r2:
            dur = float(r2.stdout.strip() or 0)
            print("时长：", round(dur, 2), "s")
            if not (13.0 <= dur <= 16.0):
                FAILS.append(f"时长异常：{dur}")
        # 断言无音轨
        ra = run([FPROBE, "-v", "error", "-show_entries", "stream=codec_type", "-of", "csv=p=0", out])
        types = [l.strip() for l in (ra.stdout.splitlines() if ra else []) if l.strip()]
        print("输出流：", types)
        if types != ["video"]:
            FAILS.append(f"输出应只有 video 流，实际：{types}")

    ok = not FAILS
    print("冒烟测试", "通过 ✔" if ok else "失败 ✘")
    if not ok:
        print("失败项：")
        for f in FAILS:
            print(" -", f)
        sys.exit(1)

if __name__ == "__main__":
    main()

# 最小冒烟测试

目的：通过 2 张测试图、2 段各 3 秒的视频、4 张信息卡、
1 张联系表和 1 张封面，验证环境与四个脚本的基本链路是否正常。

最终会生成一段约 15 秒的无音轨测试视频，
并检查视频分辨率、帧率、时长及音轨情况。

## 前置
- Python 3.9+ 与 Pillow（`pip install -r requirements.txt`）
- ffmpeg / ffprobe 可执行（加入 PATH，或用环境变量 `FFMPEG` 指定可执行文件路径）
- 中文字体：Windows 默认读 `C:/Windows/Fonts/`；Linux/macOS 需配置（否则提示找不到楷体）：
```bash
export FONT_DIR=/usr/share/fonts/opentype/noto     # 或任意含中文字体的目录
# 字体文件名不匹配时直接指定文件
export FONT_KAI=/path/NotoSerifCJKsc-Bold.otf
export FONT_SONG=/path/NotoSerifCJKsc-Regular.otf
export FONT_EN=/path/EBGaramond-Regular.ttf
```

## 运行
```bash
python examples/smoke_test/smoke.py
```

它会：
1. 用 ffmpeg 生成两段 3 秒测试片段（一段彩色、一段纯色）
2. 调 `make_cards.py` 出卷目卡与引文卡
3. 调 `contact_sheet.py` 把 1920×1080 与 1080×1080 混排（验证不变形）
4. 调 `post_make.py` 拼接，并用 ffprobe 断言输出**只有 video 流**（无音轨）

通过标准：最后一行打印 `冒烟测试 通过 ✔`。

产物在 `examples/smoke_test/work/`，可随时删。

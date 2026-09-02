#!/usr/bin/env python3
"""生成 Demo 视频: 终端打字动画 + 报告滚动. 输出 demo.mp4 / demo.gif"""
import os
from PIL import Image, ImageDraw, ImageFont
import imageio.v2 as imageio

W, H, FPS = 1280, 720, 28
BG = (14, 17, 23)
FG = (207, 227, 230)
ACC = (59, 216, 155)

def font(sz):
    # 优先带中文的字体(PingFang SC), 否则 Menlo/Courier
    for p in ["/System/Library/Fonts/PingFang.ttc","/System/Library/Fonts/STHeiti Medium.ttc","/System/Library/Fonts/Hiragino Sans GB.ttc","/System/Library/Fonts/Menlo.ttc","/System/Library/Fonts/Courier.ttc"]:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, sz)
            except: pass
    return ImageFont.load_default()

f_small, f_big = font(22), font(30)

def terminal_frame(lines, cursor=True, title="binance-analysis-agent — zsh"):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # 标题栏
    d.rounded_rectangle([0,0,W,46], radius=0, fill=(22,27,34))
    d.text((16,12), title, font=f_small, fill=(120,150,160))
    d.line([0,46,W,46], fill=(35,48,52))
    y = 70
    for i, ln in enumerate(lines):
        color = ACC if ln.startswith(("$","✓")) else FG
        d.text((24, y), ln, font=f_small, fill=color)
        y += 34
    if cursor:
        d.rectangle([24, y+2, 24+12, y+20], fill=ACC)
    return img

LOG = [
    "$ python3 agent.py",
    ">>> 拉取币安行情 + 技术分析 ...",
    ">>> 成功分析 8/8 个币种",
    ">>> 链上信号 20 条",
    "✓ 市场分析报告已生成 output/report.md",
    "",
    "$ # 打开报告: output/demo.html",
    "$ open output/demo.html",
]

def build_terminal_frames():
    frames = []
    # 逐行打字(每行停顿)
    for n in range(1, len(LOG)+1):
        frames.append(terminal_frame(LOG[:n], cursor=True))
    return frames

def build_scroll_frames(report_img, dur=5.0):
    frames = []
    rw, rh = report_img.size
    # 缩到窗口宽度
    scale = (W-80)/rw
    rimg = report_img.resize((int(rw*scale), int(rh*scale)), Image.LANCZOS)
    rw, rh = rimg.size
    total = max(1, rh-(H-120))
    steps = int(dur*FPS)
    for k in range(steps):
        top = int((rh-(H-120)) * (k/steps)) if steps else 0
        crop = rimg.crop((0, top, rw, top+(H-120)))
        img = Image.new("RGB", (W, H), BG)
        img.paste(crop, ((W-rw)//2, 60))
        d = ImageDraw.Draw(img)
        d.rectangle([0,0,W,54], fill=(22,27,34))
        d.text((16,14), "Binance Agent OS 数据分析 Agent — 市场分析报告", font=f_small, fill=ACC)
        frames.append(img)
    return frames

def main():
    t = build_terminal_frames()
    report = imageio.imread("/Users/jnz/binance-analysis-agent/output/demo.png")
    rep = Image.open("/Users/jnz/binance-analysis-agent/output/demo.png").convert("RGB")
    s = build_scroll_frames(rep, 6.0)
    allframes = t + s
    print("total frames:", len(allframes))
    imageio.mimsave("/Users/jnz/binance-analysis-agent/output/demo.mp4", allframes, fps=FPS)
    imageio.mimsave("/Users/jnz/binance-analysis-agent/output/demo.gif", allframes, fps=FPS/2)
    print("demo.mp4 + demo.gif saved")

if __name__ == "__main__":
    main()

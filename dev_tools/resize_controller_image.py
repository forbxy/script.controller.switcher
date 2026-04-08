"""
将遥控器图片调整为500x500，多余部分用透明像素填充，图片居中放置。
用法：
  python resize_controller_image.py [路径...]
  - 不传参数：处理所有 data/*/controller.png
  - 传参数：处理指定的图片文件
"""

import sys
import os
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("需要安装 Pillow: pip install Pillow")
    sys.exit(1)

TARGET_SIZE = (500, 500)


def resize_image(image_path: Path):
    img = Image.open(image_path).convert("RGBA")
    orig_w, orig_h = img.size

    if (orig_w, orig_h) == TARGET_SIZE:
        print(f"  跳过（已是 {TARGET_SIZE[0]}x{TARGET_SIZE[1]}）: {image_path}")
        return

    # 按比例缩放使图片完整放入目标尺寸
    scale = min(TARGET_SIZE[0] / orig_w, TARGET_SIZE[1] / orig_h)
    new_w = int(orig_w * scale)
    new_h = int(orig_h * scale)
    resized = img.resize((new_w, new_h), Image.LANCZOS)

    # 创建透明画布并居中粘贴
    canvas = Image.new("RGBA", TARGET_SIZE, (0, 0, 0, 0))
    offset_x = (TARGET_SIZE[0] - new_w) // 2
    offset_y = (TARGET_SIZE[1] - new_h) // 2
    canvas.paste(resized, (offset_x, offset_y))
    canvas.save(image_path)
    print(f"  已处理 ({orig_w}x{orig_h} -> {TARGET_SIZE[0]}x{TARGET_SIZE[1]}): {image_path}")


def main():
    if len(sys.argv) > 1:
        paths = [Path(p) for p in sys.argv[1:]]
    else:
        # 处理所有 data/*/controller.png
        data_dir = Path(__file__).resolve().parent.parent / "data"
        paths = sorted(data_dir.glob("*/controller.png"))

    if not paths:
        print("未找到任何 controller.png 文件")
        return

    print(f"共 {len(paths)} 个文件待处理")
    for p in paths:
        resize_image(p)
    print("完成")


if __name__ == "__main__":
    main()

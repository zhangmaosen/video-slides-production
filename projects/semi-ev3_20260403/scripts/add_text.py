#!/usr/bin/env python3
"""为幻灯片图片添加文字标题"""
from PIL import Image, ImageDraw, ImageFont
import os

def add_text_to_slide(image_path, output_path, title=None, subtitle=None, data_badge=None):
    """为图片添加文字"""
    img = Image.open(image_path).convert("RGBA")
    width, height = img.size
    
    # 创建文字图层
    txt_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_layer)
    
    # 尝试加载字体
    font_paths = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
    ]
    
    title_font = None
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                title_font = ImageFont.truetype(fp, 80)
                break
            except:
                continue
    
    if title_font is None:
        title_font = ImageFont.load_default()
    
    data_font = None
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                data_font = ImageFont.truetype(fp, 60)
                break
            except:
                continue
    
    if data_font is None:
        data_font = ImageFont.load_default()
    
    # 绘制标题
    if title:
        # 标题位置：顶部居中
        bbox = draw.textbbox((0, 0), title, font=title_font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (width - text_width) // 2
        y = 40
        
        # 文字描边效果
        for dx in [-2, 0, 2]:
            for dy in [-2, 0, 2]:
                if dx == 0 and dy == 0:
                    continue
                draw.text((x + dx, y + dy), title, font=title_font, fill=(0, 0, 0, 180))
        
        # 主标题
        draw.text((x, y), title, font=title_font, fill=(255, 255, 255, 255))
    
    # 绘制数据标签
    if data_badge:
        x, y, text = data_badge
        bbox = draw.textbbox((0, 0), text, font=data_font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # 半透明背景
        padding = 15
        bg_box = (
            x - padding, y - padding,
            x + text_width + padding, y + text_height + padding
        )
        draw.rectangle(bg_box, fill=(0, 0, 0, 150))
        
        # 文字
        draw.text((x, y), text, font=data_font, fill=(255, 255, 255, 255))
    
    # 合并图层
    result = Image.alpha_composite(img, txt_layer)
    result = result.convert("RGB")
    result.save(output_path, "PNG")
    print(f"已添加文字 -> {output_path}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("用法: python3 add_text.py <输入图片> <输出图片> [标题] [数据标签]")
        sys.exit(1)
    
    image_path = sys.argv[1]
    output_path = sys.argv[2]
    title = sys.argv[3] if len(sys.argv) > 3 else None
    data = sys.argv[4] if len(sys.argv) > 4 else None
    
    data_badge = None
    if data:
        # 数据格式: x,y,text
        parts = data.split(",")
        if len(parts) == 3:
            data_badge = (int(parts[0]), int(parts[1]), parts[2])
    
    add_text_to_slide(image_path, output_path, title, data_badge=data_badge)

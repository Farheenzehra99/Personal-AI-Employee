#!/usr/bin/env python3
"""
Generate colorful AI/Robot themed images for LinkedIn posts
Uses simple geometric shapes and gradients to create tech-themed images
"""

from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path

def create_gradient_image(width, height, colors, filename):
    """Create a gradient background image"""
    img = Image.new('RGB', (width, height), color=colors[0])
    draw = ImageDraw.Draw(img)
    
    for y in range(height):
        r = int(colors[0][0] + (colors[1][0] - colors[0][0]) * y / height)
        g = int(colors[0][1] + (colors[1][1] - colors[0][1]) * y / height)
        b = int(colors[0][2] + (colors[1][2] - colors[0][2]) * y / height)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    img.save(filename)
    return img

def create_ai_robot_image(filename):
    """Create a colorful AI/Robot themed image"""
    width, height = 1200, 630  # LinkedIn recommended size
    img = Image.new('RGB', (width, height), color='#0a0a2a')
    draw = ImageDraw.Draw(img)
    
    # Gradient background (purple to blue)
    for y in range(height):
        r = int(10 + 20 * y / height)
        g = int(10 + 50 * y / height)
        b = int(42 + 100 * y / height)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # Draw circuit-like lines
    for i in range(20):
        x1 = i * 60
        y1 = 0
        x2 = x1 + 30
        y2 = height
        draw.line([(x1, y1), (x2, y2)], fill=(0, 255, 255, 100), width=2)
    
    # Draw circles (nodes)
    for i in range(10):
        cx = 100 + i * 120
        cy = 100 + (i % 3) * 150
        for j in range(3):
            draw.ellipse([cx-10, cy-10, cx+10, cy+10], 
                        fill=(0, 255, 255, 150), outline=(255, 255, 255, 200))
            cx += 40
    
    # Draw robot head (simplified)
    center_x, center_y = width // 2, height // 2
    
    # Head outline
    draw.ellipse([center_x-100, center_y-120, center_x+100, center_y+80], 
                fill=(30, 30, 60, 200), outline=(0, 255, 255, 255), width=3)
    
    # Eyes (glowing)
    draw.ellipse([center_x-60, center_y-60, center_x-30, center_y-30], 
                fill=(0, 255, 255, 255), outline=(100, 255, 255, 255), width=2)
    draw.ellipse([center_x+30, center_y-60, center_x+60, center_y-30], 
                fill=(0, 255, 255, 255), outline=(100, 255, 255, 255), width=2)
    
    # Antenna
    draw.line([(center_x, center_y-120), (center_x, center_y-180)], 
              fill=(0, 255, 255, 255), width=4)
    draw.ellipse([center_x-10, center_y-190, center_x+10, center_y-170], 
                fill=(255, 0, 100, 255), outline=(255, 255, 255, 255), width=2)
    
    # AI text
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
    except:
        font = ImageFont.load_default()
    
    # Draw "AI" text
    text = "AI"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_x = (width - text_width) // 2
    draw.text((text_x, center_y + 100), text, fill=(0, 255, 255, 255), font=font)
    
    img.save(filename)
    print(f"Created: {filename}")
    return filename

def create_agents_image(filename):
    """Create colorful AI Agents themed image"""
    width, height = 1200, 630
    img = Image.new('RGB', (width, height), color='#1a0a2e')
    draw = ImageDraw.Draw(img)
    
    # Gradient background (dark purple to orange)
    for y in range(height):
        r = int(26 + 200 * y / height)
        g = int(10 + 100 * y / height)
        b = int(46 + 50 * y / height)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # Draw network nodes
    nodes = [
        (200, 150), (600, 100), (1000, 150),
        (300, 350), (700, 300), (900, 400),
        (400, 500), (800, 500)
    ]
    
    # Connect nodes with lines
    for i, (x1, y1) in enumerate(nodes):
        for j, (x2, y2) in enumerate(nodes[i+1:], i+1):
            if abs(x2 - x1) < 500:
                draw.line([(x1, y1), (x2, y2)], fill=(255, 100, 200, 150), width=2)
    
    # Draw nodes (circles)
    for x, y in nodes:
        # Outer glow
        for r in range(30, 0, -5):
            alpha = int(100 * r / 30)
            draw.ellipse([x-r, y-r, x+r, y+r], 
                        fill=(255, 100, 200, alpha), outline=(255, 200, 255, alpha+50))
    
    # Central AI brain
    center_x, center_y = 600, 315
    for r in range(80, 0, -10):
        draw.ellipse([center_x-r, center_y-r, center_x+r, center_y+r], 
                    fill=(100, 50, 200, int(200 * r / 80)), 
                    outline=(255, 100, 255, 255), width=2)
    
    # Text
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
    except:
        font = ImageFont.load_default()
    
    draw.text((450, 520), "AI AGENTS", fill=(255, 255, 255, 255), font=font)
    
    img.save(filename)
    print(f"Created: {filename}")
    return filename

def create_automation_image(filename):
    """Create automation themed image"""
    width, height = 1200, 630
    img = Image.new('RGB', (width, height), color='#0a1628')
    draw = ImageDraw.Draw(img)
    
    # Gradient (dark blue to cyan)
    for y in range(height):
        r = int(10 + 0 * y / height)
        g = int(22 + 100 * y / height)
        b = int(40 + 150 * y / height)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # Draw gears
    def draw_gear(cx, cy, size, color):
        # Outer circle
        draw.ellipse([cx-size, cy-size, cx+size, cy+size], 
                    fill=color, outline=(200, 200, 200, 255), width=3)
        # Inner circle
        draw.ellipse([cx-size//2, cy-size//2, cx+size//2, cy+size//2], 
                    fill=(10, 30, 50, 255), outline=color, width=2)
        # Teeth
        for i in range(8):
            angle = i * 45
            import math
            tx = cx + (size + 10) * math.cos(math.radians(angle))
            ty = cy + (size + 10) * math.sin(math.radians(angle))
            draw.ellipse([tx-5, ty-5, tx+5, ty+5], fill=color)
    
    draw_gear(300, 315, 100, (0, 200, 255, 255))
    draw_gear(600, 315, 80, (0, 255, 150, 255))
    draw_gear(900, 315, 100, (255, 100, 200, 255))
    
    # Arrows between gears (simple lines)
    draw.line([(420, 315), (500, 315)], fill=(255, 255, 255, 200), width=4)
    draw.line([(700, 315), (780, 315)], fill=(255, 255, 255, 200), width=4)
    
    # Text
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
    except:
        font = ImageFont.load_default()
    
    draw.text((450, 520), "AUTOMATION", fill=(255, 255, 255, 255), font=font)
    
    img.save(filename)
    print(f"Created: {filename}")
    return filename

def main():
    output_dir = Path('/mnt/d/personal-ai-employee/linkedin_images')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Creating colorful AI-themed images for LinkedIn...")
    
    # Create images
    create_ai_robot_image(output_dir / 'ai_robot.png')
    create_agents_image(output_dir / 'ai_agents.png')
    create_automation_image(output_dir / 'automation.png')
    
    print(f"\nAll images saved to: {output_dir}")
    print("Ready to use with LinkedIn posts!")

if __name__ == "__main__":
    main()

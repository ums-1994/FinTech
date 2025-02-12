from PIL import Image, ImageDraw, ImageFont
import random

def create_budgetbuddy_logo():
    # Create an image canvas
    width, height = 1200, 800
    img = Image.new("RGB", (width, height), "#f8f9fa")
    draw = ImageDraw.Draw(img)
    
    # Load fonts
    try:
        title_font = ImageFont.truetype("arial.ttf", 80)
        subtitle_font = ImageFont.truetype("arial.ttf", 40)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
    
    # Draw gradient background
    for y in range(height):
        r = int(96 + (159 - 96) * (y / height))
        g = int(125 + (168 - 125) * (y / height))
        b = int(139 + (199 - 139) * (y / height))
        draw.line((0, y, width, y), fill=(r, g, b))
    
    # Draw main text
    text = "BudgetBuddy"
    text_width, text_height = draw.textsize(text, font=title_font)
    text_x = (width - text_width) // 2
    text_y = (height - text_height) // 2 - 50
    draw.text((text_x, text_y), text, fill="#2962FF", font=title_font)
    
    # Draw subtitle
    subtitle = "Your Personal Finance Manager"
    sub_width, sub_height = draw.textsize(subtitle, font=subtitle_font)
    sub_x = (width - sub_width) // 2
    sub_y = text_y + text_height + 20
    draw.text((sub_x, sub_y), subtitle, fill="#607D8B", font=subtitle_font)
    
    # Draw decorative elements
    for _ in range(50):
        x = random.randint(0, width)
        y = random.randint(0, height)
        size = random.randint(10, 30)
        draw.ellipse((x, y, x+size, y+size), outline="#FF6D00", width=2)
    
    # Save and show the logo
    img.show()
    img.save("budgetbuddy_background.png")

# Generate the logo
create_budgetbuddy_logo()
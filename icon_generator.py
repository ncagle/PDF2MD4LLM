"""
PDF to Markdown Icon Generator
Creates a simple icon representing PDF to Markdown conversion
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_pdf_to_markdown_icon():
    """
    Create a PDF to Markdown converter icon.
    
    Returns:
        None - saves icon files to current directory
    """
    # Icon dimensions (multiple sizes for different uses)
    sizes = [16, 32, 48, 64, 128, 256]
    
    for size in sizes:
        # Create new image with transparent background
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Calculate proportional sizes
        border = max(2, size // 32)
        corner_radius = max(2, size // 16)
        font_size = max(8, size // 8)
        arrow_width = max(2, size // 20)
        
        # Colors
        pdf_color = "#DC143C"      # Crimson red for PDF
        md_color = "#1b628e"       # Blue for Markdown (matches progress bar)
        arrow_color = "#4CAF50"    # Green for conversion arrow
        text_color = "#FFFFFF"     # White text
        
        # Draw PDF document (left side)
        pdf_width = size // 3
        pdf_height = int(size * 0.7)
        pdf_x = size // 6
        pdf_y = (size - pdf_height) // 2
        
        # PDF rectangle with rounded corners
        draw.rounded_rectangle(
            [pdf_x, pdf_y, pdf_x + pdf_width, pdf_y + pdf_height],
            radius=corner_radius,
            fill=pdf_color,
            outline=None
        )
        
        # PDF text
        try:
            # Try to use a system font
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            # Fall back to default font
            font = ImageFont.load_default()
        
        pdf_text = "PDF"
        # Get text bounding box for centering
        bbox = draw.textbbox((0, 0), pdf_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        draw.text(
            (pdf_x + (pdf_width - text_width) // 2, 
             pdf_y + (pdf_height - text_height) // 2),
            pdf_text,
            fill=text_color,
            font=font
        )
        
        # Draw Markdown document (right side)
        md_width = size // 3
        md_height = int(size * 0.7)
        md_x = size - pdf_width - size // 6
        md_y = (size - md_height) // 2
        
        # Draw conversion arrow (center)
        arrow_start_x = pdf_x + pdf_width + max(4, size // 20)
        arrow_end_x = md_x - max(4, size // 20)
        arrow_y = size // 2
        arrow_length = arrow_end_x - arrow_start_x
        
        # Make sure arrow is visible
        if arrow_length > size // 10:
            # Arrow shaft - draw as a thick line
            shaft_width = max(2, size // 25)
            draw.line(
                [arrow_start_x, arrow_y, arrow_end_x - max(6, size // 15), arrow_y],
                fill=arrow_color,
                width=shaft_width
            )
            
            # Arrow head - make it bigger and more visible
            head_size = max(6, size // 12)
            arrow_tip_x = arrow_end_x
            
            # Draw arrow head as a filled triangle
            arrow_head_points = [
                (arrow_tip_x, arrow_y),  # Tip
                (arrow_tip_x - head_size, arrow_y - head_size // 2),  # Top
                (arrow_tip_x - head_size, arrow_y + head_size // 2)   # Bottom
            ]
            draw.polygon(arrow_head_points, fill=arrow_color)
            
            # Add outline to make arrow more visible
            draw.polygon(arrow_head_points, outline="#2E7D32", width=1)
        
        # Markdown rectangle with rounded corners
        draw.rounded_rectangle(
            [md_x, md_y, md_x + md_width, md_y + md_height],
            radius=corner_radius,
            fill=md_color,
            outline=None
        )
        
        # Markdown text/symbol
        md_text = "MD"
        bbox = draw.textbbox((0, 0), md_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        draw.text(
            (md_x + (md_width - text_width) // 2,
             md_y + (md_height - text_height) // 2),
            md_text,
            fill=text_color,
            font=font
        )
        
        # Add small markdown-style lines for larger icons
        if size >= 48:
            line_color = "#FFFFFF"
            line_width = max(1, size // 64)
            line_spacing = max(2, size // 32)
            
            # Add some horizontal lines to represent text
            for i in range(3):
                y_pos = md_y + md_height // 3 + i * line_spacing
                draw.line(
                    [md_x + border, y_pos, md_x + md_width - border, y_pos],
                    fill=line_color,
                    width=line_width
                )
        
        # Save the icon
        filename = f"pdf_icon_{size}x{size}.png"
        img.save(filename, "PNG")
        print(f"Created {filename}")
    
    # Create the main .ico file (Windows icon format)
    # Load all sizes and save as .ico
    icon_images = []
    for size in [16, 32, 48, 64, 128, 256]:
        filename = f"pdf_icon_{size}x{size}.png"
        if os.path.exists(filename):
            icon_images.append(Image.open(filename))
    
    if icon_images:
        # Save as .ico file with multiple sizes
        icon_images[0].save(
            "pdf_icon.ico",
            format="ICO",
            sizes=[(img.width, img.height) for img in icon_images]
        )
        print("Created pdf_icon.ico with multiple sizes")
        
        # Clean up individual PNG files
        for size in [16, 32, 48, 64, 128, 256]:
            filename = f"pdf_icon_{size}x{size}.png"
            if os.path.exists(filename):
                os.remove(filename)
        
        print("Icon creation complete!")
    else:
        print("Error: No icon images were created")

def create_simple_text_icon():
    """
    Create a simpler text-based icon as an alternative.
    """
    size = 256
    img = Image.new("RGBA", (size, size), (255, 255, 255, 255))  # White background
    draw = ImageDraw.Draw(img)
    
    # Draw a simple border
    border_color = "#1b628e"
    border_width = 8
    draw.rectangle(
        [border_width//2, border_width//2, size-border_width//2, size-border_width//2],
        outline=border_color,
        width=border_width
    )
    
    # Large text
    try:
        font = ImageFont.truetype("arial.ttf", 48)
    except:
        font = ImageFont.load_default()
    
    text = "PDF\n→\nMD"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    draw.text(
        ((size - text_width) // 2, (size - text_height) // 2),
        text,
        fill="#1b628e",
        font=font,
        align="center"
    )
    
    img.save("pdf_icon_simple.ico", "ICO")
    print("Created pdf_icon_simple.ico")

if __name__ == "__main__":
    print("Creating PDF to Markdown Converter Icon...")
    
    try:
        create_pdf_to_markdown_icon()
    except Exception as e:
        print(f"Error creating detailed icon: {e}")
        print("Creating simple fallback icon...")
        try:
            create_simple_text_icon()
        except Exception as e2:
            print(f"Error creating simple icon: {e2}")
            print("Please install Pillow: pip install Pillow")

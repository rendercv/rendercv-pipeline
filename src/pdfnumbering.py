import argparse
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import Color
from io import BytesIO
import os


def add_page_numbers(
    input_pdf,
    output_pdf,
    position,
    font_size,
    font_family,
    bottom_margin,
    italic,
    bold,
    color,
):
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    total_pages = len(reader.pages)

    # Register the Charter font if it's being used
    if font_family.lower() == "charter":
        try:
            pdfmetrics.registerFont(
                TTFont("Charter", os.path.join("..", "fonts", "Charter", "Charter.ttf"))
            )
            if bold:
                pdfmetrics.registerFont(
                    TTFont(
                        "Charter-Bold",
                        os.path.join("..", "fonts", "Charter", "Charter-Bold.ttf"),
                    )
                )
            if italic:
                pdfmetrics.registerFont(
                    TTFont(
                        "Charter-Italic",
                        os.path.join("..", "fonts", "Charter", "Charter-Italic.ttf"),
                    )
                )
            if bold and italic:
                pdfmetrics.registerFont(
                    TTFont("..", "fonts", "Charter", "Charter-Bold-Italic.ttf")
                )
        except Exception as e:
            print(f"Error registering Charter font: {e}")
            print("Falling back to Helvetica")
            font_family = "Helvetica"

    for page_num, page in enumerate(reader.pages, 1):
        packet = BytesIO()
        page_width = float(page.mediabox.width)
        page_height = float(page.mediabox.height)
        can = canvas.Canvas(packet, pagesize=(page_width, page_height))

        # Set font and style
        font_name = font_family
        if font_family.lower() == "helvetica":
            if bold and italic:
                font_name = "Helvetica-BoldOblique"
            elif bold:
                font_name = "Helvetica-Bold"
            elif italic:
                font_name = "Helvetica-Oblique"
        else:
            if bold and italic:
                font_name += "-BoldItalic"
            elif bold:
                font_name += "-Bold"
            elif italic:
                font_name += "-Italic"

        try:
            can.setFont(font_name, font_size)
        except Exception as e:
            print(f"Error setting font {font_name}: {e}")
            print("Falling back to Helvetica")
            can.setFont("Helvetica", font_size)

        # Set color
        try:
            can.setFillColor(color)
        except Exception:
            print("Warning, no or wrong color, falling back to default light gray")
            can.setFillColor(Color(134 / 255, 134 / 255, 134 / 255, 1))  # Light gray #868686

        # Set position for page number
        page_text = f"{page_num} / {total_pages}"
        if position == "left":
            x = 50
        elif position == "center":
            can.setFont(
                "Helvetica", font_size
            )  # Temporarily set to Helvetica to get correct width
            text_width = can.stringWidth(page_text)
            x = (page_width - text_width) / 2
            can.setFont(font_name, font_size)  # Set back to the original font
        else:  # right
            x = page_width - 50

        y = bottom_margin  # Distance from bottom

        # Draw the page number
        can.drawString(x, y, page_text)

        can.save()

        packet.seek(0)
        new_page = PdfReader(packet).pages[0]
        page.merge_page(new_page)
        writer.add_page(page)

    with open(output_pdf, "wb") as output_file:
        writer.write(output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add page numbers to a PDF file.")
    parser.add_argument("input_pdf", help="Input PDF file")
    parser.add_argument("output_pdf", help="Output PDF file")
    parser.add_argument(
        "--position",
        choices=["left", "center", "right"],
        default="center",
        help="Position of page numbers (default: center)",
    )
    parser.add_argument(
        "--font-size", type=int, default=9, help="Font size (default: 9)"
    )
    parser.add_argument(
        "--font-family",
        default="Charter",
        help="Font family (default: Charter)",
    )
    parser.add_argument(
        "--bottom-margin",
        type=int,
        default=30,
        help="Distance from bottom of the page (default: 30)",
    )
    parser.add_argument(
        "--italic",
        action="store_true",
        help="Use italic style (default: True)",
        default=True,
    )
    parser.add_argument(
        "--bold", action="store_true", help="Use bold style (default: False)"
    )
    parser.add_argument(
        "--color", help="Color of the page numbers (default: gray)"
    )

    args = parser.parse_args()

    add_page_numbers(
        args.input_pdf,
        args.output_pdf,
        args.position,
        args.font_size,
        args.font_family,
        args.bottom_margin,
        args.italic,
        args.bold,
        args.color,
    )
    print(f"Page numbers added. Output saved to {args.output_pdf}")

from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader

def create_certificate(output_path, recipient, course, start_date, end_date, time_invested, avg_score):
    width, height = landscape(A4)
    c = canvas.Canvas(output_path, pagesize=landscape(A4))
    
    # Background Color
    c.setFillColor(HexColor("#f5f5ff"))
    c.rect(0, 0, width, height, fill=1, stroke=0)
    
    # Title
    c.setFillColor(HexColor("#4338CA"))
    c.setFont("Helvetica-Bold", 40)
    c.drawCentredString(width / 2, height - 100, "Certificate of Completion")
    
    # Recipient Name
    c.setFillColor(HexColor("#333333"))
    c.setFont("Helvetica-Bold", 35)
    c.drawCentredString(width / 2, height - 200, recipient)
    
    # Description
    c.setFillColor(HexColor("#666666"))
    c.setFont("Helvetica", 20)
    text = f"Has successfully completed 50 levels of {course} with outstanding performance."
    c.drawCentredString(width / 2, height - 250, text)
    
    # Statistics
    stats = [
        ("Starting Date", start_date),
        ("Completion Date", end_date),
        ("Time Invested", time_invested),
        ("Average Score", avg_score)
    ]
    x_start = width / 4
    y_start = height - 320
    
    for label, value in stats:
        c.setFillColor(HexColor("#666666"))
        c.setFont("Helvetica", 14)
        c.drawString(x_start, y_start, label)
        c.setFillColor(HexColor("#4338CA"))
        c.setFont("Helvetica-Bold", 18)
        c.drawString(x_start, y_start - 25, value)
        x_start += width / 4
    
    # Signatures
    c.setFillColor(HexColor("#666666"))
    c.setFont("Helvetica", 14)
    c.drawString(width / 4, 100, "Director")
    c.drawString((3 * width) / 4, 100, "Stamp")
    
    # Placeholder for signature and stamp images
    try:
        director_sign = ImageReader("signature.png")
        stamp = ImageReader("stamp.png")
        c.drawImage(director_sign, width / 4 - 75, 120, 150, 50, mask='auto')
        c.drawImage(stamp, (3 * width) / 4 - 50, 120, 100, 100, mask='auto')
    except:
        pass  # Ignore if images are not found
    
    # Save PDF
    c.save()
    print(f"Certificate saved to {output_path}")

# Example usage
create_certificate("certificate.pdf", "Pihoo S. Patel", "Advanced JavaScript Programming", "Jan 15, 2024", "Feb 14, 2024", "45 Hours", "92%")

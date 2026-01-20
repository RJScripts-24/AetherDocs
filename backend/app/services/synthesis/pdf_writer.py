from reportlab.pdfgen import canvas

def create_pdf(text: str, output_path: str):
    c = canvas.Canvas(output_path)
    c.drawString(100, 750, text[:50] + "...") # Truncated for demo
    c.save()

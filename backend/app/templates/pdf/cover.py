def draw_cover(canvas, title):
    canvas.saveState()
    canvas.setFont("Helvetica-Bold", 30)
    canvas.drawString(100, 500, title)
    canvas.restoreState()

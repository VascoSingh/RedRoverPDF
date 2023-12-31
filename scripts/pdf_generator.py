from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Spacer, PageBreak, Image, BaseDocTemplate, Frame, PageTemplate
from reportlab.graphics.shapes import Drawing, String, Rect
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from colorsys import rgb_to_hls, hls_to_rgb

import pandas as pd

def generate_colors(base_color, step=0.2, lightness_factor=0.8):
    """
    Generates colors based on the provided base color. The colors are generated in the HSL color space by varying the hue.
    :param base_color: A tuple representing the base RGB color, e.g., (255, 204, 0)
    :param step: The step size for varying the hue in the HSL space.
    :param lightness_factor: Factor to reduce the lightness for slightly darker colors.
    :return: A generator that yields RGB colors.
    """
    r, g, b = [x/255.0 for x in base_color]
    h, l, s = rgb_to_hls(r, g, b)
    l *= lightness_factor  # Reduce the lightness
    while True:
        h = (h + step) % 1.0
        r, g, b = hls_to_rgb(h, l, s)
        yield (int(r * 255), int(g * 255), int(b * 255))

# Initialize color palette with #c2152d
color_palette = [HexColor('#c2152d')]

# Generate additional colors for the palette
color_generator = generate_colors((255, 204, 0))
for _ in range(999):  # 999 colors to make the total palette size 1000
    color_palette.append(HexColor('#' + ''.join(f'{int(val):02x}' for val in next(color_generator))))

def generate_pdf(data, output_filename):
    frame = Frame(0, 0, letter[0], letter[1], id='normal')
    
    def on_each_page(canvas, doc):
        # Draw a red border
        border_color = HexColor("#993333")
        border_thickness = 2
        offset = 40
        canvas.setStrokeColor(border_color)
        canvas.setLineWidth(border_thickness)
        canvas.rect(offset + border_thickness/2, 
                    offset + border_thickness/2, 
                    letter[0] - 2*offset - border_thickness, 
                    letter[1] - 2*offset - border_thickness)
        
        # Draw the logo on each page
        canvas.drawInlineImage("./data/RedRoverIcon.png", 530, 15, width=70, height=70)

        # Draw page number at the bottom center of the page
        page_num = canvas.getPageNumber()
        canvas.setFont("Helvetica-Bold", 15)
        canvas.setFillColor(HexColor("#993333"))  # Set the fill color for the text
        canvas.drawCentredString(letter[0] / 2.0, 15, f"{page_num}")
    
    template = PageTemplate(id='main', frames=frame, onPage=on_each_page)
    
    # Use BaseDocTemplate instead of SimpleDocTemplate
    doc = BaseDocTemplate(output_filename, pagesize=letter)
    doc.addPageTemplates(template)

    elements = []
    styles = getSampleStyleSheet()

    # Group by question and answer
    grouped_data = data.groupby(['question', 'answer'])

    added_questions = set()

    # Define a new style for the answer text
    answer_style = ParagraphStyle(
    'AnswerStyle', parent=styles['Heading2'], fontSize=20, alignment=TA_LEFT, leftIndent=80
    )

    for (question, answer), group in grouped_data:
        # Add title page for the question if not already added
        if question not in added_questions:
            add_title_page(elements, data, question, styles)
            added_questions.add(question)

        # Move the answer text 40 pixels down using spacers
        elements.append(Spacer(-1, 40))
        elements.append(Paragraph(f"Answer: {answer}", answer_style))
        elements.append(Spacer(1, -20))  # Reset the position for other elements

        # Add demographic pie charts
        add_demographic_pie_charts(elements, group, styles)

        # Add a page break after each question-answer combination
        elements.append(PageBreak())

    # Build the PDF
    doc.build(elements)

def add_title_page(elements, data, question, styles):
    # Modify the Question style to make it bigger and centered
    centered_heading_style = ParagraphStyle(
        'CenteredHeading', parent=styles['Heading1'], fontSize=24, alignment=TA_CENTER, leftIndent=100, rightIndent=100, topIndent=100
    )
    
    # Add spacing to move the question text 50 pixels lower
    elements.append(Spacer(1, 50))
    
    # Question
    elements.append(Paragraph(question, centered_heading_style))
    elements.append(Spacer(1, 24))  # Add some spacing
    
    # Bar chart with overall responses
    question_data = data[data['question'] == question]
    answer_counts = question_data['answer'].value_counts()
    data_dict = answer_counts.to_dict()
    drawing = generate_bar_chart(data_dict)
    elements.append(drawing)
    elements.append(PageBreak())

def add_demographic_pie_charts(elements, group, styles):
    demographics = [
        'educationLevel', 'gender', 'hispanicOrLatino', 'incomeLevel', 'lgbtq',
        'livingSituation', 'occupation', 'pet', 'politicalAffiliation', 'race',
        'religion', 'state', 'school'  # Moved 'school' to the end of the list
    ]
    for demo in demographics:
        demo_data = group[demo].value_counts().to_dict()
        drawing = generate_pie_chart_with_legend(demo_data)
        elements.append(drawing)
        elements.append(Spacer(1, 12))

def generate_bar_chart(data):
    # Adjusting dimensions for a larger and centered bar chart
    drawing = Drawing(500, 250)
    chart = VerticalBarChart()
    chart.x = 115  # Adjusted for centering
    chart.y = 50
    chart.height = 150  # Made larger
    chart.width = 350  # Made larger

    # Display number of votes at the top of each bar
    chart.barLabelFormat = '%d'
    chart.barLabels.nudge = 10  # Adjust to place the label above the bar

    # Data
    chart.data = [list(data.values())]
    chart.categoryAxis.categoryNames = list(data.keys())
    chart.bars[0].fillColor = HexColor("#993333")
    chart.bars[0].strokeColor = HexColor("#993333")
    # Assuming the first entry is the winner, change its color
    if len(chart.bars) > 0:
        chart.bars[0].fillColor = HexColor("#a91e22")

    # Ensure the y-axis starts at 0
    chart.valueAxis.valueMin = 0

    drawing.add(chart)
    return drawing

def generate_pie_chart_with_legend(data):
    drawing = Drawing(400, 200)
    pie = Pie()
    pie.x = 100
    pie.y = 0
    pie.width = 150
    pie.height = 150

    # Sort the data by values (from largest to smallest)
    sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)
    sorted_labels = [item[0] for item in sorted_data]
    sorted_values = [item[1] for item in sorted_data]

    pie.data = sorted_values
    pie.labels = sorted_labels
    pie.simpleLabels = 0
    pie.slices.label_pointer_piePad = 10
    pie.slices.fontColor = None
    pie.slices.strokeWidth = 0.5
    pie.slices.strokeColor = HexColor("#ffffff")
    pie.slices[0].popout = 10
    total_votes = sum(sorted_values)

    # Assign colors to pie slices
    for i in range(len(pie.data)):
        pie.slices[i].fillColor = color_palette[i % len(color_palette)]
    
    drawing.add(pie)

    # Add legend in two columns
    x_pos = 270  # Starting x position
    y_pos = 130  # Starting y position
    box_size = 10
    items_per_column = len(sorted_labels) // 2 + len(sorted_labels) % 2

    y_start = 130  # Set the starting y position
    y_pos = y_start

    max_chars_per_line = 30  # Maximum characters per line

    y_pos_offsets = [0]  # List to store the y position offsets for each legend item

    # First pass: Calculate y position offsets for each legend item based on the number of lines
    for i, label in enumerate(sorted_labels):
        value = data[label]
        percentage = (value / total_votes) * 100
        legend_text = f"{label} ({percentage:.1f}%)"

        words = legend_text.split()
        lines = []
        current_line = words[0]
        for word in words[1:]:
            if len(current_line + ' ' + word) <= max_chars_per_line:
                current_line += ' ' + word
            else:
                lines.append(current_line)
                current_line = word
        lines.append(current_line)

        y_pos_offsets.append(len(lines) - 1)  # Store the y offset for this legend item

    # Second pass: Draw the legend items using the calculated y position offsets
    for i, label in enumerate(sorted_labels):
        if i == items_per_column:
            y_pos = y_start  # Reset y position when transitioning to second column
        if i >= items_per_column:
            x_pos = 415
            y_pos -= y_pos_offsets[i - items_per_column + 1]  # Use the y position offset for this legend item
        else:
            y_pos -= y_pos_offsets[i]  # Use the y position offset for this legend item

        value = data[label]
        percentage = (value / total_votes) * 100
        legend_text = f"{label} ({percentage:.1f}%)"

        words = legend_text.split()
        lines = []
        current_line = words[0]
        for word in words[1:]:
            if len(current_line + ' ' + word) <= max_chars_per_line:
                current_line += ' ' + word
            else:
                lines.append(current_line)
                current_line = word
        lines.append(current_line)

        drawing.add(Rect(x_pos, y_pos, box_size, box_size, fillColor=color_palette[i % len(color_palette)], strokeColor=color_palette[i % len(color_palette)]))
        for line in lines:
            drawing.add(String(x_pos + 15, y_pos + 2, line))
            y_pos -= 13.5

    return drawing

# Generating the PDF
if __name__ == "__main__":
    data_df = pd.read_csv("./data/dummyDataFinal.csv")
    output_filename = "./data/sep21_test_pdf.pdf"
    generate_pdf(data_df, output_filename)
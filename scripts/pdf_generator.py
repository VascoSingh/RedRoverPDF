from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Spacer, PageBreak, Image, BaseDocTemplate, Frame, PageTemplate
from reportlab.graphics.shapes import Drawing, String, Rect
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT

import pandas as pd

# Define color palette for pie charts
color_palette = [
    HexColor('#ffcc00'),
    HexColor('#ff9900'),
    HexColor('#ff6600'),
    HexColor('#cc3399'),
    HexColor('#990066'),
    HexColor('#3399cc'),
    HexColor('#006699'),
    HexColor('#ccee66'),
    HexColor('#99cc33'),
    HexColor('#669900'),
]

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
        'religion', 'school', 'state'
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
    pie.data = list(data.values())
    pie.labels = list(data.keys())
    pie.simpleLabels = 0
    pie.slices.label_pointer_piePad = 10
    pie.slices.fontColor = None
    pie.slices.strokeWidth = 0.5
    pie.slices.strokeColor = HexColor("#ffffff")
    pie.slices[0].popout = 10
    total_votes = sum(data.values())


    # Color scheme (Removed infinite loop)
    for i in range(len(pie.slices)):
        pie.slices[i].fillColor = color_palette[i % len(color_palette)]

    drawing.add(pie)

    # Add legend
    x_pos = 300
    y_pos = 130
    box_size = 10
    for i, (label, value) in enumerate(data.items()):
        percentage = (value / total_votes) * 100  # Calculate percentage
        drawing.add(Rect(x_pos, y_pos - i * 15, box_size, box_size, fillColor=color_palette[i % len(color_palette)]))
        drawing.add(String(x_pos + 15, y_pos - i * 15 + 2, f"{label} ({percentage:.1f}%)"))  # Display percentage

    return drawing

# Generating the PDF
if __name__ == "__main__":
    data_df = pd.read_csv("./data/combined_dummy_dataset.csv")
    output_filename = "./data/vasco_comment_pdf.pdf"
    generate_pdf(data_df, output_filename)
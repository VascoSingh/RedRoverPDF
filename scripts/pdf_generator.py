from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image
from reportlab.graphics.shapes import Drawing, String, Rect
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.lib.colors import HexColor
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
    doc = SimpleDocTemplate(output_filename, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Group by question and answer
    grouped_data = data.groupby(['question', 'answer'])
    
    added_questions = set()
    
    for (question, answer), group in grouped_data:
        # Add title page for the question if not already added
        if question not in added_questions:
            add_title_page(elements, data, question, styles)
            added_questions.add(question)
        
        # Add "Answer: _____" text only once per answer
        elements.append(Paragraph(f"Answer: {answer}", styles['Heading2']))
        elements.append(Spacer(1, 12))
        
        # Add demographic pie charts
        add_demographic_pie_charts(elements, group, styles)
        
        # Add a page break after each question-answer combination
        elements.append(PageBreak())
    
    # Build the PDF
    doc.build(elements)

def add_title_page(elements, data, question, styles):
    # Logo
    logo = Image("./data/RedRoverIcon.png", width=100, height=100)
    elements.append(logo)
    
    # Question
    elements.append(Paragraph(question, styles['Heading1']))
    
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
    drawing = Drawing(400, 200)
    chart = VerticalBarChart()
    chart.x = 50
    chart.y = 50
    chart.height = 125
    chart.width = 300

    # Data
    chart.data = [list(data.values())]
    chart.categoryAxis.categoryNames = list(data.keys())
    chart.bars[0].fillColor = HexColor("#993333")
    # Assuming the first entry is the winner, change its color
    if len(chart.bars) > 0:
        chart.bars[0].fillColor = HexColor("#a91e22")

    drawing.add(chart)
    return drawing

def generate_pie_chart_with_legend(data):
    drawing = Drawing(400, 200)
    pie = Pie()
    pie.x = 50
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

    # Color scheme (Removed infinite loop)
    for i in range(len(pie.slices)):
        pie.slices[i].fillColor = color_palette[i % len(color_palette)]

    drawing.add(pie)

    # Add legend
    x_pos = 250
    y_pos = 130
    box_size = 10
    for i, (label, value) in enumerate(data.items()):
        drawing.add(Rect(x_pos, y_pos - i * 15, box_size, box_size, fillColor=color_palette[i % len(color_palette)]))
        drawing.add(String(x_pos + 15, y_pos - i * 15 + 2, f"{label} ({value}%)"))

    return drawing

# Generating the PDF
if __name__ == "__main__":
    data_df = pd.read_csv("./data/exported_data - 2023-09-17T091545.392.csv")
    output_filename = "./data/output_pdf.pdf"
    generate_pdf(data_df, output_filename)
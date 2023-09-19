
import pandas as pd
from pdf_generator import generate_pdf

if __name__ == "__main__":
    data_df = pd.read_csv("./data/exported_data - 2023-09-17T091545.392.csv")
    generate_pdf(data_df, "output_pdf.pdf")

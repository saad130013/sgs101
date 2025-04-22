
import streamlit as st
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import arabic_reshaper
from bidi.algorithm import get_display
import tempfile
import os

# تسجيل خط Cairo
font_path = "Cairo-Regular.ttf"
pdfmetrics.registerFont(TTFont("Cairo", font_path))

def fix_arabic(text):
    return get_display(arabic_reshaper.reshape(text))

st.set_page_config(layout="wide")
st.title("📊 نظام رؤيا - توليد تقرير الأصول")

uploaded_file = st.file_uploader("📤 ارفع ملف Excel الخاص بالأصول", type=["xlsx"])
logo_file = "Logo-04.png"

def generate_report(df):
    df = df.dropna(subset=["Asset Description"])
    top_locations = df["Current Location"].value_counts().reset_index()
    top_locations.columns = ["الموقع", "عدد الأصول"]

    top_custodians = df["Custodian"].value_counts().reset_index()
    top_custodians.columns = ["الموظف", "عدد الأصول"]

    top_descriptions = df["Asset Description"].value_counts().reset_index()
    top_descriptions.columns = ["نوع الأصل", "العدد"]

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
        c = canvas.Canvas(tmpfile.name, pagesize=landscape(A4))
        width, height = landscape(A4)

        logo = ImageReader(logo_file)
        c.drawImage(logo, x=40, y=height - 100, width=80, height=80, mask='auto')

        c.setFont("Cairo", 16)
        c.drawCentredString(width / 2 + 40, height - 40, fix_arabic("تقرير ملخص الأصول - هيئة المساحة الجيولوجية السعودية"))

        def draw_table(title_ar, title_en, dataframe, x, y):
            c.setFont("Cairo", 12)
            c.drawString(x, y, fix_arabic(title_ar) + " / " + title_en)
            y -= 20
            c.setFont("Cairo", 8)
            data = [list(dataframe.columns)] + dataframe.astype(str).values.tolist()
            table = Table(data, repeatRows=1)
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("FONTNAME", (0, 0), (-1, -1), "Cairo"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]))
            table.wrapOn(c, width, height)
            table.drawOn(c, x, y - (15 * len(data)))

        draw_table("أكثر المواقع امتلاكًا للأصول", "Top Locations by Asset Count", top_locations, 50, height - 120)
        draw_table("أكثر الموظفين امتلاكًا للأصول", "Top Custodians by Asset Count", top_custodians, 50, height - 320)
        draw_table("أكثر أنواع الأصول تكرارًا", "Top Asset Descriptions", top_descriptions, 50, height - 520)
        c.save()
        return tmpfile.name

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        pdf_path = generate_report(df)
        st.success("✅ تم توليد التقرير بنجاح!")
        with open(pdf_path, "rb") as f:
            st.download_button("📥 تحميل تقرير PDF", f, file_name="SGS_Assets_Report_Bilingual.pdf")
    except Exception as e:
        st.error(f"حدث خطأ أثناء المعالجة: {e}")

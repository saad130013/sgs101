
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

# تسجيل خط Cairo
pdfmetrics.registerFont(TTFont("Cairo", "Cairo-Regular.ttf"))

# دالة إصلاح النص العربي
def fix_arabic(text):
    return get_display(arabic_reshaper.reshape(text))

# تحميل البيانات من Excel
df = pd.read_excel("employee_assets.xlsx", sheet_name="Sheet1")
df = df.dropna(subset=["Asset Description"])

# تحليلات
top_locations = df["Current Location"].value_counts().reset_index()
top_locations.columns = ["الموقع", "عدد الأصول"]

top_custodians = df["Custodian"].value_counts().reset_index()
top_custodians.columns = ["الموظف", "عدد الأصول"]

top_descriptions = df["Asset Description"].value_counts().reset_index()
top_descriptions.columns = ["نوع الأصل", "العدد"]

# إعداد PDF
c = canvas.Canvas("SGS_Assets_Report_Bilingual.pdf", pagesize=landscape(A4))
width, height = landscape(A4)

# الشعار
logo = ImageReader("Logo-04.png")
c.drawImage(logo, x=40, y=height - 100, width=80, height=80, mask='auto')

# عنوان التقرير
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

# رسم الجداول
draw_table("أكثر المواقع امتلاكًا للأصول", "Top Locations by Asset Count", top_locations, 50, height - 120)
draw_table("أكثر الموظفين امتلاكًا للأصول", "Top Custodians by Asset Count", top_custodians, 50, height - 320)
draw_table("أكثر أنواع الأصول تكرارًا", "Top Asset Descriptions", top_descriptions, 50, height - 520)

c.save()
print("✅ تقرير PDF تم إنشاؤه بنجاح باسم: SGS_Assets_Report_Bilingual.pdf")

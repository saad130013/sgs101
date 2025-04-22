
import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("📊 نظام رؤيا - تحليل الأصول")

uploaded_file = st.file_uploader("📤 ارفع ملف Excel الخاص بالأصول", type=["xlsx"])

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        df = df.dropna(subset=["Asset Description"])

        # تحليل البيانات
        top_locations = df["Current Location"].value_counts().reset_index()
        top_locations.columns = ["الموقع", "عدد الأصول"]

        top_custodians = df["Custodian"].value_counts().reset_index()
        top_custodians.columns = ["الموظف", "عدد الأصول"]

        top_descriptions = df["Asset Description"].value_counts().reset_index()
        top_descriptions.columns = ["نوع الأصل", "العدد"]

        # عرض النتائج داخل الصفحة
        st.subheader("📍 أكثر المواقع امتلاكًا للأصول")
        st.dataframe(top_locations)

        st.subheader("👤 أكثر الموظفين امتلاكًا للأصول")
        st.dataframe(top_custodians)

        st.subheader("🧾 أكثر أنواع الأصول تكرارًا")
        st.dataframe(top_descriptions)

    except Exception as e:
        st.error(f"حدث خطأ أثناء المعالجة: {e}")

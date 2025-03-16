import streamlit as st
import pandas as pd
import os
from io import BytesIO

# Page setup
st.set_page_config(page_title="File Converter & Cleaner", layout="wide")
st.title("📁 File Converter & Cleaner")
st.write("Convert your CSV & Excel files with built-in data cleaning and visualization.")

# File uploader
uploaded_files = st.file_uploader("Upload your CSV or Excel file", type=["csv", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_extension = os.path.splitext(file.name)[-1].lower()
        safe_file_key = file.name.replace(".", "_")  

        # Read the uploaded file
        if file_extension == ".csv":
            df = pd.read_csv(file)
        elif file_extension == ".xlsx":
            df = pd.read_excel(file)
        else:
            st.error("❌ Unsupported file type! Please upload a CSV or Excel file.")
            continue

        # Show basic file info
        st.write(f"📄 **File Name:** {file.name}")
        st.write(f"📏 **File Size:** {len(file.getvalue()) / 1024:.2f} KB")
        st.write("**Preview (first 5 rows):**")
        st.dataframe(df.head())

        # Data Cleaning Options
        st.subheader("🧹 Data Cleaning Options")
        if st.checkbox(f"Enable Cleaning for {file.name}", key=f"clean_{safe_file_key}"):
            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"Remove Duplicates From ({file.name})", key=f"remove_duplicates_{safe_file_key}"):
                    df.drop_duplicates(inplace=True)
                    st.success("✅ Duplicates removed!")

            with col2:
                if df.isnull().values.any():  # Only show if missing values exist
                    if st.button(f"Fill Missing Values into ({file.name})", key=f"fill_missing_{safe_file_key}"):
                        numeric_cols = df.select_dtypes(include=['number']).columns
                        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                        st.success("✅ Missing values filled!")

        # Column Selection
        st.subheader("🎯 Select Columns")
        selected_columns = st.multiselect(f"Choose columns to keep ({file.name})", df.columns, default=df.columns, key=f"columns_{safe_file_key}")
        if selected_columns:
            df = df[selected_columns]

        # Data Visualization
        st.subheader("📊 Data Visualization")
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0: 
            if st.checkbox(f"Show Data Visualization for {file.name}", key=f"viz_{safe_file_key}"):
                selected_viz_col = st.selectbox(f"Pick a column for visualization from ({file.name}):", numeric_cols, key=f"viz_col_{safe_file_key}")
                st.bar_chart(df[selected_viz_col])
        else:
            st.warning("⚠ No numeric columns available for visualization.")

        # File Conversion
        st.subheader("🔄 File Conversion Option")
        conversion_type = st.radio(f"Convert {file.name} to:", ("CSV", "Excel"), key=f"convert_{safe_file_key}")

        if st.button(f"Convert {file.name} to {conversion_type}", key=f"convert_btn_{safe_file_key}"):
            buffer = BytesIO()
            new_file_name = file.name.replace(file_extension, f".{conversion_type.lower()}")

            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)
                mime_type = "text/csv"
            else:
                with pd.ExcelWriter(buffer, engine="openpyxl") as writer:   
                    df.to_excel(writer, index=False)
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

            buffer.seek(0)

            # Download button
            st.download_button(
                label=f"📩 Download {new_file_name}",
                data=buffer,
                file_name=new_file_name,
                mime=mime_type,
                key=f"download_{safe_file_key}"
            )

            st.success(f"🎉 {file.name} converted to {conversion_type} successfully!")
import streamlit as st
import pandas as pd
import os
import sqlite3
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
from datetime import datetime

# --- Setup ---
st.set_page_config(page_title="💿 Mine Sweeper", layout="wide")
st.title("💿 Mine Sweeper")
st.write("Upload, clean, and analyze your CSV/Excel data — with automated profiling and upload logging!")

# --- SQLite Setup ---
DB_PATH = "upload_logs.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS uploads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        timestamp TEXT,
        rows INTEGER,
        cols INTEGER
    )''')
    conn.commit()
    conn.close()

def log_upload(filename, rows, cols):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO uploads (filename, timestamp, rows, cols) VALUES (?, ?, ?, ?)",
              (filename, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), rows, cols))
    conn.commit()
    conn.close()

init_db()

# --- File uploader ---
uploaded_files = st.file_uploader("📁 Upload CSV or Excel files:", type=["csv", "xlsx"], accept_multiple_files=True)

# --- Excel Export Helper ---
def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# --- Process Each Uploaded File ---
if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()
        st.divider()
        st.header(f"📄 {file.name}")

        # Load file
        try:
            if file_ext == ".csv":
                df = pd.read_csv(file)
            elif file_ext == ".xlsx":
                df = pd.read_excel(file)
            else:
                st.error(f"❌ Unsupported file type: {file_ext}")
                continue
        except Exception as e:
            st.error(f"⚠️ Failed to read {file.name}: {e}")
            continue

        # Log upload to DB
        log_upload(file.name, df.shape[0], df.shape[1])

        # Preview
        st.subheader("🔍 Preview")
        st.dataframe(df.head(), use_container_width=True)

        # Auto profiling
        st.subheader("📊 Automatic Profiling")
        with st.expander("🧠 Summary Statistics"):
            st.write("**Data Types**")
            st.dataframe(df.dtypes.astype(str))

            st.write("**Missing Values (%)**")
            missing_pct = df.isnull().mean() * 100
            st.dataframe(missing_pct[missing_pct > 0].round(2).to_frame(name='Missing %'))

            numeric_cols = df.select_dtypes(include=['number'])
            if not numeric_cols.empty:
                st.write("**Correlation Heatmap**")
                fig, ax = plt.subplots()
                sns.heatmap(numeric_cols.corr(), annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
                st.pyplot(fig)
            else:
                st.info("No numeric columns available for correlation heatmap.")

        # Cleaning options
        st.subheader("🧹 Data Cleaning & Transformation")
        with st.expander(f"⚙️ Options for: {file.name}"):
            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"🧽 Remove Duplicates ({file.name})"):
                    before = len(df)
                    df.drop_duplicates(inplace=True)
                    after = len(df)
                    st.success(f"✅ Removed {before - after} duplicate rows.")

            with col2:
                if st.button(f"🩹 Fill Missing Values ({file.name})"):
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    if not numeric_cols.empty:
                        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                        st.success("✅ Missing numeric values filled with column mean.")
                    else:
                        st.warning("⚠️ No numeric columns to fill.")

            st.markdown("---")
            selected_cols = st.multiselect("🎯 Select columns to keep", df.columns.tolist(), default=df.columns.tolist())
            if selected_cols:
                df = df[selected_cols]

        # Mini visualization
        st.subheader("📈 Quick Data Snapshot")
        numeric_cols = df.select_dtypes(include=['number']).columns
        if not numeric_cols.empty:
            col = st.selectbox("Choose a numeric column for bar chart:", numeric_cols)
            st.bar_chart(df[col])
        else:
            st.info("ℹ️ No numeric columns found for visualization.")

        # Download cleaned data
        st.subheader("⬇️ Download Cleaned Data")
        excel_data = convert_df_to_excel(df)
        st.download_button(
            label="💾 Download as Excel",
            data=excel_data,
            file_name=f"cleaned_{file.name.replace('.', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# Optional: Show Upload History
with st.expander("🗂️ View Upload History (from SQLite)"):
    conn = sqlite3.connect(DB_PATH)
    history_df = pd.read_sql("SELECT * FROM uploads ORDER BY timestamp DESC", conn)
    conn.close()
    st.dataframe(history_df)

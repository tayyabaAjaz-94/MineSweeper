# imports
import streamlit as st
import pandas as pd
import os
from io import BytesIO


# setup our app
st.set_page_config(page_title="💿Mine sweeper",layout="wide" )
st.title("💿Mine sweeper")
st.write("Transform your files between CVS and Excel formats with built-in data cleaning and visualization!")


# file uploader
uploaded_files= st.file_uploader("upload ypur Files (Accepts CVS or Excel):",type=["CVS","xlsx"],accept_multiple_files=(True))



if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()

        if file_ext == ".csv":
            df =pd.read_csv(file)
        elif file_ext == "xlsx":
                        df =pd.read_excel(file)
        else:
            st.error(f"unsuppotered file type: {file_ext}")
            continue
        # file details
        st.write("🔍 preview the head of the Dataframe")
        st.dataframe(df.head())

        # data cleaning options
        st.subheader("🛠️ data cleaning options")
        if st.checkbox(f"clean data for {file.name}"):
              col1,col2 =st.columns(2)


              with col1:
                    if st.button(f"remove duplicates from the file:{file.name}"):
                          df.drop_duplicates(inplace=True)
                          st.write("✅ dupilicate removed!")
                         
                          with col2:
                                if st.button(f"Fill missing value for {file.name}"):
                                      numeric_cols= df.select_dtypes(includes=['number']).columns
                          df[numeric_cols]=df[numeric_cols].fillna(df[numeric_cols].mean())
                          st.write("✅ missing values has been filled ")
                          
                          
                        #   st.subheader("🎯 select column to keep ")
                        #   columns=st.multiselect(f"choose columns for ")
                          
                        #   st.subheader("📊 Data visualization")
                        #   if st.
                    


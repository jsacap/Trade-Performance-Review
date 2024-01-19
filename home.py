import streamlit as st
import pandas as pd

from data_processing import clean_data

st.title('Trading Edge Auditor')
st.write('Upload and analyze your trade data.')

file_upload = st.file_uploader("Upload your trade data", type=["html", "htm"])


if file_upload:
    cleaned_df = clean_data(file_upload)
    if not cleaned_df.empty:
        st.dataframe(cleaned_df)

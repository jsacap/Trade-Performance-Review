import streamlit as st
import plotly.express as px
import pandas as pd
from data_processing import clean_data, line_chart, drawdown_negative
from metrics import totals_metrics, drawdown_negative_metrics


st.title('Trading Edge Auditor')
st.write('Upload and analyze your trade data.')

file_upload = st.file_uploader("Upload your trade data", type=["html", "htm"])

if file_upload:
    df = clean_data(file_upload)
    # Globals
    lowest_pnl, date_lowest_pnl_str, drawdown_fig, _ = drawdown_negative(df)

    if not df.empty:
        st.dataframe(df)
        totals_metrics(df)
        line_chart(df)
        st.subheader('Drawdown')
        st.plotly_chart(drawdown_fig)
        drawdown_negative_metrics(df)

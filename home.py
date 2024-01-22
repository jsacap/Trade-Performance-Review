import streamlit as st
import plotly.express as px
import pandas as pd
from data_processing import clean_data, line_chart, drawdown_negative, daily_df, grouped_assets_chart, grouped_assets_df
from metrics import totals_metrics, drawdown_negative_metrics, real_drawdown_metrics


st.set_page_config(layout='wide')
st.title('Trading Edge Auditor')
st.write('Upload and analyze your trade data.')

file_upload = st.file_uploader("Upload your trade data", type=["html", "htm"])

if file_upload:
    df = clean_data(file_upload)
    # Globals
    lowest_pnl, date_lowest_pnl_str, drawdown_fig, _ = drawdown_negative(df)
    daily_pnl_df = daily_df(df)
    grouped_df = grouped_assets_df(df)
    assets_chart = grouped_assets_chart(grouped_df)

    if not df.empty:
        st.dataframe(df)
        totals_metrics(df)
        line_chart(df)

        st.header('Drawdown')
        st.subheader('Days below starting balance')
        drawdown_negative_metrics(df)
        st.plotly_chart(drawdown_fig)

        st.subheader('Drawdowns (after reaching new equity highs)')
        real_drawdown_metrics(daily_pnl_df)

        st.plotly_chart(assets_chart)

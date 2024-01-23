import streamlit as st
import plotly.express as px
import pandas as pd
import time
from data_processing import clean_data, line_chart, drawdown_negative, daily_df, grouped_assets_chart, grouped_assets_df, positive_assets_pie, predict_and_plot_rolling_pnl, process_data
from metrics import totals_metrics, drawdown_negative_metrics, real_drawdown_metrics, top_pnl_day_metrics, trade_times_metrics, predict_and_plot_metrics


st.set_page_config(page_title='Trading Performance Review', layout='wide')


st.title('Trading Edge Auditor')
st.write('Upload and analyze your trade data.')
blog_url = "https://sanchojralegre.com/blog/article/77"
st.write(f"Visit the blog article [here]({blog_url}).")
file_upload = st.file_uploader("Upload your trade data", type=["html", "htm"])

if file_upload:
    progress_bar = st.progress(0)
    status_text = st.empty()
    process_data(progress_bar, status_text)
    st.snow()

    df = clean_data(file_upload)
    # Globals
    lowest_pnl, date_lowest_pnl_str, drawdown_fig, _ = drawdown_negative(df)
    daily_pnl_df = daily_df(df)
    grouped_df = grouped_assets_df(df)
    assets_chart = grouped_assets_chart(grouped_df)
    predict_fig, _, _ = predict_and_plot_rolling_pnl(df)

    if not df.empty:
        st.dataframe(df)
        totals_metrics(df)
        line_chart(df)

        st.header('HIGHLIGHTS')
        top_pnl_day_metrics(df)
        col1, col2, col3 = st.columns(3)
        with col2:
            positive_assets_pie(df)
        trade_times_metrics(df)
        predict_and_plot_metrics(df)
        st.plotly_chart(predict_fig, use_container_width=True)

        st.header('Drawdown')
        st.subheader('Days below starting balance')
        drawdown_negative_metrics(df)
        st.plotly_chart(drawdown_fig, use_container_width=True)

        st.subheader('Drawdowns (after reaching new equity highs)')
        real_drawdown_metrics(daily_pnl_df)

        st.plotly_chart(assets_chart, use_container_width=True)

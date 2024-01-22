from data_processing import totals, drawdown_negative, find_recovery_date, duration_to_recovery
import streamlit as st


def totals_metrics(df):
    total_loss, total_profit, net_pnl = totals(df)
    format_loss = f'-${-total_loss:.2f}'
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric('Total Profit', f'${total_profit}')
    with col2:
        st.metric('Total Loss', format_loss)
    with col3:
        st.metric('Net PnL', f'${net_pnl}')


def drawdown_negative_metrics(df):
    lowest_pnl, date_lowest_pnl_str, _, index_of_Lowest_pnl = drawdown_negative(
        df)
    recovery_date = find_recovery_date(
        df, index_of_lowest_pnl=index_of_Lowest_pnl)
    recovery_date_str = recovery_date.strftime("%d %B %Y")
    duration = duration_to_recovery(df)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric('Lowest Pnl', f'-${-lowest_pnl}')

    with col2:
        st.metric('Lowest PnL date', date_lowest_pnl_str)
    with col3:
        st.metric('Recovery Date', recovery_date_str)
    with col4:
        st.metric('Recovery Duration from lowest PnL', f'{duration} DAYS')

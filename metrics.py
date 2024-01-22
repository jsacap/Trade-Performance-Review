from data_processing import totals, drawdown_negative, find_recovery_date, duration_to_recovery, calculate_real_drawdown, average_drawdown_duration, calculate_largest_drawdown, top_pnl_day, get_top_asset, grouped_assets_df, daily_df
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


def real_drawdown_metrics(df):
    largest_drawdown, drawdown_start_date, drawdown_end_date, drawdown_duration = calculate_largest_drawdown(
        df)
    average_duration = average_drawdown_duration(df)
    drawdown_start_date_str = drawdown_start_date.strftime(
        "%Y-%m-%d") if drawdown_start_date else 'N/A'
    drawdown_end_date_str = drawdown_end_date.strftime(
        "%Y-%m-%d") if drawdown_end_date else 'N/A'

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric('Largest Drawdown after reaching',
                  f'${largest_drawdown:.2f}')
    with col2:
        st.metric('Date of the largest drawdown', drawdown_start_date_str)
    with col3:
        st.metric('Recovered on: ', drawdown_end_date_str)
    with col4:
        st.metric('No. of days to recover the largest drawdown',
                  drawdown_duration)
    with col5:
        st.metric('Average Duration for all Drawdowns',
                  f'{average_duration} Days')


def top_pnl_day_metrics(df):
    daily_pnl_df = daily_df(df)
    grouped_df = grouped_assets_df(df)
    top_asset, top_asset_pnl = get_top_asset(grouped_df)
    strongest_pnl_date_str, strongest_pnl = top_pnl_day(daily_pnl_df)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric('Top Asset', top_asset)
    with col2:
        st.metric('Top Asset PnL', f'${top_asset_pnl}')
    with col3:
        st.metric('Highest return in 1-Day', f'${strongest_pnl}')
    with col4:
        st.metric('Date of highest return', strongest_pnl_date_str)

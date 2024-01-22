import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime


def clean_data(file):
    try:
        trades = pd.read_html(file)
        df = trades[0]

        header_row_index = 2
        df.columns = df.iloc[header_row_index]
        df = df[header_row_index + 1:]

        df.drop(['Ticket', 'Taxes'], axis=1, inplace=True)

        df.columns = ['Open Date', 'Type', 'Size', 'Asset', 'Open Price', 'Stop Loss',
                      'Take Profit', 'Close Date', 'Close Price', 'Commissions', 'Swap', 'PnL']

        valid_trade_types = ['buy', 'sell', 'buy limit',
                             'sell limit', 'buy stop', 'sell stop']
        df = df[df['Type'].str.lower().isin(valid_trade_types)]
        df = df[df['PnL'].str.lower() != 'cancelled']

        cols_to_float = ['Size', 'Open Price', 'Stop Loss', 'Take Profit', 'Close Price',
                         'Commissions', 'Swap', 'PnL']
        for col in cols_to_float:
            df[col] = df[col].astype(str).str.replace(' ', '').astype(float)

        df['Open Date'] = pd.to_datetime(
            df['Open Date'], format='%Y.%m.%d %H:%M:%S')
        df['Close Date'] = pd.to_datetime(
            df['Close Date'], format='%Y.%m.%d %H:%M:%S')

        df = df.sort_values(by='Close Date', ascending=True).reset_index()
        df['Rolling PnL'] = df['PnL'].cumsum()

        return df

    except Exception as e:
        st.error(f"An error occurred: {e}")
        return pd.DataFrame()


def line_chart(df):
    fig = px.line(df, x=df.index, y='Rolling PnL',
                  title='Rolling PnL Over Time')
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='$ PnL'
    )
    st.plotly_chart(fig)


def totals(df):
    total_profit = df[df['PnL'] > 0]['PnL'].sum().round(2)
    total_loss = df[df['PnL'] < 0]['PnL'].sum().round(2)
    net_pnl = df['PnL'].sum().round(2)
    return total_loss, total_profit, net_pnl


def daily_df(df):
    df['Close Date'] = pd.to_datetime(df['Close Date']).dt.date
    daily_pnl_df = df.groupby('Close Date')['PnL'].sum().reset_index()
    daily_pnl_df['Rolling PnL'] = daily_pnl_df['PnL'].cumsum()
    return daily_pnl_df


def find_recovery_date(df, index_of_lowest_pnl):
    index_of_lowest_pnl = df['Rolling PnL'].idxmin()
    recovery_df = df.iloc[index_of_lowest_pnl + 1:]

    for index, row in recovery_df.iterrows():
        if row['Rolling PnL'] > 0:
            return row['Close Date']

    return None


def drawdown_negative(df):
    daily_pnl_df = daily_df(df)
    lowest_pnl = df['Rolling PnL'].min().round(2)
    index_of_lowest_pnl = df['Rolling PnL'].idxmin()
    date_lowest_pnl = df.loc[index_of_lowest_pnl, 'Close Date']
    date_lowest_pnl_str = date_lowest_pnl.strftime("%d %B %Y")
    negative_days_df = daily_pnl_df[daily_pnl_df['Rolling PnL'] < 0]
    drawdown_fig = px.area(negative_days_df, x='Close Date', y='Rolling PnL')
    drawdown_fig.update_traces(
        line=dict(color="red"), fillcolor='rgba(255,0,0,0.5)')

    return lowest_pnl, date_lowest_pnl_str, drawdown_fig, index_of_lowest_pnl


def duration_to_recovery(df):
    lowest_pnl, date_lowest_pnl_str, _, index_of_lowest_pnl = drawdown_negative(
        df)
    recovery_date = find_recovery_date(df, index_of_lowest_pnl)

    if recovery_date is not None:
        date_lowest_pnl = datetime.strptime(date_lowest_pnl_str, "%d %B %Y")
        recovery_date = datetime.strptime(
            recovery_date.strftime("%d %B %Y"), "%d %B %Y")

        duration = recovery_date - date_lowest_pnl
        return duration.days

    return None


def calculate_real_drawdown(daily_pnl_df):
    new_highs = []
    drawdowns = []
    drawdown_dates = []
    drawdown_durations = []
    current_high = daily_pnl_df['Rolling PnL'].iloc[0]
    lowest_rolling = current_high
    date_of_lowest_rolling = daily_pnl_df['Close Date'].iloc[0]

    for index, row in daily_pnl_df.iterrows():
        if row['Rolling PnL'] > current_high:
            current_high = row['Rolling PnL']
            new_highs.append((row['Close Date'], current_high))

            drawdown_amount = current_high - lowest_rolling
            drawdowns.append(drawdown_amount)

            start_date = date_of_lowest_rolling
            end_date = row['Close Date']
            drawdown_dates.append((start_date, end_date))

            duration = (end_date - start_date).days
            drawdown_durations.append(duration)

            lowest_rolling = current_high
            date_of_lowest_rolling = row['Close Date']
        else:
            if row['Rolling PnL'] < lowest_rolling:
                lowest_rolling = row['Rolling PnL']
                date_of_lowest_rolling = row['Close Date']

    return new_highs, drawdowns, drawdown_dates, drawdown_durations


def calculate_largest_drawdown(daily_pnl_df):
    _, drawdowns, drawdown_dates, _ = calculate_real_drawdown(daily_pnl_df)

    if drawdowns:
        largest_drawdown = max(drawdowns)
        largest_drawdown_index = drawdowns.index(largest_drawdown)
        start_date, end_date = drawdown_dates[largest_drawdown_index]

        duration = (end_date - start_date).days
        return largest_drawdown, start_date, end_date, duration
    else:
        return None, None, None, None


def average_drawdown_duration(daily_pnl_df):
    _, _, _, drawdown_durations = calculate_real_drawdown(daily_pnl_df)

    if drawdown_durations:
        average_duration = sum(drawdown_durations) / len(drawdown_durations)
        return average_duration
    else:
        return None


def grouped_assets_df(df):
    return df.groupby('Asset')['PnL'].sum().sort_values(ascending=False)


def grouped_assets_chart(grouped_assets_pnl):
    fig = px.bar(grouped_assets_pnl, x=grouped_assets_pnl.index, y='PnL')
    return fig

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LinearRegression


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
    return df.groupby('Asset')['PnL'].sum().sort_values(ascending=False).reset_index()


def grouped_assets_chart(grouped_assets_pnl):
    fig = px.bar(grouped_assets_pnl, x='Asset', y='PnL')
    return fig


def get_top_asset(grouped_assets_df):
    top_asset = grouped_assets_df.iloc[0]['Asset'].upper()
    top_asset_pnl = grouped_assets_df.iloc[0]['PnL']
    return top_asset, top_asset_pnl


def top_pnl_day(daily_pnl_df):
    strongest_pnl_df = daily_pnl_df.sort_values(by='PnL', ascending=False)
    strongest_pnl_date = strongest_pnl_df.iloc[0]['Close Date']
    strongest_pnl_date_str = strongest_pnl_date.strftime("%d %B %Y")
    strongest_pnl = strongest_pnl_df.iloc[0]['PnL']

    return strongest_pnl_date_str, strongest_pnl


def positive_assets(df):
    positive_assets_df = df[df['PnL'] > 0].groupby(
        'Asset')['PnL'].sum().sort_values(ascending=False).reset_index()
    positive_assets_df['Asset'] = positive_assets_df['Asset'].str.upper()
    return positive_assets_df


def positive_assets_pie(df):
    positive_assets_df = positive_assets(df)
    fig = px.pie(positive_assets_df, names='Asset', values='PnL',
                 color='Asset', color_discrete_sequence=px.colors.sequential.Blues_r)
    st.plotly_chart(fig)


def timedelta_to_hours_minutes(td):
    total_seconds = td.total_seconds()
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    return f'{hours} hours and {minutes} minutes'


def trade_times(df):
    df['Open Date'] = pd.to_datetime(df['Open Date'])
    df['Close Date'] = pd.to_datetime(df['Close Date'])
    negative_df = df[df['PnL'] < 0]
    positive_df = df[df['PnL'] > 0]
    time_differences_negative = negative_df['Close Date'] - \
        negative_df['Open Date']
    time_differences_positive = positive_df['Close Date'] - \
        positive_df['Open Date']
    average_time_positive = time_differences_positive.mean()
    average_time_negative = time_differences_negative.mean()

    positive_time_str = timedelta_to_hours_minutes(average_time_positive)
    negative_time_str = timedelta_to_hours_minutes(average_time_negative)
    max_time_negative = time_differences_negative.max()
    max_time_negative_id = time_differences_negative.idxmax()
    convert_max_negative = timedelta_to_hours_minutes(max_time_negative)
    max_time_positive = time_differences_positive.max()
    max_time_positive_id = time_differences_positive.idxmax()
    convert_max_positive = timedelta_to_hours_minutes(max_time_positive)

    return positive_time_str, negative_time_str, convert_max_negative, convert_max_positive


def predict_and_plot_rolling_pnl(df, num_days_to_predict=30, degree=3):
    df['DateNumeric'] = pd.to_datetime(
        df['Close Date']).map(datetime.toordinal)

    X = df[['DateNumeric']]
    y = df['Rolling PnL']

    polyreg = make_pipeline(PolynomialFeatures(degree), LinearRegression())
    polyreg.fit(X, y)

    # Start predictions from the first date in the dataset
    start_date_for_prediction = pd.to_datetime(df['Close Date']).min()
    last_date = pd.to_datetime(df['Close Date']).max()
    end_date_for_prediction = last_date + timedelta(days=num_days_to_predict)
    prediction_dates = pd.date_range(
        start=start_date_for_prediction, end=end_date_for_prediction, freq='D')
    prediction_dates_numeric = [datetime.toordinal(
        date) for date in prediction_dates]

    # Make predictions for this range
    predictions = polyreg.predict(
        np.array(prediction_dates_numeric).reshape(-1, 1))

    # Create a DataFrame for the predictions
    predictions_df = pd.DataFrame(
        {'Date': prediction_dates, 'Predicted Rolling PnL': predictions})

    # Plotting the original and predicted data
    fig = px.line(df, x='Close Date', y='Rolling PnL', labels={
                  'Rolling PnL': 'Original Rolling PnL'}, title='Rolling PnL and Predictions')
    fig.add_scatter(x=predictions_df['Date'], y=predictions_df['Predicted Rolling PnL'],
                    mode='lines', name='Predicted Rolling PnL', line=dict(color='orange'))

    # Get the last prediction date and value for future use
    last_prediction_date = end_date_for_prediction
    last_prediction_value = predictions[-1].round(2)

    return fig, last_prediction_date, last_prediction_value

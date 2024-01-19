import streamlit as st
import pandas as pd


def clean_data(file):
    try:
        trades = pd.read_html(file)
        df = trades[0]

        header_row_index = 2
        df.columns = df.iloc[header_row_index]
        df = df[header_row_index + 1:]

        df.drop(['Ticket', 'Taxes'], axis=1, inplace=True)

        df.columns = ['Open Time', 'Type', 'Size', 'Asset', 'Open Price', 'Stop Loss',
                      'Take Profit', 'Close Time', 'Close Price', 'Commissions', 'Swap', 'PnL']

        valid_trade_types = ['buy', 'sell', 'buy limit',
                             'sell limit', 'buy stop', 'sell stop']
        df = df[df['Type'].str.lower().isin(valid_trade_types)]
        df = df[df['PnL'].str.lower() != 'cancelled']

        cols_to_float = ['Size', 'Open Price', 'Stop Loss', 'Take Profit', 'Close Price',
                         'Commissions', 'Swap', 'PnL']
        for col in cols_to_float:
            df[col] = df[col].astype(str).str.replace(' ', '').astype(float)

        return df

    except Exception as e:
        st.error(f"An error occurred: {e}")
        return pd.DataFrame()

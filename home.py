import streamlit as st
import pandas as pd

st.title('Trading Edge Auditor')
st.write('Upload and analyze your trade data.')

file_upload = st.file_uploader("Upload your trade data", type=["html", "htm"])
df = pd.DataFrame()

if file_upload:
    try:
        trades = pd.read_html(file_upload)
        df = trades[0]

        # Assuming the third row contains the column headers
        header_row_index = 2
        df.columns = df.iloc[header_row_index]
        df = df[header_row_index + 1:]

        # Drop 'Ticket' and 'Taxes' columns
        df.drop(['Ticket', 'Taxes'], axis=1, inplace=True)

        # Rename columns
        df.columns = ['Open Time', 'Type', 'Size', 'Asset', 'Open Price', 'Stop Loss',
                      'Take Profit', 'Close Time', 'Close Price', 'Commissions', 'Swap', 'PnL']

        # Filter out non-trade rows
        valid_trade_types = ['buy', 'sell', 'buy limit',
                             'sell limit', 'buy stop', 'sell stop']
        df = df[df['Type'].str.lower().isin(valid_trade_types)]

        # Remove rows with 'cancelled' in the 'PnL' column
        df = df[df['PnL'].str.lower() != 'cancelled']

        # Convert columns to float, handling non-numeric formats
        cols_to_float = ['Size', 'Open Price', 'Stop Loss', 'Take Profit', 'Close Price',
                         'Commissions', 'Swap', 'PnL']
        for col in cols_to_float:
            df[col] = df[col].astype(str).str.replace(' ', '').astype(float)

        st.dataframe(df)

    except Exception as e:
        st.error(f"An error occurred: {e}")

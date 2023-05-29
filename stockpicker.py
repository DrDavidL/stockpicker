import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from ta.momentum import RSIIndicator
from ta.trend import MACD

st.title('Check your Stock Picks!')
st.sidebar.info('Check your Stock Picks! This app uses data from Yahoo Finance to display stock prices and buy/sell signals based on published technical analysis methods. *This is NOT investment advice!!!* Only invest what you can afford to lose. As we know... the market is crazy and prices are not predictable.')

# User input
ticker_symbols = st.sidebar.text_input("Enter stock symbols (comma separated, e.g. GOOGL,MSFT):", 'GOOGL,MSFT')
# start_date = st.date_input("Start date:", pd.to_datetime('2020-01-01'))
start_date = st.sidebar.date_input("Start date - default is 2 years ago:", pd.to_datetime('today') - pd.DateOffset(years=2))

end_date = st.sidebar.date_input("End date - default is today:", pd.to_datetime('today'))

st.info("""Green dots are buy signals; red dots are sell signals using typical statistical methods
        (e.g. moving average crossover, RSI). Of course, this is not financial advice! Prices are not predictable and the market 
        is not rational. Only invest what you can afford to lose.""")
signal_type = st.sidebar.radio("Select your buy/sell signal type:", ['Moving Average Crossover', 'Relative Strength Index (RSI)', 'Moving Average Convergence Divergence (MACD)'])

# User input for moving averages
st.sidebar.write("""Include optional moving averages for charts:""")
show_50_ma = st.sidebar.checkbox('Show 50 day moving average')
show_200_ma = st.sidebar.checkbox('Show 200 day moving average')

# Display QR code
st.sidebar.write("""If you found this app useful, please consider donating to the developer:""")
st.sidebar.image("bmc/bmc_qr.png", width=100)

# Fetch data and plot for each stock
for ticker_symbol in ticker_symbols.split(','):
    ticker_symbol = ticker_symbol.strip().upper()  # Clean up the ticker symbol
    ticker_data = yf.Ticker(ticker_symbol)
    ticker_df = ticker_data.history(period='1d', start=start_date, end=end_date)

    # Display data
    st.write(f"Displaying data for {ticker_symbol}")

    if signal_type == 'Moving Average Crossover':
        # Calculate moving averages
        ma_50 = ticker_df.Close.rolling(50).mean()
        ma_200 = ticker_df.Close.rolling(200).mean()

        # Calculate and display "buy" and "sell" signals based on moving average crossover
        buy_signals = (ma_50 > ma_200) & (ma_50.shift() < ma_200.shift())  # Bullish crossover
        sell_signals = (ma_50 < ma_200) & (ma_50.shift() > ma_200.shift())  # Bearish crossover
    elif signal_type == 'Relative Strength Index (RSI)':
        # Calculate RSI
        rsi = RSIIndicator(ticker_df.Close).rsi()
        # buy_rsi = st.slider("RSI buy level - typically < 30", min_value=0, max_value=100, value=30, step=1)
        buy_rsi = st.slider(f"RSI buy level for {ticker_symbol} - typically < 30", min_value=0, max_value=100, value=25, step=1, key=f"buy_rsi_{ticker_symbol}")

        # sell_rsi = st.slider("RSI sell level - typically > 70", min_value=0, max_value=100, value=80, step=1)
        sell_rsi = st.slider(f"RSI sell level for {ticker_symbol} - typically > 70", min_value=0, max_value=100, value=80, step=1, key=f"sell_rsi_{ticker_symbol}")


        # Calculate and display "buy" and "sell" signals based on RSI
        buy_signals = rsi < buy_rsi  # RSI below 30 is considered oversold
        sell_signals = rsi > sell_rsi  # RSI above 70 is considered overbought, here using 90 to be more conservative
    elif signal_type == 'Moving Average Convergence Divergence (MACD)':
        # Calculate MACD
        macd = MACD(ticker_df.Close).macd()

        # Calculate and display "buy" and "sell" signals based on MACD
        buy_signals = (macd > 0) & (macd.shift() < 0)  # Bullish crossover
        sell_signals = (macd < 0) & (macd.shift() > 0)  # Bearish crossover

    # Create a new DataFrame for plotting
    plot_df = pd.DataFrame({'Close': ticker_df.Close, 'Buy Signal': np.nan, 'Sell Signal': np.nan})
    plot_df.loc[buy_signals, 'Buy Signal'] = ticker_df.loc[buy_signals, 'Close']  # Only show buy signals where they are true
    plot_df.loc[sell_signals, 'Sell Signal'] = ticker_df.loc[sell_signals, 'Close']  # Only show sell signals where they are true

    # Create a Matplotlib figure
    fig, ax = plt.subplots()
    ax.plot(plot_df.index, plot_df['Close'], label='Close')
    # Plot moving averages if selected by user
    if show_50_ma:
        ma_50 = ticker_df.Close.rolling(50).mean()
        ax.plot(plot_df.index, ma_50, label='50 day MA', color='orange')
    if show_200_ma:
        ma_200 = ticker_df.Close.rolling(200).mean()
        ax.plot(plot_df.index, ma_200, label='200 day MA', color='purple')
    ax.scatter(plot_df.index, plot_df['Buy Signal'], color='green', s=100)  # Plot buy signals as larger green dots
    ax.scatter(plot_df.index, plot_df['Sell Signal'], color='red', s=100)  # Plot sell signals as larger red dots
    ax.legend()
    
    # Add title with stock ticker
    ax.set_title(f'Stock Price for {ticker_symbol}')
    
    # Add gridlines
    ax.grid(True, linestyle='--', alpha=0.6)

    # Rotate x-axis labels
    plt.xticks(rotation=45)

    # Display the Matplotlib figure in Streamlit
    st.pyplot(fig)

    # Display volume
    st.write(f"Volume for {ticker_symbol}")
    st.bar_chart(ticker_df.Volume)

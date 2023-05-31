import streamlit as st
import yfinance as yf
import pandas_ta as ta
import re


# Define a function to calculate RSI
def calculate_rsi(data, time_period):
    return ta.rsi(data['Close'], length=time_period)


# Define a function to interpret the RSI
# def buy_or_not_rsi(rsi, buy_level):
#     if rsi.iloc[-1] < buy_level:  # RSI indicates oversold condition
#         return "BUY"
#     else:
#         return "DON'T BUY"
    
    
def buy_or_not_rsi(symbol, data, length, buy_level):
    rsi = ta.rsi(data['Close'], length=length)
    if rsi[-1] < buy_level:
        return {"Signal": "BUY", "Date": data.index[-1].date(), "Closing Price": data['Close'][-1], "Symbol": symbol}
    else:
        return {"Signal": "DON'T BUY", "Date": data.index[-1].date(), "Closing Price": data['Close'][-1], "Symbol": symbol}



def calculate_rsi_orig(data, window):
    return ta.rsi(data['Close'], length=window)

def calculate_sma(data, window):
    return ta.sma(data['Close'], length=window)

def calculate_macd(data, short_window, long_window):
    macd = ta.macd(data['Close'], fast=short_window, slow=long_window)
    return macd

def buy_or_not_macd(macd, symbol, data, fast, slow):
    if macd[f'MACD_{fast}_{slow}_9'][-1] > macd[f'MACDs_{fast}_{slow}_9'][-1] and macd[f'MACD_{fast}_{slow}_9'][-2] < macd[f'MACDs_{fast}_{slow}_9'][-2]:
        return {"Signal": "BUY", "Date": data.index[-1].date(), "Closing Price": data['Close'][-1], "Symbol": symbol}
    else:
        return {"Signal": "DON'T BUY", "Date": data.index[-1].date(), "Closing Price": data['Close'][-1], "Symbol": symbol}

    
def buy_or_not_rsi_sma(rsi, sma, symbol, data, length):
    if rsi[-1] > sma['sma'+str(length)][-1] and rsi[-2] < sma['sma'+str(length)][-2]:
        return {"Signal": "BUY", "Date": data.index[-1].date(), "Closing Price": data['Close'][-1], "Symbol": symbol}
    else:
        return {"Signal": "DON'T BUY", "Date": data.index[-1].date(), "Closing Price": data['Close'][-1], "Symbol": symbol}





st.title('Stock Technical Analysis App')

user_input = st.text_input("Enter one or more stock symbols (separated by comma or space):", 'AAPL')

symbols = re.split(',| ', user_input)

analysis_method = st.radio("Select the technical analysis method:", ("MACD", "RSI"))

if analysis_method == "RSI":
    rsi_buy_level = st.slider("RSI buy level typically < 30", min_value=0, max_value=100, value=25, step=1)

st.header('Technical Analysis Results')

buys_1mo = []
buys_3mo = []
buys_6mo = []
sells_1mo = []

for symbol in symbols:
    symbol = symbol.strip().upper()

    if not symbol:  # skip if symbol is empty
        continue

    data = yf.download(symbol, period='6mo')
    
    if data.empty:
        st.write(f"No data available for {symbol}. Please check the symbol.")
        continue

    # if analysis_method == "RSI and SMA":
    #     rsi_1mo = ta.rsi(data['Close'], length=10)
    #     sma_1mo = ta.sma(rsi_1mo, length=10)
    #     sma_1mo.rename(columns={'close': 'sma10'}, inplace=True)
        
    #     rsi_3mo = ta.rsi(data['Close'], length=14)
    #     sma_3mo = ta.sma(rsi_3mo, length=14)
    #     sma_3mo.rename(columns={'close': 'sma14'}, inplace=True)
        
    #     rsi_6mo = ta.rsi(data['Close'], length=24)
    #     sma_6mo = ta.sma(rsi_6mo, length=24)
    #     sma_6mo.rename(columns={'close': 'sma24'}, inplace=True)

    #     signal_1mo = buy_or_not_rsi_sma(rsi_1mo, sma_1mo, symbol, data, 10)
    #     if signal_1mo["Signal"] == "BUY":
    #         buys_1mo.append(signal_1mo)

    #     signal_3mo = buy_or_not_rsi_sma(rsi_3mo, sma_3mo, symbol, data, 14)
    #     if signal_3mo["Signal"] == "BUY":
    #         buys_3mo.append(signal_3mo)

    #     signal_6mo = buy_or_not_rsi_sma(rsi_6mo, sma_6mo, symbol, data, 24)
    #     if signal_6mo["Signal"] == "BUY":
    #         buys_6mo.append(signal_6mo)




 
    if analysis_method == "MACD":
        macd_1mo = ta.macd(data['Close'], fast=8, slow=17)
        macd_3mo = ta.macd(data['Close'], fast=12, slow=26)
        macd_6mo = ta.macd(data['Close'], fast=26, slow=54)

        signal_1mo = buy_or_not_macd(macd_1mo, symbol, data, 8, 17)
        if signal_1mo["Signal"] == "BUY":
            buys_1mo.append(signal_1mo)
        elif signal_1mo["Signal"] == "DON'T BUY" and macd_1mo[f"MACD_8_17_9"][-1] < macd_1mo[f"MACDs_8_17_9"][-1]:  # Sell condition
            sells_1mo.append(signal_1mo)

        signal_3mo = buy_or_not_macd(macd_3mo, symbol, data, 12, 26)
        if signal_3mo["Signal"] == "BUY":
            buys_3mo.append(signal_3mo)

        signal_6mo = buy_or_not_macd(macd_6mo, symbol, data, 26, 54)
        if signal_6mo["Signal"] == "BUY":
            buys_6mo.append(signal_6mo)

    

    if analysis_method == "RSI": 
        rsi_1mo = ta.rsi(data['Close'], length=10)       
        
        signal_1mo = buy_or_not_rsi(symbol, data, 10, rsi_buy_level)
        if signal_1mo["Signal"] == "BUY":
            buys_1mo.append(signal_1mo)
        elif signal_1mo["Signal"] == "DON'T BUY" and rsi_1mo[-1] > 80:  # Sell condition
            sells_1mo.append(signal_1mo)

        signal_3mo = buy_or_not_rsi(symbol, data, 14, rsi_buy_level)
        if signal_3mo["Signal"] == "BUY":
            buys_3mo.append(signal_3mo)

        signal_6mo = buy_or_not_rsi(symbol, data, 24, rsi_buy_level)
        if signal_6mo["Signal"] == "BUY":
            buys_6mo.append(signal_6mo)
            
st.subheader("1-Month Sell Indicators:")
st.write(sells_1mo)

# Find symbols in both 1-month and 3-month categories
symbols_in_both = [symbol_info["Symbol"] for symbol_info in buys_1mo if symbol_info["Symbol"] in buys_3mo]

# Display symbols that appear in both categories
if symbols_in_both:
    st.subheader("Symbols Appearing in Both 1-Month and 3-Month Categories")
    st.write(", ".join(symbols_in_both))
else:
    st.subheader("No Symbols Found in Both 1-Month and 3-Month Categories")


st.subheader("1, 3, and 6 Month Buy Indicators:")
       
st.write("1 Month Horizon:", buys_1mo)
st.write("3 Month Horizon:", buys_3mo)
st.write("6 Month Horizon:", buys_6mo)


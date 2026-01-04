import streamlit as st
import yfinance as yf
import pandas as pd

st.title("即時股價查詢工具")

# 輸入框：讓使用者輸入股票代號
# 注意：台股需加 .TW (如 2330.TW)，美股直接輸入 (如 AAPL)
target_stock = st.text_input("輸入股票代號查詢 (例如: 2330.TW 或 TSLA)", "2330.TW")

if target_stock:
    try:
        # 使用 yfinance 抓取即時資訊
        stock_data = yf.Ticker(target_stock)
        
        # 獲取最新的一筆價格 (通常是今天或最後一個交易日)
        # period="1d" 代表抓取最近一天的資料
        df = stock_data.history(period="1d")
        
        if not df.empty:
            current_price = df['Close'].iloc[-1]
            prev_close = stock_data.info.get('previousClose', current_price)
            change = current_price - prev_close
            change_percent = (change / prev_close) * 100

            # 使用 Streamlit 的 metric 組件美化顯示
            col1, col2 = st.columns(2)
            col1.metric(label=f"{target_stock} 目前股價", value=f"{current_price:.2f}")
            col2.metric(label="今日漲跌", value=f"{change:.2f}", delta=f"{change_percent:.2f}%")
            
            # 顯示簡易的公司名稱
            st.write(f"公司簡稱: {stock_data.info.get('shortName', 'N/A')}")
        else:
            st.error("找不到該股票資料，請檢查代號是否正確。")
            
    except Exception as e:
        st.error(f"抓取資料時發生錯誤: {e}")

# --- 下方可保留你之前的交易紀錄表單 ---
st.divider()
st.subheader("新增交易紀錄")
# ... (之前的表單代碼)

import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# 設定標題
st.set_page_config(page_title="雲端股票投資工具", page_icon="📈")
st.title("📈 雲端股票投資工具")

# 建立資料庫連線
conn = st.connection("postgresql", type="sql")

# --- 第一部分：新增交易紀錄 ---
st.header("📝 新增買賣紀錄")
with st.form("trade_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        t_date = st.date_input("交易日期", datetime.now())
        t_symbol = st.text_input("股票代號 (例: 2330.TW)")
        t_type = st.selectbox("交易類型", ["買進", "賣出"])
    with col2:
        t_price = st.number_input("交易單價", min_value=0.0)
        t_qty = st.number_input("股數", min_value=1)
        t_fee = st.number_input("手續費/稅金", min_value=0)

    submitted = st.form_submit_button("儲存至雲端資料庫")
    
    if submitted:
        if t_symbol:
            query = f"""
                INSERT INTO transactions (trade_date, stock_symbol, trade_type, price, quantity, fee)
                VALUES ('{t_date}', '{t_symbol.upper()}', '{t_type}', {t_price}, {t_qty}, {t_fee})
            """
            with conn.session as s:
                s.execute(query)
                s.commit()
            st.success(f"成功存入 {t_symbol}")
            st.cache_data.clear() # 清除緩存以顯示新資料
        else:
            st.error("請輸入股票代號")

st.divider()

# --- 第二部分：顯示歷史紀錄與損益 ---
st.header("📊 持股與損益概況")

# 從資料庫讀取紀錄
df_records = conn.query("SELECT * FROM transactions ORDER BY trade_date DESC", ttl="0")

if not df_records.empty:
    st.subheader("最近交易明細")
    st.dataframe(df_records, use_container_width=True)

    # 簡易庫存計算邏輯 (此處為示範，複雜損益需更深層計算)
    summary = df_records.copy()
    # 買進為正，賣出為負
    summary['adj_qty'] = summary.apply(lambda x: x['quantity'] if x['trade_type'] == '買進' else -x['quantity'], axis=1)
    
    inventory = summary.groupby('stock_symbol')['adj_qty'].sum()
    inventory = inventory[inventory > 0] # 只看還有持股的

    if not inventory.empty:
        st.subheader("目前持股現值")
        for symbol, qty in inventory.items():
            # 抓取即時價格
            try:
                curr_p = yf.Ticker(symbol).history(period="1d")['Close'].iloc[-1]
                st.write(f"🔹 **{symbol}**: {qty} 股 | 目前股價: {curr_p:.2f} | 總市值: {qty*curr_p:,.0f}")
            except:
                st.write(f"🔹 **{symbol}**: {qty} 股 (無法抓取即時價格)")
else:
    st.info("目前尚無交易紀錄，請從上方表單新增。")

import yfinance as yf
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

# 1. 妳指定的關注清單
stock_list = [
    '2330.TW', '0050.TW', '00919.TW', 
    '2884.TW', '2892.TW', '2801.TW', 
    '5904.TW', '1701.TW'
]

print("正在抓取最新股市資料...")

# 2. 抓取資料並計算季線
data_results = []
for ticker in stock_list:
    stock = yf.Ticker(ticker)
    df = stock.history(period="3mo")
    
    if not df.empty:
        latest_close = df['Close'].iloc[-1]
        ma60 = df['Close'].rolling(window=60).mean().iloc[-1]
        
        data_results.append({
            '股票代號': ticker,
            '最新收盤價': round(latest_close, 2),
            '60日均線(MA60)': round(ma60, 2) if pd.notna(ma60) else 0,
            '狀態': '股價大於MA60' if latest_close > ma60 else '股價小於MA60'
        })

df_result = pd.DataFrame(data_results)

# 3. 轉成乾淨的 HTML 表格
if not df_result.empty:
    df_result['最新收盤價'] = df_result['最新收盤價'].map('{:.2f}'.format)
    df_result['60日均線(MA60)'] = df_result['60日均線(MA60)'].map('{:.2f}'.format)
    
    # 轉為 HTML 表格語法
    table_html = df_result.to_html(index=False, border=1, justify='center')
    html_content = f"<h3>📊 每日股市智慧篩選報告</h3>{table_html}"
else:
    html_content = "<h3>今日無資料</h3>"

# 4. 寄送信件設定
sender_email = os.environ.get('GMAIL_USER')
app_password = os.environ.get('GMAIL_PASS')
receiver_email = sender_email

msg = MIMEMultipart()
msg['From'] = sender_email
msg['To'] = receiver_email
msg['Subject'] = "📊 每日股市智慧篩選報告"
msg.attach(MIMEText(html_content, 'html', 'utf-8'))

# 5. 執行自動寄信
try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, app_password)
    server.send_message(msg)
    server.quit()
    print("信件寄送成功！")
except Exception as e:
    print(f"寄信失敗: {e}")

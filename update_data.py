#!/usr/bin/env python3
"""
生成 SOXX RV21 数据 JSON — 供 GitHub Pages 图表使用
可以用 cron 每天跑一次更新
"""
import sys, os
try:
    sys.path.insert(0, '/Users/kow/.local/lib/python3.9/site-packages')
except: pass
import warnings; warnings.filterwarnings('ignore')

import yfinance as yf
import pandas as pd
import numpy as np
import json

# Download SOXX
soxx = yf.download("SOXX", start="2010-01-01", progress=False)
close = soxx['Close'].squeeze()
if isinstance(close, pd.DataFrame): close = close.iloc[:, 0]

# Calculate indicators
log_ret = np.log(close / close.shift(1))
rv21 = log_ret.rolling(21).std() * np.sqrt(252) * 100
ema10 = close.ewm(span=10).mean()
ema250 = close.ewm(span=250).mean()

df = pd.DataFrame({
    'price': close,
    'rv21': rv21,
    'ema10': ema10,
    'ema250': ema250,
}).dropna()

# Export as JSON
data = []
for date, row in df.iterrows():
    data.append({
        'date': date.strftime('%Y-%m-%d'),
        'price': round(float(row['price']), 2),
        'rv21': round(float(row['rv21']), 2),
        'ema10': round(float(row['ema10']), 2),
        'ema250': round(float(row['ema250']), 2),
    })

import os
output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.json')
with open(output_path, 'w') as f:
    json.dump(data, f)

print(f"Generated {len(data)} data points → {output_path}")
print(f"Latest: {data[-1]['date']} | RV21: {data[-1]['rv21']}% | Price: ${data[-1]['price']}")
print(f"EMA10: {data[-1]['ema10']:.1f} | EMA250: {data[-1]['ema250']:.1f}")
print(f"Signal: {'SOXL' if data[-1]['ema10'] > data[-1]['ema250'] and data[-1]['rv21'] < 45 else 'GLD'}")

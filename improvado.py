import streamlit as st
import pandas as pd
url = 'https://raw.githubusercontent.com/eugenio9445/mkt_test/refs/heads/main/2026-01-21%205_28pm_2026-01-21-1915.csv'
data = pd.read_csv(url,  index_col=0)
print(data)
import pandas as pd
import re
from wordcloud import WordCloud
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
from datetime import timedelta, datetime
import streamlit as st

# Streamlit app structure
st.title("Speech Analysis Tool")
st.text("You can open YouTube video -> more -> Show transcript -> copy it")
# Text input
input_text = st.text_area("Enter your text with timestamps:", height=200)

if input_text:
    pre_lines = input_text.strip().split('\n')
    # Check if the current element is in time format (numbers separated by colons)
    def correct_list(lines):
        i = 0
        while i < len(lines) - 1:
            if not lines[i].replace(':', '').isdigit():
                lines.pop(i)
                continue
            if lines[i + 1].replace(':', '').isdigit():
                lines.pop(i)
                continue
            i += 2
        return lines
    
    lines = correct_list(pre_lines)
    st.write(f"**List:** {lines}")

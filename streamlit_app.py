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
st.title("YouTube Subtitles Analysis Tool")
st.write("")  # Adds a blank line (space)
multi = '''**Objective:** To improve personal English skills by uploading videos to YouTube, transcribing them, and comparing the transcriptions to reference materials.

You can open a YouTube video, go to ***More***, select ***Show transcript***, and then copy it.
'''
st.markdown(multi)
st.write("")  # Adds a blank line (space)
input_text = st.text_area("Enter your text with timestamps:", height=200)
st.write("")  # Adds a blank line (space)
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
    # Initializing lists to hold the data
    time_stamps = []
    texts = []
    word_counts = []
    durations = []
    num_fillers = []
    # List of filler words
    filler_words = ['uh', 'um']
    unique_words = set()  # Set to hold unique words
    num_unique_words = []
    
    # Processing the lines
    for i in range(0, len(lines), 2):
        time_str = lines[i]
        text = lines[i+1]
        # Convert time to datetime object
        if len(time_str.split(':'))==2:
            time_obj = datetime.strptime('00:' + time_str, '%H:%M:%S')
        else:
            time_obj = datetime.strptime(time_str, '%H:%M:%S')
        # Count the number of words
        text = re.sub(r'\[.*?\]', '', text)  # Remove words in square brackets
        word_count = len(text.split())
    
        # Count the number of filler words
        filler_count = sum(text.split().count(filler) for filler in filler_words)
    
        # Add words to the set of unique words
        words_in_text = text.split()
        unique_words.update(words_in_text)
        
        # Append the data to lists
        time_stamps.append(time_obj)
        texts.append(text)
        word_counts.append(word_count)
        num_fillers.append(filler_count)
        num_unique_words.append(len(unique_words))
    
        # Calculate duration between current and previous timestamp
        if i >= len(lines)-2:
            durations.append(0)  # No previous segment for the first one
        else:
            if len(lines[i+2].split(':'))==2:
                next_time_obj = datetime.strptime('00:' + lines[i+2], '%H:%M:%S')
            else:
                next_time_obj = datetime.strptime(lines[i+2], '%H:%M:%S')
            duration = (next_time_obj - time_obj).seconds
            durations.append(duration)
    
    # Creating the DataFrame
    df = pd.DataFrame({
        'time': time_stamps,
        'text': texts,
        'num_words': word_counts,
        'num_fillers': num_fillers,
        'duration': durations,
        'num_unique_words': num_unique_words
    })
    df['duration_clean'] = df.apply(lambda row: row['duration'] if 0 < row['duration'] <= (row['num_words'] + 3) else (row['num_words']*1), axis=1)
    df['cumulative_num_fillers'] = df['num_fillers'].cumsum()
    df['cumulative_num_words'] = df['num_words'].cumsum()
    df['cumulative_duration_clean'] = df['duration_clean'].cumsum()
    df['pace']=df['cumulative_num_words']/df['cumulative_duration_clean'] * 60.0
    df['fillers_share']=df['cumulative_num_fillers']/df['cumulative_num_words']
    df['rolling_avg_pace'] = df['num_words'].rolling(window=12).mean() / df['duration_clean'].rolling(window=12).mean() * 60.0

    # Total duration
    total_duration = df['time'].iloc[-1] - df['time'].iloc[0]
    total_duration_str = str(total_duration)
    if "days" in total_duration_str:
        total_duration_str = total_duration_str.split("days")[1]  # Remove the "0 days" part
    
    # Clean duration (no silence)
    clean_duration_seconds = int(df['cumulative_duration_clean'].iloc[-1])
    clean_duration = timedelta(seconds=clean_duration_seconds)
    
    # Number of unique words (vocabulary)
    num_unique_words_value = df['num_unique_words'].iloc[-1]
    
    # Words per minute (pace)
    words_per_minute = df['pace'].iloc[-1]
    
    # Max pace
    max_pace = df['rolling_avg_pace'].max()
    
    # Min pace
    min_pace = df['rolling_avg_pace'].min()
    
    # Percent of fillers in speech
    percent_fillers = df['fillers_share'].iloc[-1] * 100  # Convert to percentage
    
    # Print the information
    # st.write(f"**Total Duration:** {total_duration_str}")
    # st.write(f"**Clean Duration (no silence):** {clean_duration}")
    # st.write(f"**Number of Unique Words (Vocabulary):** {num_unique_words_value}")
    # st.write(f"**Words per Minute (Pace):** {words_per_minute:.1f}")
    # st.write(f"**Max Pace:** {max_pace:.1f}")
    # st.write(f"**Min Pace:** {min_pace:.1f}")
    # st.write(f"**Percent of Fillers in Speech:** {percent_fillers:.2f}%")
    # st.write(f"**List of Fillers:** {', '.join(filler_words)}")

    # Setting up the Seaborn theme
    sns.set_theme(style="darkgrid")
    
    # Create a 2x2 grid for the plots
    fig, axes = plt.subplots(2, 2, figsize=(18, 14))
    
    # Plot 1: Pace and Rolling Average Pace
    sns.lineplot(ax=axes[0, 0], x='time', y='pace', data=df, color='royalblue', label='Pace')
    # marker=False, linewidth=2.5, 
    sns.lineplot(ax=axes[0, 0], x='time', y='rolling_avg_pace', data=df,  color='orange', label='Rolling Avg Pace')
    # marker=False, linestyle='--', linewidth=2.5,
    axes[0, 0].set_title('Pace and Rolling Average Pace Over Time', fontsize=16, weight='bold')
    axes[0, 0].set_xlabel('Time', fontsize=12)
    axes[0, 0].set_ylabel('Pace', fontsize=12)
    axes[0, 0].legend()
    
    # Plot 2: Number of Unique Words Over Time
    sns.lineplot(ax=axes[0, 1], x='time', y='num_unique_words', data=df, color='teal')
    # marker='o', linewidth=2.5, 
    axes[0, 1].set_title('Number of Unique Words Over Time', fontsize=16, weight='bold')
    axes[0, 1].set_xlabel('Time', fontsize=12)
    axes[0, 1].set_ylabel('Number of Unique Words', fontsize=12)
    
    # Plot 3: Filler Word Share Over Time
    sns.lineplot(ax=axes[1, 0], x='time', y='fillers_share', data=df, color='coral')
    # marker='o', linewidth=2.5, 
    axes[1, 0].set_title('Filler Word Share Over Time', fontsize=16, weight='bold')
    axes[1, 0].set_xlabel('Time', fontsize=12)
    axes[1, 0].set_ylabel('Filler Word Share', fontsize=12)
    
    def format_time(x, pos=None):
        return x.strftime('%H:%M:%S')
    
    # Format x-ticks to show only the time (H:M:S)
    axes[1, 0].xaxis.set_major_formatter(FuncFormatter(lambda x, _: mdates.num2date(x).strftime('%H:%M:%S')))
    axes[0, 0].xaxis.set_major_formatter(FuncFormatter(lambda x, _: mdates.num2date(x).strftime('%H:%M:%S')))
    axes[0, 1].xaxis.set_major_formatter(FuncFormatter(lambda x, _: mdates.num2date(x).strftime('%H:%M:%S')))
    
    # Rotate x-tick labels
    # plt.setp(axes[1, 0].get_xticklabels(), rotation=45, ha='right')
    # plt.setp(axes[0, 0].get_xticklabels(), rotation=45, ha='right')
    # plt.setp(axes[0, 1].get_xticklabels(), rotation=45, ha='right')
    
    
    # Plot 4: Word Cloud of Unique Words
    # Combine all text into one string
    all_text = ' '.join(df['text'])
    
    # Generate the Word Cloud with a larger size
    wordcloud = WordCloud(width=900, height=600, background_color='white').generate(all_text)
    
    # Display the Word Cloud in the bottom right subplot
    axes[1, 1].imshow(wordcloud, interpolation='bilinear')
    axes[1, 1].axis('off')  # Hide axes
    axes[1, 1].set_title('Word Cloud of Unique Words', fontsize=16, weight='bold')
    
    # Adjust layout to avoid overlap
    plt.tight_layout()

    # Display the plots
    st.pyplot(fig)

    # Create a DataFrame to display the information in a table
    info_data = {
        "Metric": [
            "Total Duration",
            "Clean Duration (no silence)",
            "Number of Unique Words (Vocabulary)",
            "Words per Minute (Pace)",
            "Max Pace",
            "Min Pace",
            "Percent of Fillers in Speech",
            "List of Fillers"
        ],
        "Value": [
            total_duration_str,
            clean_duration,
            num_unique_words_value,
            f"{words_per_minute:.1f}",
            f"{max_pace:.1f}",
            f"{min_pace:.1f}",
            f"{percent_fillers:.2f}%",
            ', '.join(filler_words)
        ]
    }
    
    info_df = pd.DataFrame(info_data)
    # Display the table
    # st.table(info_df)
    st.write("")  # Adds a blank line (space)
    st.write(info_df.to_html(index=False), unsafe_allow_html=True)

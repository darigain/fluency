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
st.markdown(
    "More infos and :star: at [github.com/darigain/youtube_subs_analysis](https://github.com/darigain/youtube_subs_analysis)"
)
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
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # Plot 1: Pace and Rolling Average Pace
    sns.lineplot(ax=axes[0, 0], x='time', y='pace', data=df, color='black')
    # marker=False, linewidth=2.5, color='royalblue', label='Pace'
    sns.lineplot(ax=axes[0, 0], x='time', y='rolling_avg_pace', data=df,  color='gray', linestyle=':')
    # marker=False, linestyle='--', linewidth=2.5, color='orange', label='Rolling Avg Pace'
    axes[0, 0].set_title('Cumulative pace and moving average with a one-minute window', fontsize=14, weight='bold')
    axes[0, 0].set_xlabel('Time', fontsize=12)
    axes[0, 0].set_ylabel('Words per minute', fontsize=12)
    # axes[0, 0].legend()
    # axes[0, 0].legend(loc='center', bbox_to_anchor=(0.85, 0.85), frameon=False)

    wpm_data = {
        "CEFR Level": ["A1", "A2", "B1", "B2", "C1", "C2", "Rap God"],
        "Average WPM": [30, 50, 75, 105, 135, 165, 257]
    }

    colors = sns.color_palette("Oranges", len(wpm_data["Average WPM"]))

    for i, (level, wpm) in enumerate(zip(wpm_data["CEFR Level"], wpm_data["Average WPM"])):
        axes[0, 0].axhline(y=wpm, color=colors[i], linestyle='-', label=f'{level} - {wpm} WPM')
        axes[0, 0].text(x=df['time'].max(), y=wpm, s=f'{level} - {wpm} WPM', 
                        color=colors[i], va='bottom')
    # axes[0, 0].legend(loc='upper left', bbox_to_anchor=(1, 1))

    # Plot 2: Number of Unique Words Over Time
    # ________________________________________________________________________
    # Data for the native English teacher
    teacher_data_minutes = np.array([0, 5, 10, 15, 20, 30, 60, 120, 180])
    teacher_data_words = np.array([0, 318, 500, 638, 767, 1000, 1450, 2250, 2800])

    # Create an interpolation function based on the teacher's data
    interpolate_teacher = interp1d(teacher_data_minutes, teacher_data_words, kind='cubic')

    # Define the monologue lengths for plotting
    monologue_lengths_fine = np.linspace(0, 180, 100)

    # Convert minutes to datetime for alignment with the original plot's x-axis
    base_time = pd.to_datetime("1900-01-01 00:00:00")
    time_as_datetime = [base_time + pd.Timedelta(minutes=m) for m in monologue_lengths_fine]

    # Define scaling factors for each CEFR level based on expected differences
    scaling_factors = {
        "A1": 0.2,
        "A2": 0.3,
        "B1": 0.4,
        "B2": 0.6,
        "C1": 0.8,
        "C2": 1.0,
        "Rap God": 2.0, 
    }

    # Get the min and max time from the original data
    min_time = df['time'].min()
    max_time = df['time'].max()

    # Filter the interpolated curves to match the original x-axis time range
    time_as_datetime_filtered = [t for t in time_as_datetime if min_time <= t <= max_time]
    monologue_lengths_filtered = [m for t, m in zip(time_as_datetime, monologue_lengths_fine) if min_time <= t <= max_time]

    # Use the "Oranges" color palette for the lines
    colors = sns.color_palette("Oranges", len(scaling_factors))

    sns.lineplot(ax=axes[0, 1], x='time', y='num_unique_words', data=df, color='black')
    # marker='o', linewidth=2.5,
    axes[0, 1].set_title('Number of unique words over time (vocabulary)', fontsize=14, weight='bold')
    axes[0, 1].set_xlabel('Time', fontsize=12)
    axes[0, 1].set_ylabel('Unique Words', fontsize=12)

    # Add interpolated curves for each CEFR level, aligning time axis to original datetime x-axis
    for i, (level, scale) in enumerate(scaling_factors.items()):
        scaled_words = interpolate_teacher(monologue_lengths_filtered) * scale
        # Apply color from the palette for each line
        axes[0, 1].plot(time_as_datetime_filtered, scaled_words, label=level, linestyle='-', color=colors[i])

        # Add text near each line to label them
        axes[0, 1].text(time_as_datetime_filtered[-1], scaled_words[-1], f'{level}', color=colors[i], va='center')


    # ________________________________________________________________________
    # Plot 3: Filler Word Share Over Time
    sns.lineplot(ax=axes[1, 0], x='time', y='fillers_share', data=df, color='black')
    # marker='o', linewidth=2.5,
    axes[1, 0].set_title('Cumulative filler word share over time', fontsize=14, weight='bold')
    axes[1, 0].set_xlabel('Time', fontsize=12)
    axes[1, 0].set_ylabel('Share', fontsize=12)

    colors = sns.color_palette("Oranges", len(wpm_data["Average WPM"]))
    axes[1, 0].axhline(y=0.2, color=colors[-1], linestyle='-', label='20% level')
    axes[1, 0].text(x=df['time'].max(), y=0.2, s='20% level', 
                        color=colors[-1], va='bottom')

    def format_time(x, pos=None):
        return x.strftime('%H:%M:%S')

    # Format x-ticks to show only the time (H:M:S)
    axes[1, 0].xaxis.set_major_formatter(FuncFormatter(lambda x, _: mdates.num2date(x).strftime('%H:%M:%S')))
    axes[0, 0].xaxis.set_major_formatter(FuncFormatter(lambda x, _: mdates.num2date(x).strftime('%H:%M:%S')))
    axes[0, 1].xaxis.set_major_formatter(FuncFormatter(lambda x, _: mdates.num2date(x).strftime('%H:%M:%S')))

    # Plot 4: Word Cloud of Unique Words
    # Combine all text into one string
    all_text = ' '.join(df['text'])

    # Generate the Word Cloud with a larger size
    wordcloud = WordCloud(width=900, height=600, background_color='white').generate(all_text)

    # Display the Word Cloud in the bottom right subplot
    axes[1, 1].imshow(wordcloud, interpolation='bilinear')
    axes[1, 1].axis('off')  # Hide axes
    axes[1, 1].set_title('Word frequency', fontsize=14, weight='bold')

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
    
    info_df = pd.DataFrame(info_data).T
    # Display the table
    # st.table(info_df)
    st.write("")  # Adds a blank line (space)
    st.write(info_df.to_html(index=False), unsafe_allow_html=True)
    st.write("")  # Adds a blank line (space)
    st.write("")  # Adds a blank line (space)
    st.markdown(
        "More infos and :star: at [github.com/darigain/youtube_subs_analysis](https://github.com/darigain/youtube_subs_analysis)"
    )

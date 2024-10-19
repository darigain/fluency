import pandas as pd
import re
from wordcloud import WordCloud
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
from datetime import timedelta, datetime
from scipy.interpolate import interp1d
import numpy as np
import streamlit as st

# Add text to the left sidebar
st.sidebar.title("Who and Why:")
side_text = '''A bit about me—I'm Aidar, a data analyst, and I built this app to track my own progress in language fluency. I believe it could be helpful for you, too! The app runs on Python, and you can check out the code on GitHub for full transparency.

If you have any privacy concerns, feel free to review the source code on GitHub:

:star: [github.com/darigain](https://github.com/darigain/youtube_subs_analysis) :star:
'''
st.sidebar.write(side_text)

# Streamlit app structure
st.title("Language Proficiency Assessment Tool: Analyze Your Fluency 🗣️")
st.write("")  # Adds a blank line (space)
multi = '''💬Did you know that the average adult native speaker uses around 500 unique words in a 10-minute conversation, speaking at an average speed of 150 words per minute (WPM)? If you're like Eminem, you could hit an impressive 257 WPM! 🎤

📈With this tool, you can analyze your speech patterns, including your speaking speed and active vocabulary. After calculating these values, you'll also get an estimate of your language proficiency level based on CEFR standards. As a bonus, you'll receive a personalized Word Cloud and insights into how frequently you use filler words.💡

🎬To get started, open any YouTube video, click "More," select "Show transcript," and simply copy the text.📜
'''
st.markdown(multi)
st.write("")  # Adds a blank line (space)
st.markdown(
    "Here is an example YouTube video: [youtube.com/watch?v=arj7oStGLkU](https://www.youtube.com/watch?v=arj7oStGLkU)"
)

example = '''
0:12
So in college,
0:15
I was a government major,
0:16
which means I had to write a lot of papers.
0:19
Now, when a normal student writes a paper,
0:21
they might spread the work out a little like this.
0:23
So, you know --
0:25
(Laughter)
0:26
you get started maybe a little slowly,
0:28
but you get enough done in the first week
0:30
that, with some heavier days later on,
0:32
everything gets done, things stay civil.
0:34
(Laughter)
0:35
And I would want to do that like that.
0:38
That would be the plan.
0:39
I would have it all ready to go,
0:41
but then, actually, the paper would come along,
0:44
and then I would kind of do this.
0:46
(Laughter)
0:48
And that would happen every single paper.
0:51
But then came my 90-page senior thesis,
0:55
a paper you're supposed to spend a year on.
0:57
And I knew for a paper like that, my normal work flow was not an option.
1:01
It was way too big a project.
1:02
So I planned things out,
1:04
and I decided I kind of had to go something like this.
1:07
This is how the year would go.
1:09
So I'd start off light,
1:11
and I'd bump it up in the middle months,
1:13
and then at the end, I would kick it up into high gear
1:16
just like a little staircase.
1:17
How hard could it be to walk up the stairs?
1:20
No big deal, right?
1:23
But then, the funniest thing happened.
1:24
Those first few months?
1:26
They came and went,
1:27
and I couldn't quite do stuff.
1:29
So we had an awesome new revised plan.
1:31
(Laughter)
1:32
And then --
1:33
(Laughter)
1:35
But then those middle months actually went by,
1:38
and I didn't really write words,
1:40
and so we were here.
1:43
And then two months turned into one month,
1:46
which turned into two weeks.
1:47
And one day I woke up
1:49
with three days until the deadline,
1:53
still not having written a word,
1:55
and so I did the only thing I could:
1:57
I wrote 90 pages over 72 hours,
2:00
pulling not one but two all-nighters --
2:02
humans are not supposed to pull two all-nighters --
2:06
sprinted across campus,
2:08
dove in slow motion,
2:09
and got it in just at the deadline.
2:11
I thought that was the end of everything.
2:14
But a week later I get a call,
2:15
and it's the school.
2:17
And they say, "Is this Tim Urban?"
2:19
And I say, "Yeah."
2:20
And they say, "We need to talk about your thesis."
2:23
And I say, "OK."
2:25
And they say,
2:27
"It's the best one we've ever seen."
2:29
(Laughter)
2:32
(Applause)
2:36
That did not happen.
2:38
(Laughter)
2:40
It was a very, very bad thesis.
2:43
(Laughter)
2:45
I just wanted to enjoy that one moment when all of you thought,
2:49
"This guy is amazing!"
2:51
(Laughter)
2:52
No, no, it was very, very bad.
2:55
Anyway, today I'm a writer-blogger guy.
2:58
I write the blog Wait But Why.
3:00
And a couple of years ago, I decided to write about procrastination.
3:04
My behavior has always perplexed the non-procrastinators around me,
3:07
and I wanted to explain to the non-procrastinators of the world
3:11
what goes on in the heads of procrastinators,
3:13
and why we are the way we are.
3:14
Now, I had a hypothesis
3:16
that the brains of procrastinators were actually different
3:18
than the brains of other people.
3:21
And to test this, I found an MRI lab
3:23
that actually let me scan both my brain
3:26
and the brain of a proven non-procrastinator,
3:29
so I could compare them.
3:30
I actually brought them here to show you today.
3:32
I want you to take a look carefully to see if you can notice a difference.
3:36
I know that if you're not a trained brain expert,
3:38
it's not that obvious, but just take a look, OK?
3:40
So here's the brain of a non-procrastinator.
3:43
(Laughter)
3:46
Now ...
3:48
here's my brain.
3:50
(Laughter)
3:55
There is a difference.
3:57
Both brains have a Rational Decision-Maker in them,
4:00
but the procrastinator's brain
4:01
also has an Instant Gratification Monkey.
4:05
Now, what does this mean for the procrastinator?
4:07
Well, it means everything's fine until this happens.
4:09
[This is a perfect time to get some work done.] [Nope!]
4:12
So the Rational Decision-Maker will make the rational decision
4:15
to do something productive,
4:17
but the Monkey doesn't like that plan,
4:19
so he actually takes the wheel,
4:20
and he says, "Actually, let's read the entire Wikipedia page
4:23
of the Nancy Kerrigan/ Tonya Harding scandal,
4:25
because I just remembered that that happened.
4:28
(Laughter)
4:29
Then --
4:30
(Laughter)
4:31
Then we're going to go over to the fridge,
4:33
to see if there's anything new in there since 10 minutes ago.
4:36
After that, we're going to go on a YouTube spiral
4:39
that starts with videos of Richard Feynman talking about magnets
4:42
and ends much, much later with us watching interviews
4:45
with Justin Bieber's mom.
4:47
(Laughter)
4:49
"All of that's going to take a while,
4:51
so we're not going to really have room on the schedule for any work today.
4:54
Sorry!"
4:55
(Sigh)
4:58
Now, what is going on here?
5:03
The Instant Gratification Monkey does not seem like a guy
5:06
you want behind the wheel.
5:07
He lives entirely in the present moment.
5:09
He has no memory of the past, no knowledge of the future,
5:12
and he only cares about two things:
5:14
easy and fun.
5:16
Now, in the animal world, that works fine.
5:19
If you're a dog
5:20
and you spend your whole life doing nothing other than easy and fun things,
5:24
you're a huge success!
5:25
(Laughter)
5:27
And to the Monkey,
5:29
humans are just another animal species.
5:32
You have to keep well-slept, well-fed and propagating into the next generation,
5:36
which in tribal times might have worked OK.
5:38
But, if you haven't noticed, now we're not in tribal times.
5:41
We're in an advanced civilization, and the Monkey does not know what that is.
5:45
Which is why we have another guy in our brain,
5:48
the Rational Decision-Maker,
5:50
who gives us the ability to do things no other animal can do.
5:53
We can visualize the future.
5:55
We can see the big picture.
5:57
We can make long-term plans.
5:58
And he wants to take all of that into account.
6:02
And he wants to just have us do
6:03
whatever makes sense to be doing right now.
6:06
Now, sometimes it makes sense
6:08
to be doing things that are easy and fun,
6:10
like when you're having dinner or going to bed
6:12
or enjoying well-earned leisure time.
6:14
That's why there's an overlap.
6:15
Sometimes they agree.
6:17
But other times, it makes much more sense
6:20
to be doing things that are harder and less pleasant,
6:24
for the sake of the big picture.
6:25
And that's when we have a conflict.
6:28
And for the procrastinator,
6:29
that conflict tends to end a certain way every time,
6:31
leaving him spending a lot of time in this orange zone,
6:35
an easy and fun place that's entirely out of the Makes Sense circle.
6:39
I call it the Dark Playground.
6:42
(Laughter)
6:43
Now, the Dark Playground is a place
6:47
that all of you procrastinators out there know very well.
6:50
It's where leisure activities happen
6:52
at times when leisure activities are not supposed to be happening.
6:56
The fun you have in the Dark Playground
6:58
isn't actually fun, because it's completely unearned,
7:00
and the air is filled with guilt, dread, anxiety, self-hatred --
7:04
all of those good procrastinator feelings.
7:06
And the question is, in this situation, with the Monkey behind the wheel,
7:10
how does the procrastinator ever get himself over here to this blue zone,
7:13
a less pleasant place, but where really important things happen?
7:17
Well, turns out the procrastinator has a guardian angel,
7:22
someone who's always looking down on him and watching over him
7:25
in his darkest moments --
7:26
someone called the Panic Monster.
7:28
(Laughter)
7:34
Now, the Panic Monster is dormant most of the time,
7:39
but he suddenly wakes up anytime a deadline gets too close
7:43
or there's danger of public embarrassment,
7:45
a career disaster or some other scary consequence.
7:47
And importantly, he's the only thing the Monkey is terrified of.
7:51
Now, he became very relevant in my life pretty recently,
7:56
because the people of TED reached out to me about six months ago
7:59
and invited me to do a TED Talk.
8:01
(Laughter)
8:07
Now, of course, I said yes.
8:08
It's always been a dream of mine to have done a TED Talk in the past.
8:12
(Laughter)
8:16
(Applause)
8:24
But in the middle of all this excitement,
8:26
the Rational Decision-Maker seemed to have something else on his mind.
8:29
He was saying, "Are we clear on what we just accepted?
8:32
Do we get what's going to be now happening one day in the future?
8:35
We need to sit down and work on this right now."
8:37
And the Monkey said, "Totally agree, but let's just open Google Earth
8:40
and zoom in to the bottom of India, like 200 feet above the ground,
8:44
and scroll up for two and a half hours til we get to the top of the country,
8:47
so we can get a better feel for India."
8:49
(Laughter)
8:55
So that's what we did that day.
8:56
(Laughter)
9:00
As six months turned into four and then two and then one,
9:04
the people of TED decided to release the speakers.
9:07
And I opened up the website, and there was my face
9:10
staring right back at me.
9:11
And guess who woke up?
9:13
(Laughter)
9:17
So the Panic Monster starts losing his mind,
9:19
and a few seconds later, the whole system's in mayhem.
9:22
(Laughter)
9:27
And the Monkey -- remember, he's terrified of the Panic Monster --
9:30
boom, he's up the tree!
9:31
And finally,
9:32
finally, the Rational Decision-Maker can take the wheel
9:35
and I can start working on the talk.
9:37
Now, the Panic Monster explains
9:39
all kinds of pretty insane procrastinator behavior,
9:43
like how someone like me could spend two weeks
9:45
unable to start the opening sentence of a paper,
9:49
and then miraculously find the unbelievable work ethic
9:52
to stay up all night and write eight pages.
9:56
And this entire situation, with the three characters --
9:59
this is the procrastinator's system.
10:02
It's not pretty, but in the end, it works.
10:05
This is what I decided to write about on the blog a couple of years ago.
10:09
When I did, I was amazed by the response.
10:12
Literally thousands of emails came in,
10:14
from all different kinds of people from all over the world,
10:17
doing all different kinds of things.
10:19
These are people who were nurses, bankers, painters, engineers
10:22
and lots and lots of PhD students.
'''
with st.expander("👉Click to reveal the example👈"):
    st.code(example)

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
        text = re.sub(r'\(.*?\)', '', text)  # Remove words in round brackets
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
    clean_duration_minutes = int(clean_duration_seconds/60.0)
    
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
    fig, axes = plt.subplots(2, 2, figsize=(20, 16))

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
    wordcloud = WordCloud(background_color='white').generate(all_text)

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
            "Speaking Duration",
            "Minutes",
            "Unique Words",
            "WPM",
            "Max WPM",
            "Min WPM",
            "Fillers Percentage",
            "List of Fillers"
        ],
        "Value": [
            total_duration_str,
            clean_duration,
            clean_duration_minutes,
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
    #############################################################

    # Function to map unique words to CEFR level based on the interpolation
    def get_vocab_cefr_level(num_unique_words, duration_minutes):
        scaled_vocab = {level: interpolate_teacher(duration_minutes) * scale for level, scale in scaling_factors.items()}
        for level, vocab_threshold in scaled_vocab.items():
            if num_unique_words <= vocab_threshold:
                return level
        return "C2"  # Default to C2 if beyond the range
    
    # Define CEFR levels for words per minute (WPM)
    wpm_levels = {
        "A1": 30,
        "A2": 50,
        "B1": 75,
        "B2": 105,
        "C1": 135,
        "C2": 165
    }
    
    # Function to map WPM to CEFR level
    def get_cefr_level(value, levels_dict):
        for level, threshold in levels_dict.items():
            if value <= threshold:
                return level
        return "C2"  # Highest level
    
    # Calculate the minimum and maximum levels for num_unique_words_value and words_per_minute
    min_level = min(get_vocab_cefr_level(num_unique_words_value, clean_duration_minutes), 
                    get_cefr_level(words_per_minute, wpm_levels))
    
    max_level = max(get_vocab_cefr_level(num_unique_words_value, clean_duration_minutes), 
                    get_cefr_level(words_per_minute, wpm_levels))
    if max_level == "Rap God":
        max_level = "Native"
    # Output the language level range in the format "A2 - B1"
    language_level_range = f"{min_level} - {max_level}"
    st.write(f"**Language Level Range:** {language_level_range}")

    #############################################################
    # Create a DataFrame to display the information in a table
    info_data = {
        "Metric": [
            "Total Duration",
            "Speaking Duration",
            "Minutes",
            "Unique Words",
            "WPM",
            "Level",
            "Max WPM",
            "Min WPM",
            "Fillers Percentage",
            "List of Fillers"
        ],
        "Value": [
            total_duration_str,
            clean_duration,
            clean_duration_minutes,
            num_unique_words_value,
            f"{words_per_minute:.1f}",
            language_level_range,
            f"{max_pace:.1f}",
            f"{min_pace:.1f}",
            f"{percent_fillers:.2f}%",
            ', '.join(filler_words)
        ]
    }
    
    info_df = pd.DataFrame(info_data).T
    
    st.write("")  # Adds a blank line (space)
    st.write(info_df.to_html(index=False), unsafe_allow_html=True)
    st.write("")  # Adds a blank line (space)

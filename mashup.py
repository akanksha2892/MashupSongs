# Importing the required packages
import streamlit as st
from email.message import EmailMessage
import os
from pytube import YouTube, Search
import moviepy.editor as mp
from moviepy.editor import AudioFileClip, concatenate_audioclips
import zipfile
import smtplib

# Set the sender's email and password
sender = "asolanki50_be22@thapar.edu"
password = "Limcee@89"

# Function to check constraints
def check_constraints(number_of_videos, audio_duration):
    if int(number_of_videos) < 10:
        st.error('Number of videos should be any positive number greater than or equal to 10!')
        return False
    elif int(audio_duration) < 20:
        st.error('Duration of sub-audios should be greater than or equal to 20!')
        return False
    return True

# Set Streamlit page configuration and title
st.set_page_config(layout='centered', page_title='Mashup')
st.write('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)
st.header("MASHUP")

# Hide Streamlit menu and add footer
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

# Create a form for user input
with st.form("form1", clear_on_submit=True):
    singer_name = st.text_input("Singer Name")
    num_videos = st.text_input("Number of Videos")
    duration = st.text_input("Duration of each video (in sec)")
    email = st.text_input("Email ID", placeholder='example@thapar.edu')
    submit = st.form_submit_button("Submit")

# Email settings
subject = "Mashup Results"
msg = EmailMessage()
msg['Subject'] = subject
msg['From'] = sender
msg['To'] = email
message = """This is a mashup zipfile you want.
Done By -
Akanksha Solanki
102297010
CSE 5
"""
filename = 'mashup.zip'

# Process form submission
if submit:
    path = os.getcwd()
    search_results = []
    vid_files = []
    aud_files = [] 
    sub_files = []
    aud_clip = []
    s = Search(singer_name)
    
    # Check constraints
    if check_constraints(num_videos, duration):
        # Processing
        st.write("Processing videos...")
        for v in s.results:
            search_results.append(v.watch_url)
        for i in range(0, int(num_videos)):
            yt = YouTube(search_results[i])
            fin = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution')[-1].download()
            os.rename(fin, 'Video-%s.mp4' % i)
            vid_files.append('Video-%s.mp4' % i)
        
        # Video to audio conversion
        st.write("Converting videos to audios...")
        for i in range(0, len(vid_files)):
            clip = mp.VideoFileClip(r'%s' % os.path.join(path, vid_files[i]))
            clip.audio.write_audiofile(r'%s.mp3' % os.path.join(path, "Audio-%d" % i))
            aud_files.append('Audio-%d.mp3' % i)
        
        # Extracting sub-audios
        st.write("Extracting sub-audios...")
        for i in range(0, len(aud_files)):
            sub_file = AudioFileClip(r'%s' % os.path.join(path, aud_files[i]))
            final = sub_file.subclip(0, int(duration))
            final.write_audiofile(r'%s.mp3' % os.path.join(path, "SubAudio-%d" % i))
            sub_files.append('SubAudio-%d.mp3' % i)
        
        # Concatenating audios
        st.write("Concatenating audios...")
        for i in range(0, len(sub_files)):
            aud_clip.append(AudioFileClip(r'%s' % os.path.join(path, sub_files[i])))
        final_audio = concatenate_audioclips(aud_clip)
        final_audio.write_audiofile(r'%s.mp3' % os.path.join(path, 'Mashup'))
        
        # Creating zip file
        st.write("Creating mashup zip file...")
        with zipfile.ZipFile("mashup.zip", "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.write("./Mashup.mp3")
        
        # Sending email
        st.write("Sending email...")
        with open(filename,"rb") as f:
            file_data = f.read()
            file_name = f.name
            msg.set_content(message)
            msg.add_attachment(file_data, maintype="application", subtype="csv", filename=file_name)

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            try:
                server.login(sender, password)
                server.send_message(msg)
                st.success("Email Sent Successfully!")
            except smtplib.SMTPAuthenticationError:
                st.error("Unable to sign in")

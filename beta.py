import streamlit as st
import requests
from io import BytesIO
from pydub import AudioSegment


st.set_page_config(page_title="development",
                    page_icon='📖',
                    layout='centered'
                    )
url = "https://drive.google.com/file/d/1DxJKp7k8VBtIyi0C4E2Xys_fR27KOiGf/view?usp=share_link"

# Make a GET request to the URL to get the audio content
response = requests.get(url)

# Load the audio content into a PyDub AudioSegment object
audio_data = AudioSegment.from_file(BytesIO(response.content))

# Convert the AudioSegment to raw PCM data
raw_audio_data = audio_data.raw_data

# Create a Streamlit audio player with the raw PCM data
st.audio(raw_audio_data, format='audio/mp3')

import streamlit as st
import numpy as np
import scipy.io.wavfile as wav
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import whisper
import time
import math
import os
import matplotlib.pyplot as plt
from pydub import AudioSegment
from pydub.playback import play
import subprocess
from pyvirtualdisplay import Display

whisper_model = whisper.load_model("base")

def record_audio(output_file, duration):
    try:
        # Start a virtual display
        display = Display(visible=0, size=(1920, 1080))
        display.start()

        # Start recording the system audio
        command = f"ffmpeg -f pulse -i default -t {duration} -c:a pcm_s16le {output_file}"
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.communicate()

        if process.returncode != 0:
            st.error('Error recording audio. Please make sure ffmpeg is properly installed and configured.')
            return

        display.stop()
        print('Recording finished')
    except Exception as e:
        st.error(f"Error during recording: {e}")
        return

def transcribe_audio_whisper_lib(audio_path):
    try:
        transcript = ""
        sample_rate, data = wav.read(audio_path)
        max_duration = 30 * 60  # 30 minutes in seconds
        num_segments = math.ceil(len(data) / (sample_rate * max_duration))

        for i in range(num_segments):
            start_sample = i * sample_rate * max_duration
            end_sample = min((i + 1) * sample_rate * max_duration, len(data))

            segment_path = f"segment_{i}.wav"
            wav.write(segment_path, sample_rate, data[start_sample:end_sample])
            print(f"Transcribing segment {i + 1} of {num_segments}")

            segment_transcript = whisper_model.transcribe(segment_path)["text"]
            transcript += segment_transcript + "\n"

            os.remove(segment_path)

        return transcript
    except Exception as e:
        st.error(f"Error transcribing audio: {e}")
        st.stop()

def join_jitsi_meeting(url):
    options = Options()
    options.headless = False  # Change to True if you don't want to see the browser
    options.add_argument('--use-fake-ui-for-media-stream')  # Automatically allow camera and microphone

    service = Service('misc/chromedriver.exe')  # Update with the correct path to chromedriver
    browser = webdriver.Chrome(service=service, options=options)
    browser.get(url)

    time.sleep(5)  # Wait for the page to load

    # Disable microphone and camera
    mic_button = browser.find_element(By.XPATH, "//div[@aria-label='Silenciar micrófono']")
    mic_button.click()
    camera_button = browser.find_element(By.XPATH, "//div[@aria-label='Alternar vídeo']")
    camera_button.click()

    # Enter the name "Sec-Auto" in the text field
    name_input = browser.find_element(By.XPATH, "//input[@aria-label='Por favor ingresa tu nombre aquí']")
    name_input.send_keys("Sec-Auto")

    # Click the "Join Meeting" button
    join_button = browser.find_element(By.XPATH, "//div[@data-testid='prejoin.joinMeeting']")
    join_button.click()

    return browser

def plot_audio_levels(audio_data):
    fig, ax = plt.subplots(figsize=(8, 2))
    ax.plot(audio_data)
    ax.set_xlabel('Time')
    ax.set_ylabel('Amplitude')
    ax.set_title('Audio Levels')
    return fig

st.title('Jitsi Conference Recorder')
meeting_url_input = st.text_input('Enter Jitsi Meeting URL')
recording_duration = st.number_input('Enter recording duration in seconds', min_value=1, max_value=3600, value=60)

if st.button('Start Recording'):
    if meeting_url_input:
        browser = join_jitsi_meeting(meeting_url_input)
        st.write('Recording audio...')

        record_audio('conference_audio.wav', duration=recording_duration)

        st.write('Recording finished and saved to conference_audio.wav')
        transcription = transcribe_audio_whisper_lib('conference_audio.wav')
        st.write(transcription)
        browser.quit()
    else:
        st.write('Please enter a valid Jitsi Meeting URL')

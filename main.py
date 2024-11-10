import streamlit as st
import pyaudio
import wave
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

whisper_model = whisper.load_model("base")

def record_audio(output_file, duration):
    sample_rate = 44100
    chunk_size = 1024
    audio_format = pyaudio.paInt16
    channels = 2

    p = pyaudio.PyAudio()
    stream = p.open(format=audio_format, channels=channels,
                    rate=sample_rate, input=True,
                    frames_per_buffer=chunk_size)

    frames = []

    print('Recording')
    for _ in range(0, int(sample_rate / chunk_size * duration)):
        data = stream.read(chunk_size)
        frames.append(data)

    print('Recording finished')

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(output_file, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(audio_format))
    wf.setframerate(sample_rate)
    wf.writeframes(b''.join(frames))
    wf.close()

def transcribe_audio_whisper_lib(audio_path):
    try:
        transcript = ""
        sample_rate, data = wav.read(audio_path)
        max_duration = 30 * 60  # 30 minutos en segundos
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
        st.error(f"Error al transcribir el audio: {e}")
        st.stop()

def join_jitsi_meeting(url):
    options = Options()
    options.headless = False  # Cambiar a True si no deseas ver el navegador
    options.add_argument('--use-fake-ui-for-media-stream')  # Permitir automáticamente cámara y micrófono

    service = Service('misc/chromedriver.exe')  # Actualiza con la ruta correcta a chromedriver
    browser = webdriver.Chrome(service=service, options=options)
    browser.get(url)

    time.sleep(5)  # Espera a que la página cargue

    # Desactivar micrófono y cámara
    mic_button = browser.find_element(By.XPATH, "//div[@aria-label='Silenciar micrófono']")
    mic_button.click()
    camera_button = browser.find_element(By.XPATH, "//div[@aria-label='Alternar vídeo']")
    camera_button.click()

    # Ingresa el nombre "Sec-Auto" en el campo de texto
    name_input = browser.find_element(By.XPATH, "//input[@aria-label='Por favor ingresa tu nombre aquí']")
    name_input.send_keys("Sec-Auto")

    # Hacer clic en el botón "Entrar a la reunión"
    join_button = browser.find_element(By.XPATH, "//div[@data-testid='prejoin.joinMeeting']")
    join_button.click()

    return browser

def save_transcript_to_file(transcript, file_path):
    with open(file_path, 'w') as f:
        f.write(transcript)

st.title('Jitsi Conference Recorder')
meeting_url_input = st.text_input('Enter Jitsi Meeting URL')
recording_duration = st.number_input('Enter recording duration in seconds', min_value=1, max_value=3600, value=60)

if st.button('Start Recording'):
    if meeting_url_input:
        browser = join_jitsi_meeting(meeting_url_input)
        st.write('Recording audio...')

        record_audio('conference_audio.wav', duration=recording_duration)
        browser.quit()  # Cerrar el navegador antes de empezar la transcripción

        st.write('Recording finished and saved to conference_audio.wav')
        transcription = transcribe_audio_whisper_lib('conference_audio.wav')
        st.write(transcription)

        # Guardar la transcripción en un archivo .txt
        save_transcript_to_file(transcription, 'transcription.txt')
        st.write('Transcription saved to transcription.txt')
    else:
        st.write('Please enter a valid Jitsi Meeting URL')

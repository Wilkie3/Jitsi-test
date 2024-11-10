
# Jitsi Conference Recorder

This application allows you to record and transcribe audio from Jitsi meetings using Streamlit, PyAudio, and Whisper.

## Requirements

Ensure you have the necessary packages installed. You can install them using `pip` with the provided `requirements.txt` file:

```bash
pip install -r requirements.txt
```

Contents of `requirements.txt`:
```
streamlit==1.11.0
pyaudio==0.2.11
numpy==1.22.3
scipy==1.8.1
selenium==4.1.5
whisper==1.1.4
```

## Usage

1. Clone this repository or download the files to your local machine.
2. Navigate to the directory containing the application files.
3. Run the Streamlit application with the following command:

   ```bash
   streamlit run app.py
   ```

4. Open a web browser and go to [http://localhost:8501](http://localhost:8501) to access the application.

### Instructions

1. **Enter the Jitsi meeting URL** in the field provided.
2. **Enter the desired recording duration** in seconds.
3. Click the **Start Recording** button.

The application will:
- Open a Chrome browser (Chrome and `chromedriver` required).
- Join the specified Jitsi meeting with the microphone and camera turned off.
- Record the meeting audio for the specified duration.

Once complete, the application will:
- Save the audio recording as `conference_audio.wav`.
- Transcribe the audio using Whisper and display the transcription in the app.
- Save the transcription to `transcription.txt` in the same directory.

## Files

- `app.py`: Source code for the application.
- `requirements.txt`: List of required dependencies.
- `transcription.txt`: Generated transcription file (created automatically).

## Notes

- Ensure `chromedriver` is installed and correctly configured in your system path as specified in the code.
- Selenium is used to automate browser interaction with Jitsi.

Enjoy using the Jitsi Conference Recorder! If you have any questions or need assistance, feel free to reach out.

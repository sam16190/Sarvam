from flask import Flask, request, jsonify
import requests
from pydub import AudioSegment
import os

app = Flask(__name__)

SARVAM_API_KEY = "68ac8d5b-71d2-4103-8d8e-95607a8fa345"
SARVAM_API_BASE_URL = "https://api.sarvam.ai"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/speech-to-text-translate', methods=['POST'])
def speech_to_text_translate():
    try:
        # Ensure a file is sent
        if 'audio' not in request.files:
            return jsonify({"error": "No file part"}), 400
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        # Save the audio file
        file_path = os.path.join(UPLOAD_FOLDER, audio_file.filename)
        audio_file.save(file_path)

        try:
            # Convert audio to WAV format
            converted_path = os.path.join(UPLOAD_FOLDER, "converted_audio.wav")
            audio = AudioSegment.from_file(file_path)
            audio.export(converted_path, format="wav")
        except Exception as e:
            return jsonify({"error": f"Audio conversion failed: {str(e)}"}), 500

        # Send the converted audio to SARVAM API
        with open(converted_path, "rb") as f:
            files = {'audio_file': f}
            headers = {
                "api-subscription-key": SARVAM_API_KEY,
            }
            response = requests.post(f"{SARVAM_API_BASE_URL}/speech-to-text-translate", files=files, headers=headers)
            print(response.text)

        # Cleanup temporary files
        os.remove(file_path)
        os.remove(converted_path)

        # Handle the response from SARVAM API
        if response.status_code == 200:
            result = response.json()
        else:
            result = {"error": "Transcription and translation failed", "details": response.text}

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

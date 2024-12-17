from flask import Flask, request, jsonify
import speech_recognition as sr
from deep_translator import GoogleTranslator
import threading

app = Flask(__name__)

listening = False
recognizer = sr.Recognizer()
microphone = sr.Microphone()
message = ""  # To store the latest status message

def listen_and_translate(source_lang, target_lang):
    global listening, message
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        while listening:
            try:
                print("Listening for audio...")
                audio_data = recognizer.listen(source)
                text = recognizer.recognize_google(audio_data, language=source_lang)
                print(f"Recognized text: {text}")
                message = f"Recognized text: {text}"  # Update the message

                translation = GoogleTranslator(source=source_lang, target=target_lang).translate(text)
                print(f"Translated text: {translation}")
                message = f"Translated text: {translation}"  # Update the message

            except sr.UnknownValueError:
                print("Could not understand audio")
                message = "Could not understand audio"  # Update the message
            except sr.RequestError as e:
                print(f"Speech Recognition API Error: {e}")
                message = f"API Error: {e}"  # Update the message
            except Exception as e:
                print(f"Translation Error: {e}")
                message = f"Translation Error: {e}"  # Update the message

@app.route('/start_listening', methods=['POST'])
def start_listening():
    global listening
    if not listening:
        listening = True
        source_lang = request.json.get('source_lang', 'en')
        target_lang = request.json.get('target_lang', 'en')
        threading.Thread(target=listen_and_translate, args=(source_lang, target_lang), daemon=True).start()
        return jsonify({'status': 'Listening started'})
    return jsonify({'status': 'Already listening'})

@app.route('/stop_listening', methods=['POST'])
def stop_listening():
    global listening
    if listening:
        listening = False
        return jsonify({'status': 'Listening stopped'})
    return jsonify({'status': 'Already stopped'})

@app.route('/get_message', methods=['GET'])
def get_message():
    return jsonify({'message': message})  # Return the current status message

if __name__ == '__main__':
    app.run(debug=True)

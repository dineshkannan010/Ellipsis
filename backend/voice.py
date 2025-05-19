from dia.model import Dia
import soundfile as sf


def text_2_audio(text : str):
    api_key = ""

    # Replace with the desired voice ID (use one from your ElevenLabs dashboard)
    voice_id = "EXAVITQu4vr4xnSDxMaL"  # Example: "Rachel"

    # Text you want to convert to speech
    

    # ElevenLabs TTS endpoint
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    # Request headers
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }

    # Request payload
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",  # Or "eleven_multilingual_v1" for multi-language
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }

    # Make the POST request to ElevenLabs
    response = requests.post(url, headers=headers, json=data)

    # Check for errors
    if response.status_code != 200:
        print("Error:", response.text)
    else:
        # Save the audio content to a file
        with open("output.wav", "wb") as f:
            f.write(response.content)
        print("✅ Audio saved as output.wav")
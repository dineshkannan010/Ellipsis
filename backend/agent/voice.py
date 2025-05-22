# from dia.model import Dia
# import soundfile as sf



# def text_2_audio(text : str):
#     model = Dia.from_pretrained("nari-labs/Dia-1.6B")
#     #text = "[S1] Dia is an open weights text to dialogue model. [S2] You get full control over scripts and voices. [S1] Wow. Amazing. (laughs) [S2] Try it now on GitHub or Hugging Face."
#     output = model.generate(text)
#     sf.write("simple.mp3", output, 44100)

from scipy.io.wavfile import write
from orpheus_cpp import OrpheusCpp
import numpy as np
from dotenv import load_dotenv
from pydub import AudioSegment
load_dotenv()
# List your WAV files in order



voices = {
    'S1' : 'tara',
    'S2' : 'leo',
    'S3' : 'jess',
    'S4' : 'lea',
    'S5' : 'dan',
    'S6' : 'mia',
    'S7' : 'zac',
    'S8' : 'zoe'
}
def text_2_audio(texts = ''):
    orpheus = OrpheusCpp(verbose=False, lang="en")

    # buffer = []
    # for i, (sr, chunk) in enumerate(orpheus.stream_tts_sync(text, options={"voice_id": "tara"})):
    #    buffer.append(chunk)
    #    print(f"Generated chunk {i}")
    # buffer = np.concatenate(buffer, axis=1)
    # write("output.wav", 24_000, np.concatenate(buffer))

    file_paths = []

    for i,(v,text) in enumerate(texts):
        buffer = []
        wav_file = f"segment_{i}.wav"
        for j, (sr, chunk) in enumerate(orpheus.stream_tts_sync(text, options={"voice_id": f"{voices[v]}"})):
            buffer.append(chunk)
            print(f"Generated chunk {j}")
        buffer = np.concatenate(buffer, axis=1)
        file_paths.append(wav_file)
        write(wav_file, 24_000, np.concatenate(buffer))

    combined = AudioSegment.empty()

    for wav_file in file_paths:
        audio = AudioSegment.from_wav(wav_file)
        combined += audio

    combined.export("final_podcast.wav", format="wav")


text_2_audio()
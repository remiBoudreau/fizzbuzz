# Python
from flask import Flask
from flask import request, jsonify, send_file
import io

# Speech Brain
import torchaudio
from speechbrain.pretrained import Tacotron2
from speechbrain.pretrained import HIFIGAN

app = Flask(__name__)

@app.route('/api/tts', methods = ['GET', 'POST'])
def tts():
    print('wtf')
    # Append save_path to json
    text = request.json['text']

    # Intialize TTS (tacotron2) and Vocoder (HiFIGAN)
    tacotron2 = Tacotron2.from_hparams(source="speechbrain/tts-tacotron2-ljspeech", savedir="tmpdir_tts")
    hifi_gan = HIFIGAN.from_hparams(source="speechbrain/tts-hifigan-ljspeech", savedir="tmpdir_vocoder")

    # Running the TTS
    mel_output, mel_length, alignment = tacotron2.encode_text(text)
    # Running Vocoder (spectrogram-to-waveform)
    waveforms = hifi_gan.decode_batch(mel_output)
    # Save the waveform to bytes Buffer
    buffer_ = io.BytesIO()
    torchaudio.save(buffer_, waveforms.squeeze(1), 22050, format="wav")
    buffer_.seek(0)

    # Send binary data
    return send_file(
        FileWrapper(buffer_), 
        mimetype="audio/wav"
        )

@app.route('/', methods = ['GET', 'POST'])
def stt():
    resp = jsonify({"success":True}) 
    return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
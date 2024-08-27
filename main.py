import os
from google.cloud import texttospeech
import PyPDF2
from flask import Flask, render_template, redirect, request, flash
from flask_bootstrap import Bootstrap5

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['UPLOAD_FOLDER'] = 'uploads/'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
Bootstrap5(app)


def synthesize_text(t, output_filename):
    client = texttospeech.TextToSpeechClient()
    input_text = texttospeech.SynthesisInput(text=t)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Standard-C",
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        request={"input": input_text, "voice": voice, "audio_config": audio_config}
    )
    output_path = f"output_{output_filename}.mp3"
    with open(f"static/{output_path}", "wb") as out:
        out.write(response.audio_content)
        out.flush()
        print('Audio content written to file "output.mp3"')
    return output_path


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'pdf' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['pdf']

    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if file and file.filename.endswith('.pdf'):
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        flash('File successfully uploaded')
        with open(f"uploads/{filename}", 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            all_text = ""
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text = page.extract_text()
                all_text += text
        base_filename = os.path.splitext(filename)[0]
        print(base_filename)
        output_mp3_filename = synthesize_text(all_text, base_filename)
        return render_template('index.html', audio_filename=output_mp3_filename)

    else:
        flash('Only PDF files are allowed')
        return redirect(request.url)


if __name__ == '__main__':
    app.run(debug=True, port=5003)
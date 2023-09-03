from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
from generate import generatex
import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER_img'] = 'myimg'
app.config['UPLOAD_FOLDER_speech'] = 'myspeech'
app.config['UPLOAD_FOLDER_background'] = 'mybackground'

@app.route('/')
def index():
    images = os.listdir(app.config['UPLOAD_FOLDER_img'])
    has_files = images and os.listdir(app.config['UPLOAD_FOLDER_speech']) and os.listdir(app.config['UPLOAD_FOLDER_background'])
    return render_template('index.html', images=images, has_files=has_files)

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return redirect(request.url)
    
    files = request.files.getlist('file')
    
    for file in files:
        if file.filename == '':
            continue

        # Generate a unique filename based on the current timestamp
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"{timestamp}_{secure_filename(file.filename)}"
        
        file.save(os.path.join(app.config['UPLOAD_FOLDER_img'], filename))
    
    return redirect(url_for('index'))

@app.route('/myimg/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER_img'], filename)

@app.route('/delete/<image>')
def delete(image):
    os.remove(os.path.join(app.config['UPLOAD_FOLDER_img'], image))
    return redirect(url_for('index'))

@app.route('/generate', methods=['POST'])
def generate():
    if request.method == 'POST':
        speech_file = request.files.get('speech')
        background_file = request.files.get('background')

        if speech_file and speech_file.filename.endswith('.mp3') and background_file and background_file.filename.endswith('.mp3'):
            speech_file.save(f"{app.config['UPLOAD_FOLDER_speech']}/{speech_file.filename}")
            background_file.save(f"{app.config['UPLOAD_FOLDER_background']}/{background_file.filename}")
            
            # Generate random numbers and multiply
            output_path=generatex()
            
            return render_template('result.html',output_path=output_path)
        else:
            return render_template('index.html', message='Please upload both an MP3 speech file and an MP3 background file.')

    return render_template('index.html', message='Upload both an MP3 speech file and an MP3 background file.')

if __name__ == '__main__':
    app.run(debug=True,port=5000)

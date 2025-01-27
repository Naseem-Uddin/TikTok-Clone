import os
from flask import Flask, render_template, url_for

app = Flask(__name__)

@app.route('/')
def home():
    # List all video files in the 'static/videos' directory
    video_folder = os.path.join(app.static_folder, 'videos')
    video_files = [f"videos/{file}" for file in os.listdir(video_folder) if file.endswith(('.mp4', '.webm', '.mov'))]
    return render_template('index.html', videos=video_files)

if __name__ == '__main__':
    app.run(debug=True)

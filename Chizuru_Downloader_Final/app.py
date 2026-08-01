from flask import Flask, request, jsonify, render_template, send_file
import yt_dlp
import os
import re
import tempfile

app = Flask(__name__)

DOWNLOAD_FOLDER = tempfile.gettempdir()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/download', methods=['POST'])
def get_video_link():
    data = request.get_json()
    raw_text = data.get('url')
    
    if not raw_text:
        return jsonify({"error": "Linknya mana? Chizuru bingung nih..."}), 400

    cari_link = re.search(r'(https?://[^\s]+)', raw_text)
    
    if cari_link:
        video_url = cari_link.group(1)
    else:
        return jsonify({"error": "Chizuru nggak nemu link yang bener di situ..."}), 400

    ydl_opts = {
        'format': 'best',
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(id)s.%(ext)s'), 
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            video_title = info.get('title', 'Video tanpa judul')
            filename = f"{info['id']}.{info['ext']}"
            
            return jsonify({
                "title": video_title,
                "download_url": f"/download_file/{filename}"
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download_file/<filename>')
def download_file(filename):
    path = os.path.join(DOWNLOAD_FOLDER, filename)
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

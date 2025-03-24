from flask import Flask, render_template, request, send_file, jsonify, send_from_directory
import os
from PyPDF2 import PdfMerger

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

uploaded_files = []  # Menyimpan daftar file yang diunggah

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['pdf']
    if file:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        uploaded_files.append(file.filename)
        return jsonify({"message": "File uploaded", "filename": file.filename, "files": uploaded_files})
    return jsonify({"error": "No file uploaded"}), 400

@app.route('/delete', methods=['POST'])
def delete_file():
    data = request.json
    filename = data.get("filename")
    if filename in uploaded_files:
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        uploaded_files.remove(filename)
        return jsonify({"message": "File deleted", "files": uploaded_files})
    return jsonify({"error": "File not found"}), 400

@app.route('/merge', methods=['POST'])
def merge_pdfs():
    data = request.json
    file_order = data.get("files", uploaded_files)  # Menggunakan urutan dari frontend

    if not file_order:
        return "No files uploaded", 400
    
    merger = PdfMerger()
    for filename in file_order:
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(file_path):
            merger.append(file_path)
    
    output_path = os.path.join(UPLOAD_FOLDER, 'merged.pdf')
    merger.write(output_path)
    merger.close()
    
    for filename in file_order:
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    uploaded_files.clear()
    
    return send_file(output_path, as_attachment=True)

@app.route('/uploads/<filename>')
def get_uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
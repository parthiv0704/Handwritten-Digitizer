import os
from flask import Flask, render_template, request, jsonify, send_file
from handwriting_summarizer import get_groq_client, process_image_with_model, encode_image, convert_pdf_to_images, enhance_resolution
import io
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    language = request.form.get('language', 'English')
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            client = get_groq_client()
            result = ""
            
            if filename.lower().endswith('.pdf'):
                images = convert_pdf_to_images(filepath)
                if not images:
                    return jsonify({'error': 'Could not extract images from PDF'}), 400
                
                full_result = []
                for i, image in enumerate(images):
                    # Process each page
                    temp_img_path = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_page_{i}.jpg")
                    image.save(temp_img_path, 'JPEG')
                    
                    # Enhance resolution
                    enhanced_path = enhance_resolution(temp_img_path)
                    
                    base64_image = encode_image(enhanced_path)
                    
                    page_result = process_image_with_model(client, base64_image, language)
                    full_result.append(f"## Page {i+1}\n{page_result}")
                    
                    # Cleanup temp image
                    # Cleanup temp image
                    if os.path.exists(temp_img_path):
                        os.remove(temp_img_path)
                    if os.path.exists(enhanced_path) and enhanced_path != temp_img_path:
                        os.remove(enhanced_path)
                
                result = "\n\n".join(full_result)
            else:
                # Enhance resolution
                enhanced_path = enhance_resolution(filepath)
                base64_image = encode_image(enhanced_path)
                result = process_image_with_model(client, base64_image, language)
            
            # Cleanup uploaded file
            if os.path.exists(filepath):
                os.remove(filepath)
            if 'enhanced_path' in locals() and os.path.exists(enhanced_path) and enhanced_path != filepath:
                os.remove(enhanced_path)
                
            return jsonify({'result': result})
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/download', methods=['POST'])
def download():
    content = request.form.get("content", "")
    file_format = request.form.get("format", "txt")
    
    buffer = io.BytesIO()
    mimetype = 'text/plain'
    filename = "result.txt"

    if file_format == 'json':
        filename = "result.json"
        json_content = json.dumps({"content": content}, indent=4)
        buffer.write(json_content.encode())
        mimetype = 'application/json'
        
    else: # txt
        buffer.write(content.encode())

    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype=mimetype)

if __name__ == '__main__':
    app.run(debug=True, port=5002)

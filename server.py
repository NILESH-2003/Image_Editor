from flask import Flask, request, jsonify, send_from_directory, render_template
from werkzeug.utils import secure_filename
import os
import cv2

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}


def compress_image(input_image_path, output_image_path, percent_reduction):
    if not os.path.exists(input_image_path):
        return None

    image = cv2.imread(input_image_path, cv2.IMREAD_UNCHANGED)
    width = int(image.shape[1] * (1 - percent_reduction / 100))
    height = int(image.shape[0] * (1 - percent_reduction / 100))
    dim = (width, height)
    resized_image = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
    cv2.imwrite(output_image_path, resized_image)

    return os.path.relpath(output_image_path, app.config['UPLOAD_FOLDER'])


def resize_image(input_image_path, output_image_path):
    if not os.path.exists(input_image_path):
        return None

    image = cv2.imread(input_image_path, cv2.IMREAD_UNCHANGED)
    resized_image = cv2.resize(image, (100, 100), interpolation=cv2.INTER_AREA)
    cv2.imwrite(output_image_path, resized_image)

    return os.path.relpath(output_image_path, app.config['UPLOAD_FOLDER'])


@app.route('/')
def index():
    return app.send_static_file('main.html')


# Route for index.html
@app.route('/index.html')
def serve_index():
    return app.send_static_file('index.html')


# Route for index1.html
@app.route('/index1.html')
def serve_index1():
    return app.send_static_file('index1.html')


# Route to handle image compression
@app.route('/compress', methods=['POST'])
def compress():
    if 'imageFile' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['imageFile']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file and file.filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']:
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'compressed_' + filename)

        # Ensure the directory exists before saving the file
        os.makedirs(os.path.dirname(input_path), exist_ok=True)

        file.save(input_path)

        compression_percentage = int(request.form['compressionPercentage'])

        # Perform image compression
        compressed_image_path = compress_image(input_path, output_path, compression_percentage)

        if compressed_image_path:
            return jsonify({
                'compressed_image': compressed_image_path,
                'download_link': compressed_image_path,
                'display_image': resize_image(compressed_image_path,
                                              os.path.join(app.config['UPLOAD_FOLDER'], 'display_' + filename)),
            })
        else:
            return jsonify({'error': 'Failed to compress image'})

    else:
        return jsonify({'error': 'File type not allowed'})


# Function to enhance image using OpenCV
def enhance_image(input_image_path, output_image_path, enhancement_factor):
    if not os.path.exists(input_image_path):
        return None

    image = cv2.imread(input_image_path, cv2.IMREAD_UNCHANGED)
    height, width = image.shape[:2]

    # Calculate new dimensions based on enhancement factor
    new_width = int(width * (1.35 + enhancement_factor / 100))
    new_height = int(height * (1.35 + enhancement_factor / 100))
    dim = (new_width, new_height)

    # Resize the image with interpolation for enhancement
    enhanced_image = cv2.resize(image, dim, interpolation=cv2.INTER_CUBIC)

    # Save the enhanced image
    cv2.imwrite(output_image_path, enhanced_image)

    # Return the path to the enhanced image relative to the static folder
    return os.path.relpath(output_image_path, app.config['UPLOAD_FOLDER'])


@app.route('/enhance', methods=['POST'])
def enhance():
    if 'imageFile' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['imageFile']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file and file.filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']:
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'enhanced_' + filename)

        # Ensure the directory exists before saving the file
        os.makedirs(os.path.dirname(input_path), exist_ok=True)

        file.save(input_path)

        enhancement_factor = float(request.form['enhancementFactor'])

        # Perform image enhancement
        enhanced_image_path = enhance_image(input_path, output_path, enhancement_factor)

        if enhanced_image_path:
            return jsonify({
                'enhanced_image': enhanced_image_path,
                'download_link': enhanced_image_path,
                'display_image': resize_image(enhanced_image_path,
                                              os.path.join(app.config['UPLOAD_FOLDER'], 'display_' + filename)),
            })
        else:
            return jsonify({'error': 'Failed to enhance image'})

    else:
        return jsonify({'error': 'File type not allowed'})


# Route to handle uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True)

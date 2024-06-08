from flask import Flask, render_template, request, send_from_directory
import numpy as np
import os
import json
# Import model-related functions and classes
import torch
import cv2
import faiss
from src.dataset_retrieval import Sketchy
from experiments.options import opts
from experiments.inference_script_with_faiss import load_model, prepare_image, prepare_image_from_interface, retrieve_images, process_images
from postprocess_image import segment_object, display_masks, multi_segmentation
from rem_background import remove_background
from single_sketch import process_image_from_file
from flask_cors import CORS
from io import BytesIO
from PIL import Image
import base64



app = Flask(__name__)   
CORS(app)
@app.route('/')
def index_view():
    return render_template('index.html')

ALLOWED_EXT = set(['jpg' , 'jpeg' , 'png'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXT

def generate_image_tensor(model, image_path, dataset_transforms, device):
    image = prepare_image(image_path, dataset_transforms)
    image_tensor = image.unsqueeze(0).to(device)
    with torch.no_grad():
        output = model(image_tensor, dtype='image')
    return output

# @app.route('/predict',methods=['GET','POST'])
# def predict():
#     if request.method == 'POST':
#         file = request.files['file']
#         if file and allowed_file(file.filename): #Checking file format
#             filename = file.filename
#             file_path = os.path.join('uploads', filename)
#             file.save(file_path)

#             user_image_path = file_path
#             #process_image_from_file(user_image_path)
#     folder_path = os.path.join('Saved_outputs')
#     image_paths = [os.path.join(folder_path, img) for img in os.listdir(folder_path) if img.endswith(('jpg', 'jpeg', 'png'))]
#     print(image_paths)
#     return render_template('predict.html', image_paths=image_paths)

@app.route("/predict", methods=["POST"])
def predict():
    # Get the image data from the request
    image_data = request.get_json()
    #print(image_data)
    if not image_data:
        return json.dumps({"error": "No image data provided"}), 400

    # Extract image data, format, and filename from the dictionary
    image_base64 = image_data.get('image', '')
    image_format = image_data.get('format', 'png')  # Default to png if format not specified
    filename = image_data.get('filename', 'Received_image')  # Default filename if not specified

    # Convert Base64 image data to bytes
    image_bytes = BytesIO(base64.b64decode(image_base64.split(',')[1]))
    # Open the image using PIL (Python Imaging Library)
    img = Image.open(image_bytes)

    # Convert the image to PNG format if necessary
    if image_format.lower() != 'png':
        img = img.convert('RGBA')  # Convert to RGBA format for PNG support

    # Save the image in the "Received_sketch" folder
    output_folder = os.path.join(os.getcwd(), 'Received_sketch')  # Path to the "Received_sketch" folder
    output_path = os.path.join(output_folder, f'{filename}.png')  # Output path for the PNG file

    # Check if the file already exists and delete it before saving the new image
    if os.path.exists(output_path):
        os.remove(output_path)
    img.save(output_path, format='PNG')  # Save the image as PNG format
    
    # file_path = os.path.join('Received_sketch', filename)

    user_image_path = 'Z:\work\Sketch_LVM-20240326T182047Z-001\Sketch_LVM\Received_sketch\Received_image.png'
    
    #process_image_from_file(user_image_path)
    
    return json.dumps({"message":'Image received'}), 200

@app.route('/serve-image/<filename>', methods=['GET'])
def serve_image(filename):
  return send_from_directory('',filename)


@app.route("/getimage", methods=["GET", "POST"])
def getimage():
    image_folder = "Saved_outputs"
    image_files = [f for f in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, f))]
    if image_files:
        images_data = []
        for image_file in image_files:
            with open(os.path.join(image_folder, image_file), "rb") as img_file:
                image_data = base64.b64encode(img_file.read()).decode("utf-8")
                images_data.append({"image": image_data})

        return json.dumps({"success": 1, "images": images_data})
    else:
        return json.dumps({"success": 0, "message": "No images found in the folder."})

if __name__ == '__main__':
    app.run(debug=True,use_reloader=False, port=8000)
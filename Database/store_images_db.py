import os
from pymongo import MongoClient
from PIL import Image
from io import BytesIO
import datetime

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['visualTeach_db']
images_collection = db['images']

# Path to the directory containing your images
images_directory = 'D:\\Sketchy\\photo'

# Iterate through each image file in the directory
for category_directory, dirs, files in os.walk(images_directory): 
    category = os.path.basename(category_directory)
    print(f'Processing folder {category} ')
    for filename in files:
        if filename.endswith(('.jpg', '.jpeg', '.png')):  # Adjust file extensions as needed
            image_path = os.path.join(category_directory, filename)

            # Read image file
            with open(image_path, 'rb') as image_file:
                image_data = BytesIO(image_file.read())

            # Create a PIL Image object
            pil_image = Image.open(image_data)

            # Convert PIL Image to bytes for storage in MongoDB
            image_bytes = BytesIO()
            pil_image.save(image_bytes, format='JPEG')  # Adjust format as needed

            # Image metadata
            image_metadata = {
                'filename': filename,
                'category': category,
                'filetype' : 'jpeg'    
            }   

            # Insert image data into MongoDB
            image_document = {
                'metadata': image_metadata,
                'image_data': image_bytes.getvalue()
            }

            images_collection.insert_one(image_document)

print("Dataset insertion completed.")

import os
from pymongo import MongoClient
from PIL import Image
from io import BytesIO

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['visualTeach_db']
images_collection = db['images']

def retrieve_image_by_filename(category, filename):
    # Query MongoDB to find the document with the matching filename
    query = {'metadata.filename': filename, 'metadata.category': category} 
    result = images_collection.find_one(query)

    if result:
        # Extract image data from the document
        image_data = result['image_data']

        # Create a PIL Image from the retrieved image data
        pil_image = Image.open(BytesIO(image_data))

        return pil_image
    else:
        print(f"No image found with filename: {filename}")
        return None

#MAIN
filename_to_retrieve = 'ext_114.jpg'
category_to_retrieve = 'airplane'
retrieved_image = retrieve_image_by_filename(category_to_retrieve, filename_to_retrieve)

if retrieved_image:
    # Display the retrieved image
    retrieved_image.show()
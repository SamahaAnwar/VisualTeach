import os
import rembg
import numpy as np
from PIL import Image

def remove_background(input_image):
    #removing background from images
    input_array = np.array(input_image)
    output_array = rembg.remove(input_array)
     # Create a PIL Image from the output array
    output_image = Image.fromarray(output_array).convert('RGB')
    return output_image

def prepare_images(folder_path):
    for subdir, dirs, files in os.walk(folder_path):
        print(f"Processing folder: {os.path.basename(subdir)}")
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_path = os.path.join(subdir, file)
                input_image = Image.open(image_path).convert('RGB')
                output_image = remove_background(input_image)
                # Save the output image

                parent_directory = '/home/edge/Desktop/Samaha/removed_backgrounds'
                path = os.path.join(parent_directory, os.path.basename(subdir))
                if not os.path.exists(path):
                    os.makedirs(path)

                output_path = os.path.join(path, file)
                output_image.save(f'{output_path}')

if __name__ == '__main__':
    directory = '/home/edge/Desktop/Samaha/Sketch_LVM/data/Sketchy/Sketchy/photo'
    prepare_images(directory)


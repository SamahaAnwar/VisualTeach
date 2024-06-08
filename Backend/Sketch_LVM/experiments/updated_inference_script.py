import os
from torchvision import transforms
from pytorch_lightning.callbacks import ModelCheckpoint
from PIL import Image
import faiss
import pickle

#Loading Model
from src.model_LN_prompt import Model
from src.dataset_retrieval import Sketchy
from experiments.options import opts

import matplotlib.pyplot as plt
import torchvision.transforms.functional as F
import torch

def load_model():
    # Load the model
    ckpt_path = os.path.join('saved_models', opts.exp_name, 'last.ckpt')
    if not os.path.exists(ckpt_path):
        print(f"{ckpt_path} does not exist!")

    model = Model.load_from_checkpoint(ckpt_path)
    model.eval()
    return model

def prepare_image(user_image_path, dataset_transforms):
     user_image = Image.open(user_image_path).convert('RGB')
     user_image_tensor = dataset_transforms(user_image)
     return user_image_tensor

def prepare_image_from_interface(image_path, dataset_transforms):
    # Load and transform the image
    image = Image.open(image_path)
    white_background = Image.new('RGBA', image.size, (255, 255, 255, 255))

    # Composite the original image onto the white background
    composite_img = Image.alpha_composite(white_background, image)
    composite_img = composite_img.resize((224, 224))
    composite_img = composite_img.convert('RGB')

    """plt.imshow(composite_img)
    plt.title('Sketch')
    plt.axis('off')
    plt.show()"""

    return dataset_transforms(composite_img)

def generate_image_tensor(model, image_path, dataset_transforms, device):
    # Prepare the image
    image = prepare_image(image_path, dataset_transforms)
    image_tensor = image.unsqueeze(0).to(device)  # Move tensor to the same device as the model

    # Evaluate the model
    with torch.no_grad():
        output = model(image_tensor, dtype='image')
    
    return output

def process_images(model, folder_path, dataset_transforms, device):
    dataset_tensors = {}
    model = model.to(device)  # Move model to GPU

    for subdir, dirs, files in os.walk(folder_path):
        print(f"Processing folder: {os.path.basename(subdir)}")
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_path = os.path.join(subdir, file)
                tensor = generate_image_tensor(model, image_path, dataset_transforms, device)
                dataset_tensors[image_path] = tensor.cpu()
                #dataset_tensors[image_path] = tensor.cpu().numpy()

    return dataset_tensors

#def retrieve_images(sketch, loader='dataset.pkl'):
def find_nearest_images(test_tensor, loader , top_k=5):
    distances = []
    for image_path, tensor in loader.items():
        tensor = torch.tensor(tensor)
        distance = torch.nn.functional.cosine_similarity(test_tensor, tensor, dim=1).item()
        distances.append((image_path, distance))

    # Sort based on distance and get top_k
    distances.sort(key=lambda x: x[1], reverse=True)  # Use reverse=True for similarity, False for distance
    nearest_images = [img[0] for img in distances[:top_k]]

    return nearest_images

def display_images(image_paths):
    fig, axes = plt.subplots(1, len(image_paths), figsize=(20, 10))
    for ax, image_path in zip(axes, image_paths):
        image = Image.open(image_path)
        ax.imshow(image)
        ax.axis('off')
    plt.show()  

if __name__ == '__main__':

    dataset_transforms = Sketchy.data_transform(opts)

    model = load_model()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    #Firstly checking if dataset.pkl file exists
    dataloader_path = os.path.join('dataloader', 'dataset.pkl')
    if not os.path.exists(dataloader_path):
        print(f"{dataloader_path} not found! Starting dataloader...")
        #combining all the data in a pickle file
        dataset_path = '/home/edge/Desktop/Samaha/Sketch_LVM/data/Sketchy/Sketchy/photo' 

        loader = process_images(model, dataset_path, dataset_transforms, device)
        #print(loader)
        #Saving the dataloader 
        #with open('dataset.pkl', 'wb') as file:
            #pickle.dump(loader, file)
        torch.save(loader, 'dataset.pkl')
        print('Successfully Saved dataset.pkl')
    else:
        loader = torch.load(f'{dataloader_path}')
        print('Dataloader successfully loaded!')

    #Starting Inference
    user_image_path = '/home/edge/Desktop/Samaha/Sketch_LVM/experiments/single_image/n03686924_4151-3.png'  
    sketch = prepare_image(user_image_path, dataset_transforms)
    sketch = sketch.unsqueeze(0)

    #torch.no_grad is used during inference as it halts compuatation of gradients
    image_paths = []
    with torch.no_grad():
        sk_feat = model(sketch)
        #print("Sketch Features: ", sk_feat)

        # Find nearest images in dataset
        nearest_image_paths = find_nearest_images(sk_feat, loader, top_k=10)
        print(nearest_image_paths)

        if nearest_image_paths:
            # Display the test image and nearest images
            display_images([user_image_path] + nearest_image_paths)
            print('Nearest images:', nearest_image_paths)
        else:
            print("No nearest images found.")
    

        
    

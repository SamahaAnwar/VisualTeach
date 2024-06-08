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

    return dataset_tensors

def display_images(D, I, image_paths, len_images):
    fig, axs = plt.subplots(1, len_images + 1, figsize=(15, 3))
    user_image = Image.open(user_image_path).convert('RGB')
    axs[0].imshow(user_image)
    for i in range(len_images):
        # Retrieve the image path and distance
        retrieved_image_path = image_paths[I[0, i]]
        retrieved_distance = D[0, i]

        # Load and display the retrieved image
        retrieved_image = Image.open(retrieved_image_path)
        axs[i+1].imshow(retrieved_image)
        axs[i+1].set_title(f"Dist: {retrieved_distance:.2f}")
        axs[i+1].axis('off')

    plt.show()


def retrieve_images(sketch, loader, len_images = 10):
    faiss_index = faiss.IndexFlatL2(512)  
    for image_path, image_tensor in loader.items():
        faiss_index.add(image_tensor.numpy()) #add the representation to index
        image_paths.append(image_path)

    D, I = faiss_index.search(sketch.numpy(), len_images)
    # Display the retrieved images
    display_images(D, I, image_paths, len_images)
    return D, I

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
        #Saving the dataloader 
        #with open('dataset.pkl', 'wb') as file:
            #pickle.dump(loader, file)
        torch.save(loader, 'dataset.pkl')
        print('Successfully Saved dataset.pkl')
    else:
        #with open(dataloader_path, 'rb') as file:
            #loader = pickle.load(file)
        loader = torch.load(f'{dataloader_path}')
        print('Dataloader successfully loaded!')

    #Starting Inference
    user_image_path = '/home/edge/Desktop/Samaha/Sketch_LVM/experiments/single_image/n12651611_11104-5.png'  
    sketch = prepare_image(user_image_path, dataset_transforms)
    sketch = sketch.unsqueeze(0)

    #torch.no_grad is used during inference as it halts compuatation of gradients
    image_paths = []
    with torch.no_grad():
        sk_feat = model(sketch)
        #print("Sketch Features: ", sk_feat)

        retrieve_images(sk_feat, loader, len_images=10)

        
    

        
    

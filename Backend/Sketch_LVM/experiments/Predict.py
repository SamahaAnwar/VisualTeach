import os
from torch.utils.data import DataLoader
from torchvision import transforms
from pytorch_lightning import Trainer
from pytorch_lightning.loggers import TensorBoardLogger
from pytorch_lightning.callbacks import ModelCheckpoint
from PIL import Image
import faiss

#Loading Model
from src.model_LN_prompt import Model
from src.dataset_retrieval import Sketchy
from experiments.options import opts

import matplotlib.pyplot as plt
import torchvision.transforms.functional as F
import torch

def prepare_image(image_path, dataset_transforms):
    # Load and transform the image
    image = Image.open(image_path)
    white_background = Image.new('RGBA', image.size, (255, 255, 255, 255))

    # Composite the original image onto the white background
    composite_img = Image.alpha_composite(white_background, image)
    composite_img = composite_img.resize((224, 224))
    composite_img = composite_img.convert('RGB')

    plt.imshow(composite_img)
    plt.title('Sketch')
    plt.axis('off')
    plt.show()

    return dataset_transforms(composite_img)

def denormalize(tensor, mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]):
    for t, m, s in zip(tensor, mean, std):
        t.mul_(s).add_(m)
    return tensor

def show_images(sketch, image, title, n):
    sketch = sketch.squeeze(0)
    sketch = F.to_pil_image(denormalize(sketch))

    plt.subplot(1, n + 1, 1)
    plt.axis('off')
    #plt.set_aspect('auto')
    plt.imshow(sketch)
    plt.title('Sketch')
    for i in range(n):
        n_image = image[i]
        image_pil = F.to_pil_image(denormalize(n_image))
        plt.subplot(1, n + 1, i+2)
        plt.axis('off')
        #plt.set_aspect('auto')
        plt.imshow(image_pil)
        plt.title(f'Image {i + 1}')
    
    plt.suptitle(title)
    plt.show()

if __name__ == '__main__':

    dataset_transforms = Sketchy.data_transform(opts)

    #Loading the Dataloader
    dataloader_path = os.path.join('dataloader', 'data.pkl')
    if not os.path.exists(dataloader_path):
        print(f"{dataloader_path} not found! Starting dataloader...")
        #Load the data
        dataset = Sketchy(opts, dataset_transforms, return_orig=False)
        loader = DataLoader(dataset=dataset, batch_size=600, num_workers=opts.workers)

        #Saving the dataloader 
        torch.save(loader, 'data.pkl')
    else:
        loader = torch.load(f'{dataloader_path}')

    # Load the model
    ckpt_path = os.path.join('saved_models', opts.exp_name, 'last.ckpt')
    if not os.path.exists(ckpt_path):
        print(f"{ckpt_path} does not exist!")

    model = Model.load_from_checkpoint(ckpt_path)
    
    # Initialize the trainer
    #trainer = Trainer(model = model)

    print('Beginning Predicting')
    #trainer.test(model, loader) #dataloader is being loaded here
    model.eval()
 

    # Testing with user input image
    user_image_path = '/home/edge/Desktop/Samaha/Sketch_LVM/experiments/single_image/n07739125_1478-3.png'  

    #Apply this code if the user input is NOT from the react interface
    user_image = Image.open(user_image_path).convert('RGB')
    user_image_tensor = dataset_transforms(user_image)
    
    # Apply the same transformations as in the dataset(Use this code if the user input is from the react interface)
    #user_image_tensor = prepare_image(user_image_path, dataset_transforms)

    # Add batch dimension
    user_image_tensor = user_image_tensor.unsqueeze(0)



    """faiss_index = faiss.IndexFlatL2(512)  
        for image_path, image_tensor in loader.items():
            faiss_index.add(image_tensor.numpy()) #add the representation to index
            image_paths.append(image_path)

        D, I = faiss_index.search(sk_feat.numpy(), 5)

        #visualizing the retrieved image
        print(I[0][1])"""
        
       

             

    
    """with torch.no_grad():
        for batch in loader:
            _, img_tensor, _, _ = batch[:4]
            # Forward pass
            sk_feat = model(user_image_tensor, dtype='sketch')
            img_feat = model(img_tensor, dtype='image')

            # Visualization
            n = 5  # Assuming you want to visualize 5 images from the test dataset
            show_images(user_image_tensor, img_tensor, 'User Input Image', n)
            #break"""

    print('Testing complete.')

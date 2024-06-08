import torch
import os
import cv2
import faiss
import matplotlib.pyplot as plt
import numpy as np
from src.dataset_retrieval import Sketchy
from experiments.options import opts

from experiments.inference_script_with_faiss import load_model, prepare_image, prepare_image_from_interface, retrieve_images, process_images
from postprocess_image import segment_object, display_masks, multi_segmentation
from rem_background import remove_background

"""def display_images():
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

    plt.show()"""

def display_image(img):
    img = np.array(img)
    img = img[:, : , ::-1]
    plt.axis('off')
    plt.imshow(img)
    plt.show()

def generate_image_tensor(model, image_path, dataset_transforms, device):
    # Prepare the image
    image = prepare_image(image_path, dataset_transforms)
    image_tensor = image.unsqueeze(0).to(device)  # Move tensor to the same device as the model

    # Evaluate the model
    with torch.no_grad():
        output = model(image_tensor, dtype='image')
    
    return output


def create_appended_dataloader(model, folder_path, dataset_transforms, device):
   dataset_tensors = {}
   model = model.to(device)  # Move model to GPU

   for subdir, dirs, files in os.walk(folder_path):
        print(f"Processing folder: {os.path.basename(subdir)}")
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_path = os.path.join(subdir, file)
                tensor = generate_image_tensor(model, image_path, dataset_transforms, device)
                dataset_tensors[(image_path, os.path.basename(subdir))] = tensor.cpu()

   return dataset_tensors

def retrieve_imgs_with_class(sketch, loader, len_images):
    faiss_index = faiss.IndexFlatL2(512)  
    for image_info, image_tensor in loader.items():
        image_path, image_class = image_info
        faiss_index.add(image_tensor.numpy()) #add the representation to index
        image_paths.append(image_path)
        image_classes.append(image_class)

    D, I = faiss_index.search(sketch.numpy(), len_images)
    # Postprocess the retrieved images
    return D, I
    
def get_classname(corresponding_classes, retrieved_images, i):
    img_class = retrieved_images[i][2]
    #checking the class name of object detection results
    detected_class= [k for k, v in corresponding_classes.items() if img_class in v]
    return detected_class

if __name__ == '__main__':

     dataset_transforms = Sketchy.data_transform(opts)
     #First taking image from interface 
     user_image_path = '/home/edge/Desktop/Samaha/Sketch_LVM/2024-03-07-102050.jpg'  
     sketch = prepare_image_from_interface(user_image_path, dataset_transforms)
     sketch = sketch.unsqueeze(0)

     #Loading the Model
     model = load_model()
     device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

     #checking if dataset.pkl file exists
     dataloader_path = os.path.join('dataloader', 'appended_dataset.pkl')
 
     if not os.path.exists(dataloader_path):
        print(f"{dataloader_path} not found! Starting dataloader...")
        #combining all the data in a pickle file
        dataset_path = '/home/edge/Desktop/Samaha/Sketch_LVM/data/Sketchy/Sketchy/photo' 

        loader = create_appended_dataloader(model, dataset_path, dataset_transforms, device)
        #Saving the dataloader 
        torch.save(loader, 'appended_dataset.pkl')
        print('Successfully Saved appended_dataset.pkl')
     else:
        loader = torch.load(f'{dataloader_path}')
        print('Dataloader successfully loaded!')

     #defining the length of images
     len_images = 7

     image_paths = []
     image_classes = []
     final_images = []
     with torch.no_grad():
        sk_feat = model(sketch)
        D, I = retrieve_imgs_with_class(sk_feat, loader, len_images)

     retrieved_images = []
     for i in range(len_images):
        # Retrieve the image path and distance
        retrieved_image_path = image_paths[I[0, i]]
        retrieved_distance = D[0, i]
        retrieved_class = image_classes[I[0, i]] 
        print(retrieved_image_path, retrieved_distance, retrieved_class)

        retrieved_images.append((retrieved_image_path, retrieved_distance, retrieved_class))

        #creating a dictionary of coco-sketchy classes
        corresponding_classes = {'bird':['chicken', 'parrot', 'duck', 'songbird', 'wading_bird', 'swan', 'seagull', 'owl'], 'cat':'cat', 
                                    'dog':'dog', 'sheep':'sheep', 'boat':'sailboat', 'apple':'apple', 'banana':'banana', 'airplane':['airplane', 
                                    'blimp', 'helicopter'], 'clock':'alarm_clock', 'bear':'bear', 'bicycle':'bicycle', 'car':'car_(sedan)', 
                                    'truck':'pickup_truck', 'chair':'chair', 'bed':'couch','couch':'couch', 'cow':'cow', 'bench':'bench', 'cup':'cup', 
                                    'elephant':'elephant', 'giraffe':'giraffe', 'horse':'horse', 'hot dog':'hot dog', 'knife':'knife', 
                                    'motorcycle':'motorcycle', 'mouse':'mouse', 'pizza':'pizza', 'tennis racket':'racket', 'scissors':'scissors', 
                                    'spoon':'spoon', 'teddy bear':'teddy bear', 'dining table':'table', 'zebra':'zebra', 'umbrella':'umbrella'}
        
        cmp_class = get_classname(corresponding_classes, retrieved_images, i)
        print("YOLO DETECTED CLASS:", cmp_class)

        #Starting the object detection and segmentation pipeline
        frame = cv2.imread(retrieved_image_path)
        classes, masks, input_boxes = segment_object(frame, device)
        if masks is not None:
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            #display_masks(image, masks, input_boxes)
            if cmp_class == []:
                #YOLO has detected an object but it is not in local dataset
                #we'll just remove the background of the image
                rmg_image = remove_background(frame)
                display_image(rmg_image)
                
            else:
                print(cmp_class)
                cmp_class = cmp_class[0]
                multi_segmentation(frame, masks, classes, print_class=cmp_class)
            #same_image_segmentation(masks)
        else:
            rmg_image = remove_background(frame)
            display_image(rmg_image)
            print("Exiting Code!")
     
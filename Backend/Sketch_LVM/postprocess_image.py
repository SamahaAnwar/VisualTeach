import ultralytics
from ultralytics import YOLO
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator, SamPredictor
import cv2
import numpy as np
import torch
import matplotlib.pyplot as plt

def load_sam(device):
    ckpt_path = '/home/edge/Desktop/Samaha/Sketch_LVM/SAM_Model/sam_vit_h_4b8939.pth'
    sam = sam_model_registry['vit_h'](checkpoint=ckpt_path)
    sam.to(device=device)
    predictor = SamPredictor(sam)
    return predictor

def show_mask(mask, ax, random_color=False):
    if random_color:
        color = np.concatenate([np.random.random(3), np.array([0.6])], axis=0)
    else:
        color = np.array([30/255, 144/255, 255/255, 0.6])
    h, w = mask.shape[-2:]
    mask_image = mask.reshape(h, w, 1) * color.reshape(1, 1, -1)
    ax.imshow(mask_image)

def show_points(coords, labels, ax, marker_size=375):
    pos_points = coords[labels==1]
    neg_points = coords[labels==0]
    ax.scatter(pos_points[:, 0], pos_points[:, 1], color='green', marker='*', s=marker_size, edgecolor='white', linewidth=1.25)
    ax.scatter(neg_points[:, 0], neg_points[:, 1], color='red', marker='*', s=marker_size, edgecolor='white', linewidth=1.25)

def show_box(box, ax):
    x0, y0 = box[0], box[1]
    w, h = box[2] - box[0], box[3] - box[1]
    ax.add_patch(plt.Rectangle((x0, y0), w, h, edgecolor='green', facecolor=(0,0,0,0), lw=2))

def display_masks(image, masks, input_boxes):
    plt.figure(figsize=(10, 10))
    plt.imshow(image)
    for mask in masks:
        show_mask(mask.cpu().numpy(), plt.gca(), random_color=True)
    
    for box in input_boxes:
        show_box(box.cpu().numpy(), plt.gca())
 
    plt.axis('off')
    plt.show()

#Same image for all segmented objects
def same_image_segmentation(masks):
    accumulated_mask = np.zeros_like(masks[0].cpu().numpy())

    # Accumulate binary masks
    for i, segmentation_mask in enumerate(masks):
        binary_mask = np.where(segmentation_mask.cpu().numpy() > 0.5, 1, 0)
        accumulated_mask += binary_mask.astype(bool)

    # Ensure values in the accumulated mask are binary (0 or 1)
    accumulated_mask = np.where(accumulated_mask > 0, 1, 0)

    # Overlay the accumulated mask on white
    white_background = np.ones_like(image) * 255
    segmented_image = white_background * (1 - accumulated_mask[..., np.newaxis]) + image * accumulated_mask[..., np.newaxis] 
    plt.figure(figsize=(12, 4))

    new_image = segmented_image.astype(np.uint8)
    new_image = new_image.squeeze()
    plt.imshow(new_image)
    plt.title(f'Segmented Image')
    plt.axis('off')

    plt.show()

 #Different images for each segmented object
def multi_segmentation(frame, masks, classes, print_class):
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    for i, segmentation_mask in enumerate(masks):
        binary_mask = np.where(segmentation_mask.cpu().numpy() > 0.5, 1, 0)

        white_background = np.ones_like(image) * 255

        new_image = white_background * (1 - binary_mask[..., np.newaxis]) + image * binary_mask[..., np.newaxis]

        # Display the resulting image for each mask
        if classes[i] == print_class:
            plt.figure(figsize=(12, 4))

            new_image = new_image.astype(np.uint8)
            new_image = new_image.squeeze()
            plt.imshow(new_image)
            plt.title(f'Segmented Image {i + 1}')
            plt.axis('off')

            plt.show()

def get_detections(model, frame):
    obj_detections = model.predict(
        source= frame,
        conf=0.25
    )
    return obj_detections


def segment_object(frame, device):
    #First Loading the YOLOv8 Model for object detections
     model = YOLO('yolov8n.pt')
     obj_detections = get_detections(model, frame)
     #getting the bounding boxes for objects in the image
     for i, obj in enumerate(obj_detections):
        boxes = obj.boxes
    
     bboxes=boxes.xyxy.tolist()
     if not bboxes:
         print("There are no detections!")
         return None, None, None

    #storing names of ids
     classes = []
     for i in range(len(boxes.cls)):
        for obj in obj_detections:
            class_name = obj.names[boxes.cls[i].item()]
            classes.append(class_name)

     print(classes)
     image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
     predictor = load_sam(device)
     predictor.set_image(image)

     input_boxes = []
     for bbox in bboxes:
        input_box = np.array(bbox)
        input_boxes.append(input_box)

     input_boxes = torch.tensor(input_boxes, device=predictor.device)
     transformed_boxes = predictor.transform.apply_boxes_torch(input_boxes, image.shape[:2])

     masks, _, _ = predictor.predict_torch(
        point_coords=None,
        point_labels=None,
        boxes= transformed_boxes,
        multimask_output=False,
    )  

     return classes, masks, input_boxes

if __name__ == '__main__':
    
    device = torch.device("cuda:0") if torch.cuda.is_available() else torch.device("cpu")
    frame = cv2.imread('/home/edge/Desktop/Samaha/Sketchy/photo/helicopter/ext_135.jpg')
   
    classes, masks, input_boxes = segment_object(frame, device)
    if masks is not None:
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        display_masks(image, masks, input_boxes)
        multi_segmentation(masks, classes, print_class='airplane')
        #same_image_segmentation(masks)
    else:
        print("Exiting Code!")
    
    



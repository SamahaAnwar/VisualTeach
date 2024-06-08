import os
import glob
from torch.utils.data import DataLoader
from torchvision import transforms
from pytorch_lightning import Trainer
from pytorch_lightning.loggers import TensorBoardLogger
from pytorch_lightning.callbacks import ModelCheckpoint

#Loading Model
from src.model_LN_prompt import Model
from src.dataset_retrieval import Sketchy
from experiments.options import opts

import matplotlib.pyplot as plt
import torchvision.transforms.functional as F
import torch

def denormalize(tensor, mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]):
    for t, m, s in zip(tensor, mean, std):
        t.mul_(s).add_(m)
    return tensor

def show_images(sketch, image, title, n):
    sketch = F.to_pil_image(denormalize(sketch))

    plt.subplot(1, n + 1, 1)
    plt.imshow(sketch)
    plt.title('Sketch')
    for i in range(n):
        n_image = image[i]
        image_pil = F.to_pil_image(denormalize(n_image))
        plt.subplot(1, n + 1, i+2)
        plt.imshow(image_pil)
        plt.title('Image')
    
    plt.suptitle(title)
    plt.show()

if __name__ == '__main__':
    dataset_transforms = Sketchy.data_transform(opts)

    test_dataset = Sketchy(opts, dataset_transforms, mode='test', return_orig=False)
    test_loader = DataLoader(dataset=test_dataset, batch_size=opts.batch_size, num_workers=opts.workers)

    ckpt_path = os.path.join('saved_models', opts.exp_name, 'last.ckpt')
    if not os.path.exists(ckpt_path):
        print(f"{ckpt_path} does not exist!")
        
    model = Model.load_from_checkpoint(ckpt_path)
    
    trainer = Trainer(gpus=-1)

    print('Beginning testing...')
    #trainer.test(model, test_dataloader=test_loader)
    trainer.test(model, test_loader)

    model.eval()

    with torch.no_grad():
        for batch_idx, batch in enumerate(test_loader):
            sk_tensor, img_tensor, _, _ = batch[:4]
            
            # Forward pass
            sk_feat = model(sk_tensor, dtype='sketch')
            img_feat = model(img_tensor, dtype='image')

            # Visualization
            #show_images(sk_tensor[0], img_tensor[0], f'Batch {batch_idx + 1}')\
            n = 5
            show_images(sk_tensor[2], img_tensor, f'Batch {batch_idx + 1}', n)

    print('Testing complete.')
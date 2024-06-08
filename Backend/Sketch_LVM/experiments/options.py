import argparse

parser = argparse.ArgumentParser(description='Sketch-based OD')

parser.add_argument('--exp_name', type=str, default='LN_prompt')

# --------------------
# DataLoader Options
# --------------------

# Path to 'Sketchy' folder holding Sketch_extended dataset. It should have 2 folders named 'sketch' and 'photo'.
parser.add_argument('--data_dir', type=str, default='/home/edge/Desktop/Samaha/Sketch_LVM/data/Sketchy/Sketchy') 
parser.add_argument('--max_size', type=int, default=224)
parser.add_argument('--nclass', type=int, default=10)
parser.add_argument('--data_split', type=float, default=-1.0)

# ----------------------
# Training Params
# ----------------------

parser.add_argument('--clip_lr', type=float, default=1e-4)
parser.add_argument('--clip_LN_lr', type=float, default=1e-6)
parser.add_argument('--prompt_lr', type=float, default=1e-4)
parser.add_argument('--linear_lr', type=float, default=1e-4)
parser.add_argument('--batch_size', type=int, default=192)
parser.add_argument('--workers', type=int, default=128)

# ----------------------
# ViT Prompt Parameters
# ----------------------
parser.add_argument('--prompt_dim', type=int, default=768)
parser.add_argument('--n_prompts', type=int, default=3)

#=====================================================
# ----------------------
# Testing Params
# ----------------------

# Path to the folder holding the test dataset. It should have similar structure as the training dataset.
parser.add_argument('--test_data_dir', type=str, default='/home/edge/Desktop/Samaha/Sketch_LVM/data/Sketchy/Sketchy')

# Path to the trained model checkpoint for testing.
parser.add_argument('--trained_model_path', type=str, default='/home/edge/Desktop/Samaha/Sketch_LVM/saved_models/LN_prompt/last.ckpt')

# Set the batch size for testing.
parser.add_argument('--test_batch_size', type=int, default=64)

#======================================================

opts = parser.parse_args()

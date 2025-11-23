"""
Script để push dataset tiếng Việt lên Hugging Face Hub
"""

import json
from pathlib import Path
from PIL import Image
from datasets import Dataset, DatasetDict, Image as HFImage
from huggingface_hub import HfApi, login, whoami
import argparse
import os

def load_dataset_from_directory(dataset_dir: str):
    """Load dataset từ thư mục local và convert sang Hugging Face Dataset format"""
    dataset_path = Path(dataset_dir)
    metadata_path = dataset_path / "metadata" / "metadata.json"
    images_dir = dataset_path / "images"
    
    if not metadata_path.exists():
        raise FileNotFoundError(f"Metadata file not found: {metadata_path}")
    
    if not images_dir.exists():
        raise FileNotFoundError(f"Images directory not found: {images_dir}")
    
    print(f"Loading metadata from {metadata_path}...")
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    print(f"Found {len(metadata)} images in metadata")
    
    # Load images và tạo dataset
    data = {
        "image": [],
        "text": [],
        "prompt": [],
        "image_id": [],
        "width": [],
        "height": [],
        "font_size": [],
        "num_lines": [],
        "rotation_angle": [],
        "orientation": []
    }
    
    print("Loading images...")
    for i, meta in enumerate(metadata):
        # Load image
        img_path = dataset_path / meta['image_path']
        
        if not img_path.exists():
            print(f"Warning: Image not found: {img_path}, skipping...")
            continue
        
        try:
            # Load image as PIL Image
            img = Image.open(img_path)
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            data["image"].append(img)
            data["text"].append(meta['text'])
            data["prompt"].append(meta.get('prompt', ''))
            data["image_id"].append(meta.get('image_id', i))
            data["width"].append(meta.get('width', img.width))
            data["height"].append(meta.get('height', img.height))
            data["font_size"].append(meta.get('font_size', 0))
            data["num_lines"].append(meta.get('num_lines', 1))
            data["rotation_angle"].append(meta.get('rotation_angle', 0))
            data["orientation"].append(meta.get('orientation', 'horizontal'))
            
            if (i + 1) % 100 == 0:
                print(f"Loaded {i + 1}/{len(metadata)} images...")
        except Exception as e:
            print(f"Error loading image {img_path}: {e}, skipping...")
            continue
    
    print(f"Successfully loaded {len(data['image'])} images")
    
    # Create Hugging Face Dataset
    print("Creating Hugging Face Dataset...")
    dataset = Dataset.from_dict(data)
    
    # Cast image column to Image type
    dataset = dataset.cast_column("image", HFImage())
    
    return dataset


def push_to_hub(dataset: Dataset, repo_id: str, private: bool = False, 
                split: str = None, token: str = None):
    """Push dataset lên Hugging Face Hub"""
    
    print(f"\nPushing dataset to Hugging Face Hub: {repo_id}")
    print(f"Private: {private}")
    
    # Determine which token to use (priority: argument > environment variable)
    hf_token = token or os.getenv("HF_TOKEN")
    
    # Login if token provided
    api = HfApi()
    if hf_token:
        try:
            print("Authenticating with Hugging Face...")
            login(token=hf_token)
            # Verify user identity
            user_info = whoami(token=hf_token)
            username = user_info.get("name", "unknown")
            print(f"✅ Authentication successful (logged in as: {username})")
            
            # Verify username matches repo namespace
            repo_namespace = repo_id.split("/")[0]
            if username != repo_namespace:
                print(f"⚠️  Warning: Repository namespace '{repo_namespace}' doesn't match your username '{username}'")
                print(f"   This might cause permission errors. Make sure you have access to create datasets under '{repo_namespace}'")
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            print("\nPlease check your token:")
            print("1. Get a token from https://huggingface.co/settings/tokens")
            print("2. Make sure it's a WRITE token (not read-only)")
            print("3. Set it as environment variable: $env:HF_TOKEN='your_token_here' (PowerShell)")
            print("   Or pass it via command line: --token your_token_here")
            raise
    else:
        print("No token provided. Attempting interactive login...")
        try:
            login()
            user_info = whoami()
            username = user_info.get("name", "unknown")
            print(f"✅ Logged in as: {username}")
        except Exception as e:
            print(f"❌ Login failed: {e}")
            print("\nPlease provide a token:")
            print("1. Get a token from https://huggingface.co/settings/tokens")
            print("2. Make sure it's a WRITE token (not read-only)")
            print("3. Set it as environment variable: $env:HF_TOKEN='your_token_here' (PowerShell)")
            print("   Or pass it via command line: --token your_token_here")
            raise
    
    # Push to hub
    try:
        print("\nUploading dataset to Hugging Face Hub...")
        
        # Try to create repository first if it doesn't exist
        try:
            api.dataset_info(repo_id, token=hf_token)
            print(f"Repository {repo_id} already exists")
        except Exception:
            print(f"Repository {repo_id} doesn't exist, creating it...")
            try:
                api.create_repo(
                    repo_id=repo_id,
                    repo_type="dataset",
                    private=private,
                    token=hf_token,
                    exist_ok=True
                )
                print(f"✅ Repository created successfully")
            except Exception as create_error:
                error_msg = str(create_error)
                if "403" in error_msg or "Forbidden" in error_msg:
                    print(f"\n❌ Permission denied: {error_msg}")
                    print("\nPossible solutions:")
                    print("1. Make sure your token has WRITE permissions (not read-only)")
                    print("2. Verify the repository namespace matches your Hugging Face username")
                    print("3. Create the repository manually at: https://huggingface.co/new-dataset")
                    print("4. Check that your token is valid and hasn't expired")
                raise
        
        # Push dataset
        if split:
            # Create DatasetDict with split
            dataset_dict = DatasetDict({split: dataset})
            dataset_dict.push_to_hub(repo_id, private=private, token=hf_token)
        else:
            dataset.push_to_hub(repo_id, private=private, token=hf_token)
        
        print(f"\n✅ Successfully pushed dataset to: https://huggingface.co/datasets/{repo_id}")
    except Exception as e:
        error_msg = str(e)
        if "403" in error_msg or "Forbidden" in error_msg:
            print(f"\n❌ Permission denied: {error_msg}")
            print("\nPossible solutions:")
            print("1. Make sure your token has WRITE permissions (not read-only)")
            print("   Get a new token at: https://huggingface.co/settings/tokens")
            print("2. Verify the repository namespace matches your Hugging Face username")
            print("3. Create the repository manually at: https://huggingface.co/new-dataset")
            print("4. Check that your token is valid and hasn't expired")
        else:
            print(f"❌ Failed to push dataset: {e}")
        raise


def main():
    parser = argparse.ArgumentParser(description="Push Vietnamese image-text dataset to Hugging Face Hub")
    parser.add_argument("--dataset_dir", type=str, default="vietnamese_dataset",
                       help="Thư mục dataset (default: vietnamese_dataset)")
    parser.add_argument("--repo_id", type=str, required=True,
                       help="Hugging Face repository ID (e.g., 'username/dataset-name')")
    parser.add_argument("--private", action="store_true",
                       help="Tạo private dataset (default: public)")
    parser.add_argument("--split", type=str, default=None,
                       help="Tên split cho dataset (e.g., 'train', 'test'). Nếu không có, push trực tiếp")
    parser.add_argument("--token", type=str, default=None,
                       help="Hugging Face token (hoặc set HF_TOKEN environment variable)")
    
    args = parser.parse_args()
    
    # Load dataset
    dataset = load_dataset_from_directory(args.dataset_dir)
    
    # Push to hub
    push_to_hub(
        dataset=dataset,
        repo_id=args.repo_id,
        private=args.private,
        split=args.split,
        token=args.token
    )


if __name__ == "__main__":
    main()


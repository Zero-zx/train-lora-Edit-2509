"""
Script để chuẩn bị dataset từ vietnamese_dataset cho Qwen-Image-Edit-2509 training
- Tạo control images (ảnh nền trắng không có text)
- Tạo caption files cho mỗi ảnh
- Tạo file config TOML
"""

import json
import os
from pathlib import Path
from PIL import Image
import argparse

def create_control_images(metadata_path: str, images_dir: str, controls_dir: str):
    """Tạo control images (ảnh nền trắng) từ metadata"""
    # Đọc metadata
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    # Tạo thư mục control images
    controls_path = Path(controls_dir)
    controls_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Creating {len(metadata)} control images...")
    
    for i, item in enumerate(metadata):
        # Lấy kích thước từ metadata
        width = item.get('width', 1328)
        height = item.get('height', 1328)
        
        # Tạo ảnh nền trắng
        control_img = Image.new('RGB', (width, height), (255, 255, 255))
        
        # Lưu control image với cùng tên file
        image_filename = Path(item['image_path']).name
        control_path = controls_path / image_filename
        control_img.save(control_path, "PNG")
        
        if (i + 1) % 100 == 0:
            print(f"Created {i + 1}/{len(metadata)} control images...")
    
    print(f"✓ Control images created in: {controls_dir}")

def create_caption_files(metadata_path: str, images_dir: str):
    """Tạo caption files (.txt) cho mỗi ảnh - lưu cùng thư mục với images"""
    # Đọc metadata
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    images_path = Path(images_dir)
    
    print(f"Creating {len(metadata)} caption files...")
    
    for i, item in enumerate(metadata):
        # Tạo caption mô tả việc thêm text vào ảnh
        text = item['text']
        caption = f"Add Vietnamese text \"{text}\" to the white background image. The text should be black and centered."
        
        # Lấy tên file ảnh (không có extension)
        image_filename = Path(item['image_path']).stem
        caption_path = images_path / f"{image_filename}.txt"
        
        # Lưu caption (cùng thư mục với ảnh)
        with open(caption_path, 'w', encoding='utf-8') as f:
            f.write(caption)
        
        if (i + 1) % 100 == 0:
            print(f"Created {i + 1}/{len(metadata)} caption files...")
    
    print(f"✓ Caption files created in: {images_dir}")

def create_toml_config(
    output_path: str,
    image_dir: str,
    control_dir: str,
    cache_dir: str,
    resolution: list = [960, 544]
):
    """Tạo file config TOML cho Qwen-Image-Edit-2509"""
    # Chuyển đường dẫn Windows sang format phù hợp
    def format_path(path_str: str) -> str:
        # Chuyển backslash thành forward slash cho TOML
        return path_str.replace('\\', '/')
    
    config_content = f"""# Dataset configuration for Qwen-Image-Edit-2509 LoRA training
# Generated automatically

[general]
resolution = {resolution}
caption_extension = ".txt"
batch_size = 1
enable_bucket = true
bucket_no_upscale = false

[[datasets]]
image_directory = "{format_path(image_dir)}"
control_directory = "{format_path(control_dir)}"
cache_directory = "{format_path(cache_dir)}"
qwen_image_edit_control_resolution = [1024, 1024]  # Recommended: resize control to 1M pixels
num_repeats = 1
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print(f"✓ TOML config created: {output_path}")

def main():
    parser = argparse.ArgumentParser(
        description="Chuẩn bị dataset từ vietnamese_dataset cho Qwen-Image-Edit-2509 training"
    )
    parser.add_argument(
        "--dataset_dir",
        type=str,
        default="vietnamese_dataset",
        help="Thư mục dataset gốc (default: vietnamese_dataset)"
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="vietnamese_dataset_qwen_edit",
        help="Thư mục output (default: vietnamese_dataset_qwen_edit)"
    )
    parser.add_argument(
        "--resolution",
        type=int,
        nargs=2,
        default=[960, 544],
        help="Resolution [width height] (default: 960 544 for RTX 3090, use 1328 1328 for higher VRAM)"
    )
    
    args = parser.parse_args()
    
    dataset_dir = Path(args.dataset_dir)
    output_dir = Path(args.output_dir)
    
    # Đường dẫn các thư mục
    metadata_path = dataset_dir / "metadata" / "metadata.json"
    images_dir = dataset_dir / "images"
    
    # Thư mục output
    output_images_dir = output_dir / "images"
    output_controls_dir = output_dir / "controls"
    output_cache_dir = output_dir / "cache"
    config_path = output_dir / "dataset_config.toml"
    
    # Tạo thư mục output
    output_dir.mkdir(parents=True, exist_ok=True)
    output_images_dir.mkdir(parents=True, exist_ok=True)
    output_cache_dir.mkdir(parents=True, exist_ok=True)
    
    # Kiểm tra metadata file
    if not metadata_path.exists():
        print(f"❌ Error: Metadata file not found: {metadata_path}")
        return
    
    # Copy images từ dataset gốc (hoặc dùng symlink để tiết kiệm dung lượng)
    print("Setting up images directory...")
    if not output_images_dir.exists() or len(list(output_images_dir.glob("*.png"))) == 0:
        # Copy hoặc symlink images
        import shutil
        for img_file in images_dir.glob("*.png"):
            shutil.copy2(img_file, output_images_dir / img_file.name)
        print(f"✓ Images copied to: {output_images_dir}")
    else:
        print(f"✓ Images directory already exists: {output_images_dir}")
    
    # Tạo control images
    create_control_images(
        str(metadata_path),
        str(images_dir),
        str(output_controls_dir)
    )
    
    # Tạo caption files (cùng thư mục với images)
    create_caption_files(
        str(metadata_path),
        str(output_images_dir)
    )
    
    # Tạo TOML config
    # Sử dụng đường dẫn tuyệt đối hoặc tương đối
    image_dir_abs = str(output_images_dir.resolve())
    control_dir_abs = str(output_controls_dir.resolve())
    cache_dir_abs = str(output_cache_dir.resolve())
    
    create_toml_config(
        str(config_path),
        image_dir_abs,
        control_dir_abs,
        cache_dir_abs,
        str(output_images_dir),  # Captions cùng thư mục với images
        args.resolution
    )
    
    print("\n" + "="*60)
    print("✓ Dataset preparation completed!")
    print("="*60)
    print(f"\nDataset structure:")
    print(f"  - Images (target): {output_images_dir}")
    print(f"  - Controls (source): {output_controls_dir}")
    print(f"  - Captions: {output_images_dir} (same as images)")
    print(f"  - Cache: {output_cache_dir}")
    print(f"  - Config: {config_path}")
    print(f"\nNext steps:")
    print(f"  1. Review the config file: {config_path}")
    print(f"  2. Run latent caching:")
    print(f"     python src/musubi_tuner/qwen_image_cache_latents.py \\")
    print(f"       --dataset_config {config_path} \\")
    print(f"       --vae path/to/vae_model \\")
    print(f"       --edit_plus  # ← Flag cho Edit-2509")
    print(f"  3. Run text encoder caching:")
    print(f"     python src/musubi_tuner/qwen_image_cache_text_encoder_outputs.py \\")
    print(f"       --dataset_config {config_path} \\")
    print(f"       --text_encoder path/to/text_encoder \\")
    print(f"       --edit_plus \\  # ← Flag cho Edit-2509")
    print(f"       --batch_size 1")
    print(f"  4. Start training with --edit_plus flag (see README for full command)")

if __name__ == "__main__":
    main()


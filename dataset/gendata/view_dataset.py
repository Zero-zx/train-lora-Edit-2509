"""
Script để xem và kiểm tra dataset tiếng Việt đã tạo
"""

import json
from pathlib import Path
from PIL import Image
import argparse

def view_dataset(dataset_dir: str, num_samples: int = 10):
    """Xem một số mẫu từ dataset"""
    dataset_path = Path(dataset_dir)
    metadata_path = dataset_path / "metadata" / "metadata.json"
    images_dir = dataset_path / "images"
    
    if not metadata_path.exists():
        print(f"Không tìm thấy metadata tại: {metadata_path}")
        return
    
    # Load metadata
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    print(f"Tổng số ảnh trong dataset: {len(metadata)}")
    print(f"\nHiển thị {min(num_samples, len(metadata))} mẫu đầu tiên:\n")
    print("=" * 80)
    
    for i, meta in enumerate(metadata[:num_samples]):
        print(f"\nẢnh #{i+1}:")
        print(f"  ID: {meta['image_id']}")
        print(f"  Text: {meta['text']}")
        print(f"  Kích thước: {meta['width']}x{meta['height']}")
        
        # Hiển thị ảnh nếu có
        img_path = dataset_path / meta['image_path']
        if img_path.exists():
            try:
                img = Image.open(img_path)
                print(f"  Đường dẫn: {img_path}")
                print(f"  Format: {img.format}, Mode: {img.mode}")
            except Exception as e:
                print(f"  Lỗi khi mở ảnh: {e}")
        else:
            print(f"  ⚠️ Ảnh không tồn tại: {img_path}")
        
        print("-" * 80)
    
    # Thống kê
    print(f"\n📊 Thống kê:")
    print(f"  - Tổng số ảnh: {len(metadata)}")
    
    # Đếm độ dài text
    text_lengths = [len(meta['text']) for meta in metadata]
    print(f"  - Độ dài text trung bình: {sum(text_lengths) / len(text_lengths):.1f} ký tự")
    print(f"  - Text ngắn nhất: {min(text_lengths)} ký tự")
    print(f"  - Text dài nhất: {max(text_lengths)} ký tự")
    
    # Đếm số từ unique
    unique_texts = set(meta['text'] for meta in metadata)
    print(f"  - Số text unique: {len(unique_texts)}")
    print(f"  - Tỷ lệ duplicate: {(1 - len(unique_texts) / len(metadata)) * 100:.1f}%")


def main():
    parser = argparse.ArgumentParser(description="Xem dataset ảnh-văn bản tiếng Việt")
    parser.add_argument("--dataset_dir", type=str, default="vietnamese_dataset",
                       help="Thư mục dataset (default: vietnamese_dataset)")
    parser.add_argument("--num_samples", type=int, default=10,
                       help="Số mẫu để hiển thị (default: 10)")
    
    args = parser.parse_args()
    view_dataset(args.dataset_dir, args.num_samples)


if __name__ == "__main__":
    main()


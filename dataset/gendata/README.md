# Vietnamese Image-Text Pairs Dataset Generator

Project này tạo dataset ảnh-văn bản tiếng Việt tương tự như [image-text-pairs-ja-cc0](https://huggingface.co/datasets/alfredplpl/image-text-pairs-ja-cc0) của Hugging Face.

## Mô tả

Script này tạo các ảnh synthetic với **prompt sinh ảnh tiếng Việt** được render trên ảnh. Các prompt này là những yêu cầu thực tế mà người dùng thường sử dụng khi gen ảnh với các mô hình như DALL-E, Midjourney, Stable Diffusion, v.v.

Dataset này có thể được sử dụng để:
- Training các mô hình vision-language cho tiếng Việt
- Fine-tuning các mô hình text-to-image
- Nghiên cứu về image generation với prompt tiếng Việt

## Tính năng

- ✅ Tạo ảnh với prompt sinh ảnh tiếng Việt (Unicode support)
- ✅ **3 loại prompt**: ngắn (từ/cụm từ), trung bình (câu mô tả), chi tiết (mô tả đầy đủ với style)
- ✅ **80+ prompt mẫu** phản ánh yêu cầu thực tế của người dùng
- ✅ Background đa dạng với nhiều pattern
- ✅ Tự động điều chỉnh font size và màu sắc
- ✅ Metadata đầy đủ cho mỗi ảnh
- ✅ Export dạng JSON và text file

## Setup

1. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

2. Tạo dataset:
```bash
python generate_vietnamese_dataset.py --num_images 1000
```

## Usage

### Tạo dataset cơ bản
```bash
python generate_vietnamese_dataset.py
```

### Tạo dataset với tùy chọn
```bash
python generate_vietnamese_dataset.py \
    --num_images 5000 \
    --output_dir my_vietnamese_dataset \
    --width 512 \
    --height 512 \
    --text_source mixed
```

### Xem dataset đã tạo
```bash
python view_dataset.py --dataset_dir vietnamese_dataset --num_samples 20
```

## Tham số

- `--num_images`: Số lượng ảnh cần tạo (default: 1000)
- `--output_dir`: Thư mục lưu dataset (default: vietnamese_dataset)
- `--width`: Chiều rộng ảnh (default: 512)
- `--height`: Chiều cao ảnh (default: 512)
- `--text_source`: Nguồn prompt - `words` (ngắn), `phrases` (trung bình), `sentences` (chi tiết), hoặc `mixed` (default: mixed)

## Cấu trúc Dataset

```
vietnamese_dataset/
├── images/
│   ├── image_000000.png
│   ├── image_000001.png
│   └── ...
└── metadata/
    ├── metadata.json      # Metadata đầy đủ cho tất cả ảnh
    └── texts.txt          # Danh sách prompt (một dòng một prompt)
```

## Ví dụ Prompt

### Prompt ngắn (words):
- "Mặt trời mọc"
- "Hoàng hôn"
- "Con mèo dễ thương"
- "Phong cảnh đẹp"

### Prompt trung bình (phrases):
- "Một con mèo dễ thương đang nằm trên cỏ xanh dưới ánh nắng mặt trời"
- "Hoàng hôn đẹp trên biển với màu cam và đỏ rực rỡ"
- "Rừng mưa nhiệt đới với cây cối xanh tươi và ánh sáng xuyên qua tán lá"

### Prompt chi tiết (sentences):
- "Một bức tranh phong cảnh hoàng hôn trên biển, màu cam và đỏ rực rỡ phản chiếu trên mặt nước, phong cách realistic với độ chi tiết cao, 4K, ánh sáng tự nhiên"
- "Con mèo dễ thương màu cam đang nằm trên cỏ xanh, ánh nắng mặt trời chiếu xuống tạo bóng đẹp, phong cách nhiếp ảnh chuyên nghiệp, độ sâu trường ảnh nông"


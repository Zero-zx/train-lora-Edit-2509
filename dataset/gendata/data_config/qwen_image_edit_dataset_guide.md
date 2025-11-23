# Hướng dẫn Config Dataset cho Qwen Image Edit LoRA Training

## Tổng quan

Để train LoRA cho Qwen Image Edit, bạn cần chuẩn bị dataset với **2 loại ảnh**:
- **Ảnh mục tiêu** (target images): Ảnh sau khi chỉnh sửa - đây là kết quả bạn muốn model học
- **Ảnh điều khiển** (control images): Ảnh gốc - điểm bắt đầu để chỉnh sửa

## Cấu trúc thư mục

```
dataset/
├── images/          # Ảnh mục tiêu (sau khi edit)
│   ├── image1.jpg
│   ├── image1.txt  # Caption cho image1
│   ├── image2.jpg
│   └── image2.txt
└── controls/        # Ảnh điều khiển (ảnh gốc)
    ├── image1.png   # Cùng tên với ảnh mục tiêu
    └── image2.png
```

**Lưu ý quan trọng:**
- Ảnh mục tiêu và ảnh điều khiển phải **cùng tên file** (có thể khác extension)
- Caption file đặt trong thư mục `images/`

## Cấu hình TOML

### Cách 1: Sử dụng Caption Text Files (Đơn giản nhất)

Tạo file `dataset_config.toml`:

```toml
[general]
resolution = [1024, 1024]      # Độ phân giải training
caption_extension = ".txt"      # Extension của file caption
batch_size = 1
enable_bucket = true
bucket_no_upscale = false

[[datasets]]
image_directory = "/path/to/images"           # Thư mục ảnh mục tiêu
control_directory = "/path/to/controls"       # Thư mục ảnh điều khiển
cache_directory = "/path/to/cache"           # Thư mục cache (nên đặt riêng)
qwen_image_edit_control_resolution = [1024, 1024]  # ⭐ QUAN TRỌNG
num_repeats = 1
```

### Cách 2: Sử dụng Metadata JSONL File

Tạo file `dataset_config.toml`:

```toml
[general]
resolution = [1024, 1024]
batch_size = 1
enable_bucket = true
bucket_no_upscale = false

[[datasets]]
image_jsonl_file = "/path/to/metadata.jsonl"
cache_directory = "/path/to/cache"           # BẮT BUỘC cho JSONL
qwen_image_edit_control_resolution = [1024, 1024]  # ⭐ QUAN TRỌNG
```

Tạo file `metadata.jsonl` (mỗi dòng là một JSON):

```json
{"image_path": "/path/to/image1.jpg", "control_path": "/path/to/control1.png", "caption": "Mô tả cho ảnh 1"}
{"image_path": "/path/to/image2.jpg", "control_path": "/path/to/control2.png", "caption": "Mô tả cho ảnh 2"}
```

## Tham số quan trọng

### `qwen_image_edit_control_resolution = [1024, 1024]` ⭐

**Khuyến nghị: Luôn đặt tham số này!**

- Control image sẽ được resize về **1M pixels** (giống official code)
- Giúp model học tốt hơn và kết quả ổn định hơn
- Nếu không đặt, control image sẽ resize về cùng resolution với ảnh mục tiêu

### Các tham số khác

- `resolution`: Độ phân giải training (ví dụ: `[1024, 1024]`, `[960, 544]`)
- `cache_directory`: Thư mục lưu cache (nên đặt riêng cho mỗi dataset)
- `num_repeats`: Số lần lặp lại dataset (mặc định: 1)
- `enable_bucket`: Bật aspect ratio bucketing (khuyến nghị: `true`)

## Ví dụ hoàn chỉnh

### Ví dụ 1: Dataset đơn giản

```toml
[general]
resolution = [1024, 1024]
caption_extension = ".txt"
batch_size = 1
enable_bucket = true

[[datasets]]
image_directory = "D:/datasets/qwen_edit/images"
control_directory = "D:/datasets/qwen_edit/controls"
cache_directory = "D:/datasets/qwen_edit/cache"
qwen_image_edit_control_resolution = [1024, 1024]
```

### Ví dụ 2: Nhiều datasets

```toml
[general]
resolution = [1024, 1024]
caption_extension = ".txt"
batch_size = 1
enable_bucket = true

[[datasets]]
image_directory = "D:/datasets/edit1/images"
control_directory = "D:/datasets/edit1/controls"
cache_directory = "D:/datasets/edit1/cache"
qwen_image_edit_control_resolution = [1024, 1024]
num_repeats = 2

[[datasets]]
image_directory = "D:/datasets/edit2/images"
control_directory = "D:/datasets/edit2/controls"
cache_directory = "D:/datasets/edit2/cache"
qwen_image_edit_control_resolution = [1024, 1024]
num_repeats = 1
```

## Lưu ý quan trọng

1. **Qwen-Image-Edit** (không phải 2509): Chỉ hỗ trợ **1 control image** mỗi ảnh
2. **Qwen-Image-Edit-2509**: Hỗ trợ **nhiều control images** (tối đa 3)
3. **Tên file**: Ảnh và control image phải cùng tên (ví dụ: `image1.jpg` và `image1.png`)
4. **Cache directory**: Nên đặt riêng cho mỗi dataset để tránh xung đột

## Khi chạy Training

Khi chạy training script, nhớ thêm flag:
- `--edit` cho Qwen-Image-Edit
- `--edit_plus` cho Qwen-Image-Edit-2509

Ví dụ:
```bash
python src/musubi_tuner/qwen_image_train_network.py \
    --dit path/to/edit_dit_model \
    --vae path/to/vae_model \
    --text_encoder path/to/text_encoder \
    --dataset_config dataset_config.toml \
    --edit \
    --network_module networks.lora_qwen_image \
    ...
```

## Checklist

Trước khi train, đảm bảo:
- [ ] Đã tạo thư mục `images/` và `controls/`
- [ ] Ảnh mục tiêu và control image có cùng tên file
- [ ] Đã tạo caption files (`.txt`) hoặc file JSONL
- [ ] Đã set `qwen_image_edit_control_resolution = [1024, 1024]` trong config
- [ ] Đã set `cache_directory` riêng biệt
- [ ] Đã thêm flag `--edit` hoặc `--edit_plus` khi chạy training



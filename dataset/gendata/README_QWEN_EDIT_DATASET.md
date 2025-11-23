# Hướng dẫn chuẩn bị Dataset cho Qwen-Image-Edit-2509 LoRA Training

## Tổng quan

Dataset `vietnamese_dataset` hiện tại chứa các ảnh với text tiếng Việt được render trên nền trắng. Để train Qwen-Image-Edit-2509 LoRA, bạn cần:

1. **Ảnh mục tiêu (target)**: Ảnh có text (đã có sẵn trong `vietnamese_dataset/images/`)
2. **Ảnh điều khiển (control)**: Ảnh nền trắng không có text (cần tạo)
3. **Caption files**: Mô tả sự thay đổi (cần tạo)

## Cách sử dụng

### Bước 1: Chạy script chuẩn bị dataset

```bash
# Cho RTX 3090 (24GB VRAM) - khuyến nghị
python prepare_qwen_edit_dataset.py \
    --dataset_dir vietnamese_dataset \
    --output_dir vietnamese_dataset_qwen_edit \
    --resolution 960 544

# Cho GPU có VRAM cao hơn (48GB+)
python prepare_qwen_edit_dataset.py \
    --dataset_dir vietnamese_dataset \
    --output_dir vietnamese_dataset_qwen_edit \
    --resolution 1328 1328
```

Script này sẽ:
- Copy ảnh từ `vietnamese_dataset/images/` sang `vietnamese_dataset_qwen_edit/images/`
- Tạo control images (ảnh nền trắng) trong `vietnamese_dataset_qwen_edit/controls/`
- Tạo caption files (.txt) trong `vietnamese_dataset_qwen_edit/images/` (cùng thư mục với ảnh)
- Tạo file config TOML: `vietnamese_dataset_qwen_edit/dataset_config.toml`

### Bước 2: Kiểm tra cấu trúc dataset

Sau khi chạy script, bạn sẽ có cấu trúc:

```
vietnamese_dataset_qwen_edit/
├── images/              # Ảnh mục tiêu (có text)
│   ├── image_000000.png
│   ├── image_000000.txt  # Caption file
│   ├── image_000001.png
│   ├── image_000001.txt
│   └── ...
├── controls/            # Ảnh điều khiển (nền trắng, không text)
│   ├── image_000000.png
│   ├── image_000001.png
│   └── ...
├── cache/               # Thư mục cache (sẽ được tạo khi cache latents)
└── dataset_config.toml  # File config cho training
```

### Bước 3: Cache Latents

```bash
python src/musubi_tuner/qwen_image_cache_latents.py \
    --dataset_config vietnamese_dataset_qwen_edit/dataset_config.toml \
    --vae path/to/vae_model \
    --edit_plus  # ← Flag cho Edit-2509 (không phải --edit)
```

**Lưu ý**: Phải thêm flag `--edit_plus` cho Qwen-Image-Edit-2509! (Không phải `--edit`)

### Bước 4: Cache Text Encoder Outputs

```bash
python src/musubi_tuner/qwen_image_cache_text_encoder_outputs.py \
    --dataset_config vietnamese_dataset_qwen_edit/dataset_config.toml \
    --text_encoder path/to/text_encoder \
    --edit_plus \  # ← Flag cho Edit-2509
    --batch_size 1
```

**Lưu ý**: Phải thêm flag `--edit_plus` cho Edit-2509!

### Bước 5: Train LoRA

**Cho RTX 3090 (24GB VRAM) - Khuyến nghị:**

```bash
accelerate launch --num_cpu_threads_per_process 1 --mixed_precision bf16 \
    src/musubi_tuner/qwen_image_train_network.py \
    --dit path/to/qwen_image_edit_2509_bf16.safetensors \  # ← Phải dùng model Edit-2509
    --vae path/to/vae_model \
    --text_encoder path/to/text_encoder \
    --dataset_config vietnamese_dataset_qwen_edit/dataset_config.toml \
    --edit_plus \  # ← Flag cho Edit-2509 (bắt buộc!)
    --sdpa --mixed_precision bf16 \
    --fp8_base --fp8_scaled \  # ← Tiết kiệm VRAM cho DiT
    --fp8_vl \  # ← Tiết kiệm VRAM cho Text Encoder
    --gradient_checkpointing \  # ← Bắt buộc cho RTX 3090
    --timestep_sampling shift \
    --weighting_scheme none --discrete_flow_shift 2.2 \
    --optimizer_type adamw8bit --learning_rate 5e-5 \
    --max_data_loader_n_workers 2 --persistent_data_loader_workers \
    --network_module networks.lora_qwen_image \
    --network_dim 16 \
    --max_train_epochs 16 --save_every_n_epochs 1 --seed 42 \
    --output_dir path/to/output_dir --output_name name-of-lora
```

**Cho GPU có VRAM cao hơn (48GB+):**

```bash
accelerate launch --num_cpu_threads_per_process 1 --mixed_precision bf16 \
    src/musubi_tuner/qwen_image_train_network.py \
    --dit path/to/qwen_image_edit_2509_bf16.safetensors \
    --vae path/to/vae_model \
    --text_encoder path/to/text_encoder \
    --dataset_config vietnamese_dataset_qwen_edit/dataset_config.toml \
    --edit_plus \
    --sdpa --mixed_precision bf16 \
    --gradient_checkpointing \
    --timestep_sampling shift \
    --weighting_scheme none --discrete_flow_shift 2.2 \
    --optimizer_type adamw8bit --learning_rate 5e-5 \
    --max_data_loader_n_workers 2 --persistent_data_loader_workers \
    --network_module networks.lora_qwen_image \
    --network_dim 16 \
    --max_train_epochs 16 --save_every_n_epochs 1 --seed 42 \
    --output_dir path/to/output_dir --output_name name-of-lora
```

## Cấu trúc Dataset Config

File `dataset_config.toml` được tạo tự động có dạng:

```toml
[general]
resolution = [960, 544]  # 960x544 cho RTX 3090, hoặc 1328x1328 cho VRAM cao hơn
caption_extension = ".txt"
batch_size = 1
enable_bucket = true
bucket_no_upscale = false

[[datasets]]
image_directory = "path/to/images"      # Ảnh mục tiêu (có text)
control_directory = "path/to/controls"  # Ảnh điều khiển (nền trắng)
cache_directory = "path/to/cache"
qwen_image_edit_control_resolution = [1024, 1024]  # Resize control về 1M pixels (khuyến nghị)
num_repeats = 1
```

## Lưu ý quan trọng

1. **Control images**: Phải có cùng tên file với ảnh mục tiêu (có thể khác extension)
   - Ví dụ: `image_000000.png` (target) ↔ `image_000000.png` (control)

2. **Caption files**: Phải cùng tên với ảnh và có extension `.txt`
   - Ví dụ: `image_000000.png` ↔ `image_000000.txt`

3. **Flag `--edit_plus`**: Bắt buộc phải có khi:
   - Cache latents (dùng `--edit_plus`, không phải `--edit`)
   - Cache text encoder outputs (dùng `--edit_plus`)
   - Train LoRA (dùng `--edit_plus`)
   
   **Lưu ý**: Edit-2509 dùng `--edit_plus`, không phải `--edit`!

4. **Resolution**: 
   - Mặc định: 960x544 (phù hợp cho RTX 3090)
   - Cho VRAM cao hơn: 1328x1328 hoặc 1024x1024
   - Bạn có thể thay đổi trong script với `--resolution` hoặc sửa trong config

5. **Control resolution**: Khuyến nghị dùng `qwen_image_edit_control_resolution = [1024, 1024]` để resize control images về 1M pixels (giống official code).

## Troubleshooting

### Lỗi: Control image không tìm thấy
- Kiểm tra tên file control image phải khớp với ảnh mục tiêu
- Kiểm tra đường dẫn trong `dataset_config.toml`

### Lỗi: Caption file không tìm thấy
- Kiểm tra caption files có trong cùng thư mục với images
- Kiểm tra extension phải là `.txt`

### Lỗi khi cache/train
- Đảm bảo đã thêm flag `--edit_plus` (không phải `--edit`)
- Kiểm tra đường dẫn model files (DiT phải là `qwen_image_edit_2509_bf16.safetensors`, VAE, Text Encoder)
- Kiểm tra VRAM: Nếu thiếu VRAM, thêm `--fp8_base --fp8_scaled --fp8_vl` và `--blocks_to_swap 16`

## Tùy chỉnh Caption

Nếu muốn thay đổi format caption, sửa function `create_caption_files()` trong `prepare_qwen_edit_dataset.py`:

```python
caption = f"Add Vietnamese text \"{text}\" to the white background image. The text should be black and centered."
```

Bạn có thể thay đổi thành:
- Tiếng Việt: `f"Thêm text tiếng Việt \"{text}\" vào ảnh nền trắng. Text màu đen và căn giữa."`
- Hoặc format khác tùy nhu cầu

## Cấu hình cho RTX 3090 (24GB VRAM)

Nếu bạn dùng RTX 3090, khuyến nghị:

1. **Resolution**: Dùng `960 544` (mặc định)
   ```bash
   python prepare_qwen_edit_dataset.py --resolution 960 544
   ```

2. **Training flags**: Bắt buộc phải có:
   - `--edit_plus`: Flag cho Edit-2509
   - `--fp8_base --fp8_scaled`: Tối ưu DiT (tiết kiệm ~12GB VRAM)
   - `--fp8_vl`: Tối ưu Text Encoder (tiết kiệm VRAM)
   - `--gradient_checkpointing`: Bắt buộc
   - `--blocks_to_swap 16`: Nếu vẫn thiếu VRAM (cần 64GB RAM)

3. **VRAM Usage ước tính**:
   - Không tối ưu: ~42GB (không đủ cho RTX 3090)
   - Với `--fp8_base --fp8_scaled`: ~30GB
   - + `--blocks_to_swap 16`: ~24GB (vừa đủ cho RTX 3090)

4. **Model files**: Đảm bảo dùng đúng model Edit-2509:
   - DiT: `qwen_image_edit_2509_bf16.safetensors` (không phải `qwen_image_edit_bf16.safetensors`)
   - VAE: `diffusion_pytorch_model.safetensors` từ Qwen/Qwen-Image
   - Text Encoder: `qwen_2.5_vl_7b.safetensors` từ Comfy-Org/Qwen-Image_ComfyUI


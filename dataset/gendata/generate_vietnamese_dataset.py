"""
Script để tạo dataset ảnh-prompt tiếng Việt cho image generation
Tạo các ảnh synthetic với prompt sinh ảnh tiếng Việt được render trên ảnh
Các prompt này là những yêu cầu thực tế mà người dùng thường dùng khi gen ảnh
"""

import os
import random
import json
import sys
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional
import argparse

# Fix encoding cho Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# Danh sách prompt sinh ảnh ngắn (từ/cụm từ)
IMAGE_GEN_SHORT_PROMPTS = [
    "Mặt trời mọc", "Hoàng hôn", "Bình minh", "Đêm sao", "Bầu trời xanh",
    "Rừng xanh", "Biển xanh", "Núi cao", "Sông dài", "Cánh đồng lúa",
    "Con mèo dễ thương", "Con chó trung thành", "Chim bay", "Cá bơi", "Bướm đẹp",
    "Hoa hồng", "Hoa sen", "Hoa đào", "Hoa mai", "Hoa cúc",
    "Phong cảnh đẹp", "Thiên nhiên hoang dã", "Thành phố hiện đại", "Làng quê yên bình", "Phố cổ",
    "Người phụ nữ xinh đẹp", "Người đàn ông mạnh mẽ", "Trẻ em vui vẻ", "Người già hiền từ", "Gia đình hạnh phúc",
    "Món ăn ngon", "Cà phê thơm", "Bánh mì giòn", "Phở nóng", "Bún chả",
    "Màu đỏ rực", "Màu xanh dương", "Màu vàng tươi", "Màu hồng nhẹ", "Màu tím đậm",
    "Nghệ thuật trừu tượng", "Tranh sơn dầu", "Digital art", "Anime style", "Realistic",
    "Không gian vũ trụ", "Hành tinh xa xôi", "Ngôi sao sáng", "Thiên hà xoắn ốc", "Nebula đầy màu sắc"
]

# Danh sách prompt sinh ảnh trung bình (câu mô tả)
IMAGE_GEN_MEDIUM_PROMPTS = [
    "Một con mèo dễ thương đang nằm trên cỏ xanh dưới ánh nắng mặt trời",
    "Hoàng hôn đẹp trên biển với màu cam và đỏ rực rỡ",
    "Rừng mưa nhiệt đới với cây cối xanh tươi và ánh sáng xuyên qua tán lá",
    "Thành phố về đêm với đèn neon sáng rực và xe cộ qua lại",
    "Một người phụ nữ mặc áo dài truyền thống đứng bên hồ sen",
    "Phong cảnh núi non hùng vĩ với mây trắng bao quanh đỉnh núi",
    "Cánh đồng lúa chín vàng dưới bầu trời xanh trong",
    "Một bức tranh phong cảnh làng quê Việt Nam với nhà cổ và cây đa",
    "Chú chó đang chạy trên bãi biển vào buổi sáng sớm",
    "Hoa đào nở rộ trong vườn với cánh hoa màu hồng nhẹ nhàng",
    "Một bữa ăn truyền thống Việt Nam với nhiều món ngon bày trên bàn",
    "Thiên nhiên hoang dã với động vật đang sinh sống tự nhiên",
    "Một tòa nhà hiện đại với kiến trúc độc đáo và ánh sáng đẹp",
    "Bầu trời đêm đầy sao với dải ngân hà rõ ràng",
    "Một bức tranh nghệ thuật trừu tượng với màu sắc sống động",
    "Phong cảnh biển với sóng vỗ vào bờ cát trắng",
    "Một khu vườn đầy hoa với bướm bay lượn xung quanh",
    "Thành phố cổ kính với kiến trúc cổ điển và đường phố lát đá",
    "Một con đường uốn lượn qua rừng với ánh sáng vàng chiếu xuống",
    "Phong cảnh mùa thu với lá vàng rơi và không khí mát mẻ",
    "Một ngôi nhà nhỏ xinh xắn bên sông với cây cầu gỗ",
    "Bình minh trên núi với sương mù bao phủ thung lũng",
    "Một bức tranh digital art với hiệu ứng ánh sáng đẹp mắt",
    "Phong cảnh đô thị hiện đại với tòa nhà chọc trời",
    "Một khu rừng bí ẩn với ánh sáng xanh kỳ lạ",
    "Hoa sen trong ao với lá xanh và hoa hồng nở rộ",
    "Một bức tranh anime style với nhân vật dễ thương",
    "Phong cảnh sa mạc với cát vàng và bầu trời xanh",
    "Một con thuyền trên sông với phản chiếu đẹp trên mặt nước",
    "Thiên nhiên mùa xuân với hoa nở khắp nơi và cây xanh tươi"
]

# Danh sách prompt sinh ảnh dài (mô tả chi tiết với style)
IMAGE_GEN_DETAILED_PROMPTS = [
    "Một bức tranh phong cảnh hoàng hôn trên biển, màu cam và đỏ rực rỡ phản chiếu trên mặt nước, phong cách realistic với độ chi tiết cao, 4K, ánh sáng tự nhiên",
    "Con mèo dễ thương màu cam đang nằm trên cỏ xanh, ánh nắng mặt trời chiếu xuống tạo bóng đẹp, phong cách nhiếp ảnh chuyên nghiệp, độ sâu trường ảnh nông",
    "Rừng mưa nhiệt đới với cây cối xanh tươi, ánh sáng xuyên qua tán lá tạo hiệu ứng god rays, sương mù nhẹ, phong cách fantasy art, màu sắc sống động",
    "Thành phố về đêm với đèn neon sáng rực, xe cộ qua lại tạo vệt sáng, phong cách cyberpunk, màu xanh và hồng chủ đạo, độ phân giải cao",
    "Người phụ nữ mặc áo dài trắng truyền thống đứng bên hồ sen, hoa sen hồng nở rộ, phong cảnh yên bình, phong cách nhiếp ảnh nghệ thuật, ánh sáng mềm mại",
    "Phong cảnh núi non hùng vĩ với đỉnh núi phủ tuyết, mây trắng bao quanh, bầu trời xanh trong, phong cách landscape photography, wide angle, độ chi tiết cao",
    "Cánh đồng lúa chín vàng rộng lớn, bầu trời xanh với mây trắng, một con đường nhỏ chạy qua, phong cách realistic, ánh sáng ban ngày tự nhiên, màu sắc ấm áp",
    "Bức tranh digital art trừu tượng với màu sắc gradient từ xanh dương sang tím, hiệu ứng ánh sáng và particles, phong cách modern art, độ phân giải 4K",
    "Thiên nhiên hoang dã với đàn voi đang đi trong rừng, ánh sáng vàng chiếu xuống, phong cách wildlife photography, màu sắc tự nhiên, độ chi tiết cao",
    "Phong cảnh làng quê Việt Nam với nhà cổ, cây đa cổ thụ, ao sen, phong cách nostalgic, màu sắc ấm áp, ánh sáng hoàng hôn, bầu không khí yên bình",
    "Bầu trời đêm đầy sao với dải ngân hà rõ ràng, phong cảnh núi ở phía trước, phong cách astrophotography, màu sắc tối với điểm nhấn là các ngôi sao sáng",
    "Hoa đào nở rộ trong vườn với cánh hoa màu hồng nhẹ nhàng, phong cảnh mùa xuân, phong cách nhiếp ảnh macro, độ sâu trường ảnh nông, background mờ",
    "Một bữa ăn truyền thống Việt Nam với nhiều món ngon bày trên bàn gỗ, phong cách food photography, ánh sáng tự nhiên từ cửa sổ, màu sắc ấm áp và hấp dẫn",
    "Phong cảnh biển với sóng vỗ vào bờ cát trắng, bầu trời xanh với mây trắng, phong cách beach photography, ánh sáng ban ngày, màu sắc tươi sáng",
    "Bức tranh anime style với nhân vật nữ dễ thương, phong cảnh phía sau đẹp mắt, màu sắc pastel, phong cách Japanese animation, độ chi tiết cao",
    "Khu rừng bí ẩn với ánh sáng xanh kỳ lạ phát ra từ cây cối, sương mù bao phủ, phong cách fantasy art, không khí huyền bí, màu sắc sống động",
    "Phong cảnh đô thị hiện đại với tòa nhà chọc trời, đèn sáng vào ban đêm, phong cách urban photography, góc nhìn từ trên cao, độ phân giải cao",
    "Hoa sen trong ao với lá xanh và hoa hồng nở rộ, phản chiếu trên mặt nước, phong cách nhiếp ảnh nghệ thuật, ánh sáng mềm mại, màu sắc tự nhiên",
    "Một con đường uốn lượn qua rừng với ánh sáng vàng chiếu xuống qua tán lá, phong cách landscape photography, độ sâu trường ảnh sâu, màu sắc ấm áp",
    "Phong cảnh mùa thu với lá vàng rơi, cây cối đổi màu, không khí mát mẻ, phong cách realistic, ánh sáng tự nhiên, màu sắc ấm áp và dễ chịu",
    "Ngôi nhà nhỏ xinh xắn bên sông với cây cầu gỗ, phong cảnh yên bình, phong cách cottage core, màu sắc pastel, ánh sáng ban ngày dịu nhẹ",
    "Bình minh trên núi với sương mù bao phủ thung lũng, ánh sáng vàng cam chiếu xuống, phong cách landscape photography, wide angle, độ chi tiết cao",
    "Bức tranh digital art với hiệu ứng ánh sáng đẹp mắt, màu sắc gradient, particles và glow effects, phong cách modern art, độ phân giải 4K",
    "Phong cảnh sa mạc với cát vàng và bầu trời xanh, cây xương rồng, phong cách desert photography, ánh sáng mạnh, màu sắc tương phản",
    "Con thuyền trên sông với phản chiếu đẹp trên mặt nước, phong cảnh yên bình, phong cách nhiếp ảnh nghệ thuật, ánh sáng hoàng hôn, màu sắc ấm áp",
    "Thiên nhiên mùa xuân với hoa nở khắp nơi và cây xanh tươi, bướm bay lượn, phong cách nature photography, màu sắc tươi sáng, ánh sáng tự nhiên",
    "Phong cảnh không gian vũ trụ với hành tinh xa xôi, nebula đầy màu sắc, ngôi sao sáng, phong cách space art, màu sắc sống động, độ chi tiết cao",
    "Một khu vườn đầy hoa với bướm bay lượn xung quanh, phong cảnh mùa xuân, phong cách garden photography, màu sắc pastel, ánh sáng mềm mại",
    "Thành phố cổ kính với kiến trúc cổ điển và đường phố lát đá, phong cách European architecture, ánh sáng vàng ấm, bầu không khí lãng mạn",
    "Phong cảnh đêm với trăng tròn sáng và cây cối tạo bóng đen, phong cách night photography, màu sắc tối với điểm nhấn là ánh trăng, không khí huyền bí"
]


class VietnameseImageTextGenerator:
    """Class để tạo ảnh với text tiếng Việt"""
    
    def __init__(self, output_dir: str = "vietnamese_dataset", width: int = 512, height: int = 512):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.width = width
        self.height = height
        self.original_width = width  # Lưu kích thước gốc
        self.original_height = height  # Lưu kích thước gốc
        self.max_image_size = 2048  # Giới hạn kích thước ảnh tối đa để tránh MemoryError
        
        # Tạo thư mục con
        (self.output_dir / "images").mkdir(exist_ok=True)
        (self.output_dir / "metadata").mkdir(exist_ok=True)
        
        # Thử load font tiếng Việt
        self.font, self.font_path = self._load_font()
        
    def _test_font_vietnamese(self, font: ImageFont.FreeTypeFont) -> bool:
        """Kiểm tra font có hỗ trợ ký tự tiếng Việt không"""
        test_chars = "ứậếốộầấ"
        try:
            # Tạo một ảnh test nhỏ
            test_img = Image.new('RGB', (100, 100), (255, 255, 255))
            test_draw = ImageDraw.Draw(test_img)
            
            # Thử vẽ các ký tự có dấu
            for char in test_chars:
                try:
                    bbox = test_draw.textbbox((0, 0), char, font=font)
                    # Nếu bbox hợp lệ và có kích thước, font hỗ trợ
                    if bbox[2] - bbox[0] == 0 and bbox[3] - bbox[1] == 0:
                        return False
                except:
                    return False
            return True
        except:
            return False
    
    def _load_font(self, font_size: int = 48) -> Tuple[Optional[ImageFont.FreeTypeFont], Optional[str]]:
        """Load font hỗ trợ tiếng Việt tốt nhất, trả về (font, font_path)"""
        # Danh sách font ưu tiên - các font hỗ trợ tốt tiếng Việt
        font_paths = [
            # Windows fonts - ưu tiên các font hỗ trợ tốt Unicode
            "C:/Windows/Fonts/times.ttf",           # Times New Roman - hỗ trợ tốt
            "C:/Windows/Fonts/timesbd.ttf",         # Times New Roman Bold
            "C:/Windows/Fonts/arial.ttf",           # Arial
            "C:/Windows/Fonts/arialbd.ttf",         # Arial Bold
            "C:/Windows/Fonts/tahoma.ttf",          # Tahoma - rất tốt cho tiếng Việt
            "C:/Windows/Fonts/tahomabd.ttf",         # Tahoma Bold
            "C:/Windows/Fonts/segoeui.ttf",         # Segoe UI
            "C:/Windows/Fonts/segoeuib.ttf",        # Segoe UI Bold
            "C:/Windows/Fonts/calibri.ttf",         # Calibri
            "C:/Windows/Fonts/calibrib.ttf",        # Calibri Bold
            "C:/Windows/Fonts/verdana.ttf",         # Verdana
            "C:/Windows/Fonts/verdanab.ttf",       # Verdana Bold
            "C:/Windows/Fonts/msyh.ttc",            # Microsoft YaHei (nếu có)
            "C:/Windows/Fonts/simsun.ttc",          # SimSun (nếu có)
            
            # macOS fonts
            "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            
            # Linux fonts
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        ]
        
        best_font = None
        best_font_path = None
        best_score = 0
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    font = ImageFont.truetype(font_path, font_size)
                    # Kiểm tra font có hỗ trợ tiếng Việt không
                    if self._test_font_vietnamese(font):
                        # Ưu tiên Times New Roman và Tahoma
                        score = 10
                        if "times" in font_path.lower():
                            score = 20
                        elif "tahoma" in font_path.lower():
                            score = 15
                        elif "arial" in font_path.lower():
                            score = 12
                        
                        if score > best_score:
                            best_font = font
                            best_font_path = font_path
                            best_score = score
                            # Nếu là font tốt nhất, dùng luôn
                            if score >= 15:
                                try:
                                    print(f"Found good font: {font_path}")
                                except:
                                    pass
                                return font, font_path
                except Exception as e:
                    continue
        
        if best_font:
            try:
                print(f"Found Vietnamese font: {best_font_path}")
            except:
                pass
            return best_font, best_font_path
        
        # Fallback: thử tất cả font có sẵn mà không test
        try:
            print("Warning: No optimal font found, trying default fonts...")
        except:
            pass
        for font_path in font_paths[:5]:  # Thử 5 font đầu tiên
            if os.path.exists(font_path):
                try:
                    font = ImageFont.truetype(font_path, font_size)
                    try:
                        print(f"Using font: {font_path}")
                    except:
                        pass
                    return font, font_path
                except:
                    continue
        
        # Cuối cùng dùng font mặc định
        try:
            print("Warning: Using default font - may not display Vietnamese correctly")
        except:
            pass
        return ImageFont.load_default(), None
    
    def _generate_background(self) -> Image.Image:
        """Tạo background màu trắng cho ảnh"""
        # Tạo ảnh với nền trắng
        bg_color = (255, 255, 255)  # Màu trắng
        img = Image.new('RGB', (self.width, self.height), bg_color)
        
        return img
    
    def _get_text_color(self, bg_color: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """Chọn màu text - với nền trắng thì dùng màu đen"""
        # Vì nền luôn là trắng, text luôn là đen
        return (0, 0, 0)  # Màu đen
    
    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
        """Chia text thành nhiều dòng để fit vào chiều rộng"""
        if not text.strip():
            return [text]
        
        # Tạo một draw object tạm để đo kích thước
        temp_img = Image.new('RGB', (100, 100), (255, 255, 255))
        temp_draw = ImageDraw.Draw(temp_img)
        
        # Kiểm tra nếu text ngắn, không cần wrap
        bbox = temp_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        if text_width <= max_width:
            return [text]
        
        # Chia text thành từ
        words = text.split()
        if not words:
            return [text]
        
        lines = []
        current_line = []
        
        for word in words:
            # Thử thêm word vào dòng hiện tại
            if current_line:
                test_line = ' '.join(current_line + [word])
            else:
                test_line = word
            
            bbox = temp_draw.textbbox((0, 0), test_line, font=font)
            line_width = bbox[2] - bbox[0]
            
            if line_width <= max_width:
                current_line.append(word)
            else:
                # Dòng hiện tại đã đầy
                if current_line:
                    lines.append(' '.join(current_line))
                # Kiểm tra nếu word đơn lẻ quá dài, chia theo ký tự
                bbox_word = temp_draw.textbbox((0, 0), word, font=font)
                word_width = bbox_word[2] - bbox_word[0]
                if word_width > max_width:
                    # Chia word theo ký tự
                    char_per_line = max(10, max_width // 30)  # Ước tính số ký tự
                    for i in range(0, len(word), char_per_line):
                        lines.append(word[i:i+char_per_line])
                    current_line = []
                else:
                    current_line = [word]
        
        # Thêm dòng cuối cùng
        if current_line:
            lines.append(' '.join(current_line))
        
        # Đảm bảo có ít nhất một dòng
        if not lines:
            # Nếu vẫn không có dòng, chia theo ký tự
            char_per_line = max(15, max_width // 25)
            lines = []
            for i in range(0, len(text), char_per_line):
                lines.append(text[i:i+char_per_line])
        
        return lines
    
    def _wrap_text_vertical(self, text: str, font: ImageFont.FreeTypeFont, max_height: int) -> List[str]:
        """Chia text thành nhiều cột để fit vào chiều cao khi render dọc"""
        if not text.strip():
            return [text]
        
        # Tạo một draw object tạm để đo kích thước
        temp_img = Image.new('RGB', (100, 100), (255, 255, 255))
        temp_draw = ImageDraw.Draw(temp_img)
        
        # Kiểm tra nếu text ngắn, không cần wrap
        bbox = temp_draw.textbbox((0, 0), text, font=font)
        text_height = bbox[3] - bbox[1]
        if text_height <= max_height:
            return [text]
        
        # Chia text thành từ
        words = text.split()
        if not words:
            return [text]
        
        columns = []
        current_column = []
        current_height = 0
        
        for word in words:
            # Thử thêm word vào cột hiện tại
            if current_column:
                test_text = '\n'.join(current_column + [word])
            else:
                test_text = word
            
            # Tính chiều cao của text (mỗi ký tự một dòng khi dọc)
            # Với text dọc, mỗi ký tự chiếm một dòng
            test_height = len(test_text) * (bbox[3] - bbox[1]) // max(1, len(test_text))
            
            # Ước tính chính xác hơn
            bbox_test = temp_draw.textbbox((0, 0), test_text, font=font)
            test_height = bbox_test[3] - bbox_test[1]
            
            if test_height <= max_height:
                current_column.append(word)
                current_height = test_height
            else:
                # Cột hiện tại đã đầy
                if current_column:
                    columns.append('\n'.join(current_column))
                # Kiểm tra nếu word đơn lẻ quá dài
                bbox_word = temp_draw.textbbox((0, 0), word, font=font)
                word_height = bbox_word[3] - bbox_word[1]
                if word_height > max_height:
                    # Chia word theo ký tự
                    for char in word:
                        columns.append(char)
                else:
                    current_column = [word]
                    current_height = word_height
        
        # Thêm cột cuối cùng
        if current_column:
            columns.append('\n'.join(current_column))
        
        # Đảm bảo có ít nhất một cột
        if not columns:
            # Chia theo ký tự
            columns = list(text)
        
        return columns
    
    def _render_vertical_text(self, draw: ImageDraw.Draw, text: str, x: int, y: int, 
                             font: ImageFont.FreeTypeFont, fill: Tuple[int, int, int],
                             max_height: int) -> None:
        """Render text theo chiều dọc (từ trên xuống)"""
        # Chia text thành các cột nếu cần
        columns = self._wrap_text_vertical(text, font, max_height)
        
        current_x = x
        char_height = 0
        
        # Tính chiều cao của một ký tự
        bbox = draw.textbbox((0, 0), "A", font=font)
        char_height = bbox[3] - bbox[1]
        line_spacing = int(char_height * 0.1)  # Khoảng cách giữa các ký tự
        
        # Vẽ từng cột
        for col_idx, column in enumerate(columns):
            current_y = y
            # Vẽ từng ký tự trong cột (hoặc từng từ nếu column là một từ)
            if '\n' in column:
                # Column chứa nhiều từ, vẽ từng từ
                words = column.split('\n')
                for word in words:
                    for char in word:
                        try:
                            draw.text((current_x, current_y), char, font=font, fill=fill)
                            current_y += char_height + line_spacing
                        except:
                            pass
                    # Thêm khoảng cách giữa các từ
                    current_y += line_spacing
            else:
                # Column là một từ hoặc ký tự đơn
                for char in column:
                    try:
                        draw.text((current_x, current_y), char, font=font, fill=fill)
                        current_y += char_height + line_spacing
                    except:
                        pass
            
            # Di chuyển sang cột tiếp theo
            bbox_col = draw.textbbox((0, 0), column[0] if column else "A", font=font)
            char_width = bbox_col[2] - bbox_col[0]
            current_x += char_width + line_spacing
    
    def generate_image_with_text(self, text: str, image_id: int) -> Tuple[Image.Image, dict]:
        """Tạo ảnh với text tiếng Việt ngang, sau đó xoay ảnh -30, 0, hoặc +30 độ so với trục ngang"""
        # Đếm số từ trong text
        word_count = len(text.split())
        
        # Xác định font size và rotation angle dựa trên số từ
        if word_count > 10:
            # Với text > 10 từ: font size 104-120 và không xoay
            font_size = random.randint(104, 120)
            rotation_angle = 0  # Không xoay
        else:
            # Với text <= 10 từ: font size 104-170 và có thể xoay
            font_size = random.randint(104, 170)
            # Chọn ngẫu nhiên góc xoay: -30 độ (xuống), 0 độ (không xoay), hoặc +30 độ (lên)
            rotation_angle = random.choice([-30, 0, 30])
        
        # Tạo background
        img = self._generate_background()
        draw = ImageDraw.Draw(img)
        
        # Lấy màu nền trung bình để chọn màu text
        bg_sample = img.getpixel((self.width//2, self.height//2))
        text_color = self._get_text_color(bg_sample)
        
        # Sử dụng font path đã lưu
        font_path = self.font_path
        
        # Tính toán vị trí và kích thước text (luôn ngang)
        current_font = None
        max_width = int(self.width * 0.9)  # Để lại margin 5% mỗi bên
        max_height = int(self.height * 0.9)
        
        # Tạo font với size ngẫu nhiên
        if font_path and os.path.exists(font_path):
            current_font = ImageFont.truetype(font_path, font_size)
        else:
            current_font = self.font
        
        # Wrap text thành nhiều dòng nếu quá dài
        lines = self._wrap_text(text, current_font, max_width)
        
        # Tính kích thước tổng của tất cả các dòng
        line_heights = []
        line_widths = []
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=current_font)
            line_widths.append(bbox[2] - bbox[0])
            line_heights.append(bbox[3] - bbox[1])
        
        total_height = sum(line_heights)
        line_spacing = int(line_heights[0] * 0.2) if line_heights else 5
        total_height += line_spacing * (len(lines) - 1)
        max_line_width = max(line_widths) if line_widths else 0
        
        # Nếu tổng chiều cao vẫn quá lớn, giảm font size
        min_font_size = 40
        if total_height > max_height:
            # Giảm font size cho đến khi fit
            while total_height > max_height and font_size > min_font_size:
                font_size = max(font_size - 1, min_font_size)
                if font_path and os.path.exists(font_path):
                    current_font = ImageFont.truetype(font_path, font_size)
                else:
                    current_font = self.font
                
                # Tính lại với font size mới
                lines = self._wrap_text(text, current_font, max_width)
                line_heights = []
                line_widths = []
                for line in lines:
                    bbox = draw.textbbox((0, 0), line, font=current_font)
                    line_widths.append(bbox[2] - bbox[0])
                    line_heights.append(bbox[3] - bbox[1])
                
                total_height = sum(line_heights)
                line_spacing = int(line_heights[0] * 0.2) if line_heights else 5
                total_height += line_spacing * (len(lines) - 1)
                max_line_width = max(line_widths) if line_widths else 0
        
        # Render text ngang - có thể nhiều dòng
        # Tính vị trí để căn giữa (cả ngang và dọc)
        start_y = (self.height - total_height) // 2
        
        # Vẽ từng dòng
        current_y = start_y
        for i, line in enumerate(lines):
            if not line.strip():  # Bỏ qua dòng trống
                continue
                
            # Tính vị trí x để căn giữa dòng này
            line_width = line_widths[i]
            x = (self.width - line_width) // 2
            
            try:
                draw.text((x, current_y), line, font=current_font, fill=text_color)
            except Exception as e:
                # Nếu lỗi, thử với font mặc định
                try:
                    fallback_font = ImageFont.load_default()
                    draw.text((x, current_y), line, font=fallback_font, fill=text_color)
                except:
                    pass
            
            # Di chuyển xuống dòng tiếp theo
            current_y += line_heights[i] + line_spacing
        
        # Xoay ảnh nếu góc xoay != 0
        if rotation_angle != 0:
            try:
                img = img.rotate(rotation_angle, expand=True, fillcolor=(255, 255, 255))
                # Sau khi xoay, resize về kích thước gốc để đảm bảo tất cả ảnh có cùng kích thước
                img = img.resize((self.original_width, self.original_height), Image.Resampling.LANCZOS)
                self.width = self.original_width
                self.height = self.original_height
            except MemoryError:
                # Nếu bị MemoryError, bỏ qua việc xoay và giữ ảnh gốc
                rotation_angle = 0
                try:
                    print(f"Warning: MemoryError when rotating image {image_id}, skipping rotation")
                except:
                    pass
        
        num_lines = 1
        
        # Tạo prompt với format cố định
        prompt = f'This image is saying "{text}". The background is white. The letter is black.'
        
        # Metadata
        metadata = {
            "image_id": image_id,
            "text": text,
            "prompt": prompt,
            "width": self.original_width,
            "height": self.original_height,
            "font_size": font_size,
            "num_lines": len(lines),
            "rotation_angle": rotation_angle,
            "orientation": "rotated" if rotation_angle != 0 else "horizontal"
        }
        
        return img, metadata
    
    def generate_dataset(self, num_images: int = 1000, 
                        text_source: str = "mixed") -> None:
        """Tạo dataset với số lượng ảnh chỉ định"""
        try:
            print(f"Starting to create {num_images} images...")
        except:
            print(f"Starting to create {num_images} images...")
        
        all_metadata = []
        
        for i in range(num_images):
            # Chọn prompt ngẫu nhiên
            max_attempts = 10  # Số lần thử tối đa để tìm prompt phù hợp
            text = None
            
            for attempt in range(max_attempts):
                if text_source == "words":
                    text = random.choice(IMAGE_GEN_SHORT_PROMPTS)
                elif text_source == "phrases":
                    text = random.choice(IMAGE_GEN_MEDIUM_PROMPTS)
                elif text_source == "sentences":
                    text = random.choice(IMAGE_GEN_DETAILED_PROMPTS)
                else:  # mixed
                    text = random.choice(
                        IMAGE_GEN_SHORT_PROMPTS + IMAGE_GEN_MEDIUM_PROMPTS + IMAGE_GEN_DETAILED_PROMPTS
                    )
                
                # Đếm số từ
                word_count = len(text.split())
                
                # Chỉ chấp nhận prompt có <= 20 từ
                if word_count <= 20:
                    break
                else:
                    # Nếu quá 20 từ, thử lại với prompt ngắn hơn
                    # Ưu tiên chọn từ SHORT_PROMPTS hoặc MEDIUM_PROMPTS
                    if attempt < max_attempts - 1:
                        text = random.choice(IMAGE_GEN_SHORT_PROMPTS + IMAGE_GEN_MEDIUM_PROMPTS)
                        word_count = len(text.split())
                        if word_count <= 20:
                            break
            
            # Nếu vẫn không tìm được, dùng prompt ngắn nhất
            if text is None or len(text.split()) > 20:
                text = random.choice(IMAGE_GEN_SHORT_PROMPTS)
            
            # Tạo ảnh
            img, metadata = self.generate_image_with_text(text, i)
            
            # Đảm bảo ảnh có đúng kích thước gốc (resize nếu cần)
            if img.size != (self.original_width, self.original_height):
                img = img.resize((self.original_width, self.original_height), Image.Resampling.LANCZOS)
            
            # Lưu ảnh
            img_path = self.output_dir / "images" / f"image_{i:06d}.png"
            img.save(img_path, "PNG")
            
            # Lưu metadata
            metadata["image_path"] = str(img_path.relative_to(self.output_dir))
            all_metadata.append(metadata)
            
            if (i + 1) % 100 == 0:
                try:
                    print(f"Created {i + 1}/{num_images} images...")
                except:
                    print(f"Created {i + 1}/{num_images} images...")
        
        # Lưu metadata tổng hợp
        metadata_path = self.output_dir / "metadata" / "metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(all_metadata, f, ensure_ascii=False, indent=2)
        
        # Tạo file text list
        text_list_path = self.output_dir / "metadata" / "texts.txt"
        with open(text_list_path, 'w', encoding='utf-8') as f:
            for meta in all_metadata:
                f.write(f"{meta['text']}\n")
        
        try:
            print(f"\nCompleted! Dataset saved at: {self.output_dir}")
            print(f"- Number of images: {num_images}")
            print(f"- Images directory: {self.output_dir / 'images'}")
            print(f"- Metadata: {metadata_path}")
            print(f"- Text list: {text_list_path}")
        except:
            print(f"\nCompleted! Dataset saved at: {self.output_dir}")
            print(f"- Number of images: {num_images}")


def main():
    parser = argparse.ArgumentParser(description="Tạo dataset ảnh-văn bản tiếng Việt")
    parser.add_argument("--num_images", type=int, default=1000,
                       help="Số lượng ảnh cần tạo (default: 1000)")
    parser.add_argument("--output_dir", type=str, default="vietnamese_dataset",
                       help="Thư mục output (default: vietnamese_dataset)")
    parser.add_argument("--image_size", type=int, default=1328,
                       help="Kích thước ảnh vuông (width = height, default: 1328)")
    parser.add_argument("--text_source", type=str, default="mixed",
                       choices=["words", "phrases", "sentences", "mixed"],
                       help="Nguồn prompt: words (ngắn), phrases (trung bình), sentences (chi tiết), hoặc mixed (default: mixed)")
    
    args = parser.parse_args()
    
    generator = VietnameseImageTextGenerator(
        output_dir=args.output_dir,
        width=args.image_size,
        height=args.image_size
    )
    
    generator.generate_dataset(
        num_images=args.num_images,
        text_source=args.text_source
    )


if __name__ == "__main__":
    main()


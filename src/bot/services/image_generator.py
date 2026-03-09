from PIL import Image, ImageDraw, ImageFont
import io
import os
from bot.utils.date_utils import get_russian_month

class StatsImageGenerator:
    # New dimensions based on stat_bg.jpg (768x1024)
    WIDTH = 768
    HEIGHT = 1024
    FONT_FILENAME = "Inter-Regular.ttf"
    BG_FILENAME = "stat_bg.jpg"

    def generate(self, user_data: dict, stats: dict) -> bytes:
        # Load background template
        bg_path = self._get_file_path("assets", self.BG_FILENAME)
        if bg_path and os.path.exists(bg_path):
            img = Image.open(bg_path).convert('RGB')
        else:
            img = Image.new('RGB', (self.WIDTH, self.HEIGHT), '#E0F2F1')
            
        draw = ImageDraw.Draw(img)
        
        self._draw_header(draw, user_data)
        self._draw_stats_summary(draw, stats)
        
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG', quality=95)
        return img_byte_arr.getvalue()

    def _get_file_path(self, folder: str, filename: str):
        paths = [
            os.path.join(folder, filename),
            os.path.join(os.getcwd(), folder, filename),
            os.path.join(os.path.dirname(__file__), "../../../", folder, filename),
            f"/app/{folder}/{filename}",
            f"/Users/bozhenkas/Documents/code/daywith/{folder}/{filename}"
        ]
        if folder == "assets":
            paths.extend([
                os.path.join("assets/fonts", filename),
                os.path.join(os.getcwd(), "assets/fonts", filename),
                os.path.join(os.path.dirname(__file__), "../../../assets/fonts", filename),
            ])

        for p in paths:
            if os.path.exists(p):
                return p
        return None

    def _get_font(self, size: int):
        font_path = self._get_file_path("assets", self.FONT_FILENAME)
        if font_path:
            try:
                return ImageFont.truetype(font_path, size)
            except Exception as e:
                print(f"Error loading font {font_path}: {e}")
        
        print("WARNING: Could not load Inter font, falling back to default")
        return ImageFont.load_default()

    def _draw_text_with_spacing(self, draw: ImageDraw, position: tuple, text: str, font, fill: str, spacing_percent: float = -0.04):
        x, y = position
        for char in text:
            draw.text((x, y), char, font=font, fill=fill)
            try:
                char_width = font.getlength(char)
            except:
                char_width = 10 
            x += char_width * (1 + spacing_percent)
        return x

    def _draw_header(self, draw: ImageDraw, user_data: dict):
        username = user_data.get("username", "user") if user_data else "user"
        font_title = self._get_font(88)
        font_tag = self._get_font(32)
        
        # Position from Figma: "статистика" top-leftish
        self._draw_text_with_spacing(draw, (55, 140), "статистика", font_title, "#333333")
        # "for @username" smaller
        self._draw_text_with_spacing(draw, (230, 240), f"for @{username}", font_tag, "#333333")

    def _draw_stats_summary(self, draw: ImageDraw, stats: dict):
        rate = stats.get("completion_rate", 0)
        month = get_russian_month()
        
        font_label = self._get_font(64)
        font_value = self._get_font(64)
        
        # Block: Monthly progress
        self._draw_text_with_spacing(draw, (55, 410), f"за месяц ({month})", font_label, "#333333")
        self._draw_text_with_spacing(draw, (180, 480), f"успешность — {rate:.0f}%", font_value, "#169D8B")

        # Block: Best habit
        self._draw_text_with_spacing(draw, (55, 680), "лучшая привычка", font_label, "#333333")
        
        best = stats.get("best_habit")
        if best:
            best_name = best.get("name", "без названия")
            self._draw_text_with_spacing(draw, (280, 750), best_name, font_value, "#EE6C4D")
        else:
            self._draw_text_with_spacing(draw, (280, 750), "нет данных", font_value, "#EE6C4D")

from PIL import Image, ImageDraw, ImageFont
import io
import os
from bot.utils.date_utils import get_russian_month

class StatsImageGenerator:
    # New dimensions based on stat_bg.jpg (768x1024)
    WIDTH = 768
    HEIGHT = 1024
    FONT_FILENAME = "Inter-Regular.ttf"
    FONT_ITALIC_FILENAME = "Inter-Italic.ttf"
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

    def _get_font(self, size: int, italic=True):
        # Prefer italic if requested
        filenames = [self.FONT_ITALIC_FILENAME, self.FONT_FILENAME] if italic else [self.FONT_FILENAME]
        
        for filename in filenames:
            font_path = self._get_file_path("assets", filename)
            if font_path:
                try:
                    return ImageFont.truetype(font_path, size)
                except Exception as e:
                    print(f"Error loading font {font_path}: {e}")
        
        # Fallback to variable font if exists
        v_path = self._get_file_path("assets", "Inter-Variable.ttf")
        if v_path:
             return ImageFont.truetype(v_path, size)

        print("WARNING: Could not load Inter font, falling back to default")
        return ImageFont.load_default()

    def _draw_text_with_spacing(self, draw: ImageDraw, position: tuple, text: str, font, fill: str, spacing_px: float, align="left", container_width=0):
        text = text.lower()
        # Calculate width for alignment
        chars = list(text)
        widths = []
        for char in chars:
            try:
                widths.append(font.getlength(char))
            except:
                widths.append(font.size * 0.5)
        
        total_text_width = sum(widths) + (len(chars) - 1) * spacing_px
        
        start_x, y = position
        if align == "right" and container_width > 0:
            start_x = start_x + container_width - total_text_width
            
        current_x = start_x
        for i, char in enumerate(chars):
            draw.text((current_x, y), char, font=font, fill=fill)
            current_x += widths[i] + spacing_px
        return total_text_width

    def _draw_header(self, draw: ImageDraw, user_data: dict):
        username = user_data.get("username", "user") if user_data else "user"
        font_80 = self._get_font(80, italic=True)
        font_32 = self._get_font(32, italic=True)
        
        # Container start
        base_x, base_y = 60, 60
        container_w = 648
        
        # "статистика"
        self._draw_text_with_spacing(draw, (base_x, base_y), "статистика", font_80, "#2A2D43", -4)
        
        # "for @username" - gap 20px, right aligned
        self._draw_text_with_spacing(draw, (base_x, base_y + 80 + 20), f"for @{username}", font_32, "#2A2D43", -2.238, align="right", container_width=container_w)

    def _draw_stats_summary(self, draw: ImageDraw, stats: dict):
        rate = stats.get("completion_rate", 0)
        month = get_russian_month()
        font_60 = self._get_font(60, italic=True)
        
        # Monthly Block
        base_x, base_y = 60, 410
        container_w = 626
        
        # "за месяц (месяц)"
        self._draw_text_with_spacing(draw, (base_x, base_y), f"за месяц ({month})", font_60, "#2A2D43", -4)
        
        # "успешность – x%" - gap 20px, right aligned
        self._draw_text_with_spacing(draw, (base_x, base_y + 60 + 20), f"успешность – {rate:.0f}%", font_60, "#127475", -4, align="right", container_width=container_w)

        # Best Habit Block
        base_x, base_y = 60, 680
        container_w = 648
        
        # "лучшая привычка"
        self._draw_text_with_spacing(draw, (base_x, base_y), "лучшая привычка", font_60, "#2A2D43", -4)
        
        best = stats.get("best_habit")
        val_text = best.get("name") if best else "нет данных"
        # Best habit name - gap 20px, right aligned
        self._draw_text_with_spacing(draw, (base_x, base_y + 60 + 20), val_text, font_60, "#DD614A", -4, align="right", container_width=container_w)

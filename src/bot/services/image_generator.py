from PIL import Image, ImageDraw, ImageFont
import io

class StatsImageGenerator:
    WIDTH = 1080
    HEIGHT = 1920
    # Paths to try
    FONT_FILENAME = "Inter-Regular.ttf"

    def generate(self, user_data: dict, stats: dict) -> bytes:
        img = Image.new('RGB', (self.WIDTH, self.HEIGHT), '#1E1E1E')
        draw = ImageDraw.Draw(img)
        
        self._draw_header(draw, user_data)
        self._draw_stats_summary(draw, stats)
        
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        return img_byte_arr.getvalue()

    def _get_font(self, size: int):
        import os
        # Try several locations
        paths = [
            os.path.join("assets/fonts", self.FONT_FILENAME),
            os.path.join(os.getcwd(), "assets/fonts", self.FONT_FILENAME),
            os.path.join(os.path.dirname(__file__), "../../../assets/fonts", self.FONT_FILENAME),
            # Host fallback for local testing if not in docker
            f"/Users/bozhenkas/Documents/code/daywith/assets/fonts/{self.FONT_FILENAME}"
        ]
        
        for p in paths:
            if os.path.exists(p):
                try:
                    return ImageFont.truetype(p, size)
                except Exception as e:
                    print(f"Error loading font {p}: {e}")
                    continue
        
        print("WARNING: Could not load Inter font, falling back to default")
        return ImageFont.load_default()

    def _draw_text_with_spacing(self, draw: ImageDraw, position: tuple, text: str, font, fill: str, spacing_percent: float = -0.04):
        x, y = position
        for char in text:
            draw.text((x, y), char, font=font, fill=fill)
            # Calculate width and apply negative spacing
            try:
                char_width = font.getlength(char)
            except:
                char_width = 10 # fallback
            x += char_width * (1 + spacing_percent)

    def _draw_header(self, draw: ImageDraw, user_data: dict):
        username = user_data.get("username", "user") if user_data else "user"
        font_main = self._get_font(120)
        font_sub = self._get_font(70)
        
        self._draw_text_with_spacing(draw, (100, 200), "day with...", font_main, "#FFFFFF")
        self._draw_text_with_spacing(draw, (100, 320), f"@{username}", font_sub, "#9E9E9E")

    def _draw_stats_summary(self, draw: ImageDraw, stats: dict):
        rate = stats.get("completion_rate", 0)
        font_title = self._get_font(90)
        font_stat = self._get_font(70)
        
        self._draw_text_with_spacing(draw, (100, 600), "Статистика за месяц", font_title, "#FFFFFF")
        self._draw_text_with_spacing(draw, (100, 720), f"Успешность: {rate:.1f}%", font_stat, "#4CAF50")

        best = stats.get("best_habit")
        if best:
            best_name = best.get("name", "без названия")
            streak = best.get("streak", 0)
            self._draw_text_with_spacing(draw, (100, 900), "лучшая привычка:", font_stat, "#9E9E9E")
            self._draw_text_with_spacing(draw, (100, 990), f"{best_name} ({streak}🔥)", font_stat, "#FF9800")
        else:
            self._draw_text_with_spacing(draw, (100, 900), "лучшая привычка:", font_stat, "#9E9E9E")
            self._draw_text_with_spacing(draw, (100, 990), "нет данных", font_stat, "#FF9800")

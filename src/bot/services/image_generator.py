from PIL import Image, ImageDraw, ImageFont
import io

class StatsImageGenerator:
    WIDTH = 1080
    HEIGHT = 1920

    def generate(self, user_data: dict, stats: dict) -> bytes:
        img = Image.new('RGB', (self.WIDTH, self.HEIGHT), '#1E1E1E')
        draw = ImageDraw.Draw(img)
        
        self._draw_header(draw, user_data)
        self._draw_stats_summary(draw, stats)
        
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        return img_byte_arr.getvalue()

    def _draw_header(self, draw: ImageDraw, user_data: dict):
        username = user_data.get("username", "User")
        draw.text((100, 150), f"Davis Tracker", fill="#FFFFFF", font_size=80)
        draw.text((100, 250), f"@{username}", fill="#9E9E9E", font_size=50)

    def _draw_stats_summary(self, draw: ImageDraw, stats: dict):
        rate = stats.get("completion_rate", 0)
        draw.text((100, 450), "Статистика за месяц", fill="#FFFFFF", font_size=60)
        draw.text((100, 550), f"Успешность: {rate:.1f}%", fill="#4CAF50", font_size=50)

        best = stats.get("best_habit")
        if best:
            draw.text((100, 650), f"Лучшая привычка:\n{best['name']} ({best['streak']}🔥)", fill="#FF9800", font_size=50)

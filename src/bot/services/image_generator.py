import os
import logging
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ImageGenerator:
    def __init__(self, assets_path: str):
        self.assets_path = assets_path
        # Use a default system font if specialized one not found
        try:
            self.font_main = ImageFont.truetype(os.path.join(assets_path, "fonts", "Roboto-Regular.ttf"), 24)
            self.font_bold = ImageFont.truetype(os.path.join(assets_path, "fonts", "Roboto-Bold.ttf"), 32)
            self.font_small = ImageFont.truetype(os.path.join(assets_path, "fonts", "Roboto-Light.ttf"), 18)
        except Exception:
            self.font_main = ImageFont.load_default()
            self.font_bold = ImageFont.load_default()
            self.font_small = ImageFont.load_default()

    async def generate_stats_image(self, user_id: int, stats: dict, calendar_data: dict) -> str:
        width, height = 800, 600
        image = Image.new("RGB", (width, height), color=(245, 247, 250))
        draw = ImageDraw.Draw(image)

        self._draw_header(draw, width)
        self._draw_stats_summary(draw, stats, 50, 120)
        self._draw_calendar_heatmap(draw, calendar_data, 50, 300)

        output_path = f"/tmp/stats_{user_id}_{int(datetime.utcnow().timestamp())}.png"
        image.save(output_path)
        return output_path

    def _draw_header(self, draw: ImageDraw, width: int):
        draw.rectangle([0, 0, width, 80], fill=(44, 62, 80))
        draw.text((width // 2, 40), "HABIT TRACKER", fill=(255, 255, 255), font=self.font_bold, anchor="mm")

    def _draw_stats_summary(self, draw: ImageDraw, stats: dict, x: int, y: int):
        draw.text((x, y), f"Процент выполнения: {stats.get('completion_rate', 0):.1f}%", fill=(52, 73, 94), font=self.font_main)
        draw.text((x, y + 40), f"Лучшая привычка: {stats.get('best_habit', '—')}", fill=(52, 73, 94), font=self.font_main)
        draw.text((x, y + 80), f"Текущий стрик: {stats.get('streak', 0)} дней", fill=(52, 73, 94), font=self.font_main)

    def _draw_calendar_heatmap(self, draw: ImageDraw, calendar_data: dict, start_x: int, start_y: int):
        draw.text((start_x, start_y - 30), "Активность (последние 5 недель):", fill=(44, 62, 80), font=self.font_main)
        
        square_size = 30
        gap = 5
        
        # We draw 5 weeks (35 days)
        today = datetime.utcnow().date()
        start_date = today - timedelta(days=34)
        
        for i in range(35):
            current_date = start_date + timedelta(days=i)
            date_str = current_date.strftime("%Y-%m-%d")
            
            # Default color (empty)
            color = (224, 230, 235)
            
            if date_str in calendar_data:
                day_stats = calendar_data[date_str]
                total = day_stats.get("total", 0)
                completed = day_stats.get("completed", 0)
                
                if total > 0:
                    ratio = completed / total
                    if ratio > 0.8:
                        color = (39, 174, 96) # Green
                    elif ratio > 0.5:
                        color = (46, 204, 113) # Light green
                    elif ratio > 0:
                        color = (169, 223, 191) # Faint green
                    else:
                        color = (231, 76, 60) # Red (all missed)

            # Draw square
            week = i // 7
            day = i % 7
            x = start_x + week * (square_size + gap)
            y = start_y + day * (square_size + gap)
            
            draw.rectangle([x, y, x + square_size, y + square_size], fill=color)

        # Legend
        draw.text((start_x, start_y + 7 * (square_size + gap) + 10), "✓ - выполнено, ✗ - пропущено", fill=(127, 140, 141), font=self.font_small)

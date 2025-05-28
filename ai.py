import asyncio
import threading
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import re
from concurrent.futures import ThreadPoolExecutor


class LazyAIModel:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.model_path = "phamhai/Llama-3.2-1B-Instruct-Frog"
        self.loading = False
        self.loaded = False
        self._lock = threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=1)

    def _load_model(self):
        """Load model in a separate thread"""
        try:
            print("Loading AI model...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                device_map="auto",
                torch_dtype=torch.float16
            )
            self.loaded = True
            print("AI model loaded successfully!")
        except Exception as e:
            print(f"Error loading AI model: {e}")
            self.loaded = False
        finally:
            self.loading = False

    def ensure_loaded(self):
        """Ensure model is loaded, start loading if not"""
        with self._lock:
            if not self.loaded and not self.loading:
                self.loading = True
                # Start loading in background thread
                self.executor.submit(self._load_model)

    def is_ready(self):
        """Check if model is ready to use"""
        return self.loaded

    def generate_advice(self, temp_c, wind_kmh, humidity_percent, weather_id):
        """Generate clothing advice using the AI model"""
        if not self.is_ready():
            return None

        description = translate_weather_desc(weather_id)
        prompt = (
            f"Hãy đưa ra lời khuyên mặc gì hôm nay với dữ liệu sau:\n"
            f"Trạng thái trời: {description}\n"
            f"Nhiệt độ: {temp_c:.0f}°C\n"
            f"Gió: {wind_kmh:.2f} km/h\n"
            f"Độ ẩm: {humidity_percent}%.\n"
            "Nhớ thêm gợi ý hoặc nhắc nhở hữu ích nếu cần."
        )

        messages = [
            {"role": "system", "content": (
                "Bạn là một chuyên gia thời tiết và đưa ra gợi ý trang phục ngắn gọn, rõ ràng cho người dùng dựa trên tình trạng thời tiết hiện tại. "
                "Chỉ gợi ý trong nhiều nhất là 2 câu."
                "Không được lặp từ hoặc lặp ý trong cùng một câu trả lời. "
                "Không nói 'áo len hoặc áo len'."
                "Không đề xuất mũ bảo hiểm, mũ len, áo len, găng tay."
                "Không nhắc đến kính râm hoặc chống nắng nếu trời âm u hoặc nhiều mây. "
            )},
            {"role": "user", "content": prompt}
        ]

        try:
            tokenized = self.tokenizer.apply_chat_template(
                messages, tokenize=True, add_generation_prompt=True, return_tensors="pt"
            ).to(self.model.device)

            outputs = self.model.generate(
                tokenized,
                max_new_tokens=250,
                do_sample=True,
                temperature=0.5,
                top_k=50,
                top_p=0.95,
                repetition_penalty=1.0,
                pad_token_id=self.tokenizer.eos_token_id
            )

            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return response.split("user")[1].split("assistant")[
                1].strip() if "assistant" in response else response.strip()
        except Exception as e:
            print(f"Error generating AI advice: {e}")
            return None


# Global lazy model instance
_ai_model = LazyAIModel()


def translate_weather_desc(weather_id):
    if 200 <= weather_id <= 232:
        return "Dông, sấm sét, có thể có mưa lớn"
    elif 300 <= weather_id <= 321:
        return "Mưa phùn hoặc mưa nhẹ"
    elif 500 <= weather_id <= 504:
        return "Mưa vừa hoặc mưa lớn"
    elif weather_id == 511:
        return "Mưa tuyết"
    elif 520 <= weather_id <= 531:
        return "Mưa rào hoặc mưa lớn rải rác"
    elif 600 <= weather_id <= 602:
        return "Tuyết rơi nhẹ đến vừa"
    elif 611 <= weather_id <= 616:
        return "Tuyết ướt hoặc mưa tuyết"
    elif 620 <= weather_id <= 622:
        return "Tuyết rơi dày"
    elif 701 <= weather_id <= 781:
        return "Sương mù hoặc hiện tượng khí quyển đặc biệt"
    elif weather_id == 800:
        return "Trời quang đãng, có nắng"
    elif weather_id == 801:
        return "Ít mây, nắng nhẹ, không có mưa, không có tuyết"
    elif weather_id == 802:
        return "Trời có mây rải rác, không có mưa, không có tuyết"
    elif weather_id == 803:
        return "Trời nhiều mây, không có mưa, không có tuyết"
    elif weather_id == 804:
        return "Trời âm u, mây dày đặc, không có tuyết"
    else:
        return "Trời đẹp"


def get_fallback_advice(temp_c, wind_kmh, humidity_percent, weather_id):
    """Fallback clothing advice when AI is not available"""
    description = translate_weather_desc(weather_id)

    if temp_c < 10:
        return f"Trời {description.lower()}, hãy mặc áo ấm và áo khoác dày. Nhớ đeo khăn quàng cổ."
    elif temp_c < 20:
        return f"Nhiệt độ mát mẻ với {description.lower()}, nên mặc áo dài tay và áo khoác nhẹ."
    elif temp_c < 30:
        return f"Thời tiết dễ chịu, {description.lower()}. Mặc áo thun hoặc sơ mi nhẹ là phù hợp."
    else:
        if humidity_percent > 70:
            return f"Trời nóng ẩm với {description.lower()}. Chọn quần áo cotton thoáng mát và mang theo nước."
        else:
            return f"Trời nóng, {description.lower()}. Mặc quần áo nhẹ, thoáng mát và đội mũ."


def get_clothing_advice(temp_c, wind_kmh, humidity_percent, weather_id):
    """Get clothing advice - uses AI if available, fallback otherwise"""
    # Ensure AI model starts loading
    _ai_model.ensure_loaded()

    # Try AI first if ready
    if _ai_model.is_ready():
        ai_advice = _ai_model.generate_advice(temp_c, wind_kmh, humidity_percent, weather_id)
        if ai_advice:
            return ai_advice

    # Use fallback advice
    return get_fallback_advice(temp_c, wind_kmh, humidity_percent, weather_id)


def is_ai_ready():
    """Check if AI model is ready"""
    return _ai_model.is_ready()


def preload_ai_model():
    """Manually trigger AI model loading"""
    _ai_model.ensure_loaded()
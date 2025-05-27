from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import re

model_path = "phamhai/Llama-3.2-1B-Instruct-Frog"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(model_path, device_map="auto", torch_dtype=torch.float16)

'''
def clean_response(text):
    # Xóa các cụm lặp như "áo len hoặc áo len"
    return re.sub(r"\b(\w+(?:\s\w+)*)\s+hoặc\s+\1\b", r"\1", text)
'''

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

def get_clothing_advice(temp_c, wind_kmh, humidity_percent, weather_id):
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
    #prev mess = "Bạn là một chuyên gia thời tiết. Báo cáo nên ngắn gọn, rõ ràng, tự nhiên, không lặp lại số liệu một cách máy móc, và có gợi ý phù hợp cho người đọc. Hãy chỉ đề xuất kính râm nếu trời nắng hoặc có ánh sáng mạnh."

    tokenized = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True, return_tensors="pt").to(model.device)
    outputs = model.generate(
        tokenized,
        max_new_tokens=250,
        do_sample=True,               # enables sampling
        temperature=0.5,              # controls randomness (lower = more focused)
        top_k=50,                     # top-k sampling
        top_p=0.95,                   # top-p (nucleus) sampling
        repetition_penalty=1.0,
        pad_token_id=tokenizer.eos_token_id
    )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response.split("user")[1].split("assistant")[1].strip() if "assistant" in response else response.strip()

    '''
    cleaned = clean_response(response)
    return cleaned.split("user")[1].split("assistant")[1].strip() if "assistant" in cleaned else cleaned.strip()
    '''
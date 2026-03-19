import os
import requests
import random
import urllib3
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_tips(temp, pop, weather):
    t, p = float(temp), int(pop)
    
    # --- 第一行：天氣與降雨 (每 10% 一級，五選一) ---
    if p >= 90:
        a = random.choice(["今日降雨極高，出門務必攜帶雨具。", "有大雨發生機率，請注意行車安全。", "雨勢強大，盡量待在室內確保安全。", "外出請備妥雨衣傘具，慎防淋濕。", "降雨機率極大，注意雷雨或強降雨。"])
    elif p >= 70:
        a = random.choice(["降雨機率高，出門記得帶傘。", "外面正在下雨，外出請多留意。", "有明顯雨勢，建議攜帶堅固雨具。", "降雨機率約七成，請備妥雨傘。", "天氣不穩定，出門請記得帶雨具。"])
    elif p >= 50:
        a = random.choice(["降雨機率過半，建議攜帶折疊傘。", "天空陰沉，局部地區會有陣雨。", "有一半機會下雨，出門帶傘較保險。", "可能會有短暫降雨，請多留意。", "天氣不穩，建議隨身攜帶雨具。"])
    elif p >= 30:
        a = random.choice(["降雨機率約三成，可考慮帶傘備用。", "局部地區可能有零星陣雨。", "天空雲量較多，有短暫雨機會。", "偶有陣雨，外出可帶把小傘。", "天氣稍不穩，注意氣象變化。"])
    elif p >= 10:
        a = random.choice(["降雨機率低，不帶傘應無大礙。", "天氣大致多雲，僅有極低降雨機率。", "偶爾有零星降雨，影響不大。", "大致為多雲天氣，降雨機會小。", "降雨機率輕微，不需過度擔心。"])
    else:
        a = random.choice(["天氣乾爽，不需要攜帶雨具。", "今日無雨，適合戶外活動。", "降雨機率為零，天氣非常晴朗。", "陽光充足，不需擔心下雨。", "天氣穩定，出門散步很合適。"])

    # --- 第二行：氣溫與穿搭 (每 2-3 度一級，五選一) ---
    if t < 13:
        b = random.choice(["氣溫極低，請務必穿著厚大衣保暖。", "寒流來襲，請多加衣物避免感冒。", "天氣寒冷，記得戴上圍巾與手套。", "低溫特報，請注意家中長輩保暖。", "穿上羽絨衣或厚重外套，預防凍傷。"])
    elif t < 16:
        b = random.choice(["天氣冷涼，請穿著厚外套保暖。", "氣溫偏低，建議穿著毛衣或夾克。", "早晚冷空氣明顯，請注意保暖。", "請穿著保暖衣物，預防受寒。", "冷氣團影響，外出請注意防風。"])
    elif t < 19:
        b = random.choice(["天氣涼爽，建議穿著薄外套或長袖。", "氣溫適中偏涼，注意早晚溫差。", "洋蔥式穿法最合適，方便增減衣物。", "穿著長袖上衣，搭配一件外套。", "天氣略有涼意，請適時添加衣物。"])
    elif t < 22:
        b = random.choice(["溫度舒適，穿著一般長袖即可。", "氣溫宜人，是一年中最舒服的天氣。", "穿著件長袖襯衫或衛衣即可出門。", "室內外溫差適中，穿搭輕鬆即可。", "天氣溫和，不冷不熱非常舒適。"])
    elif t < 25:
        b = random.choice(["體感微熱，穿著短袖即可。", "氣溫升高，建議穿著透氣輕便衣物。", "白天稍微熱一些，短袖是好選擇。", "建議穿著棉質透氣衣物。", "天氣晴朗微熱，出門注意防曬。"])
    elif t < 29:
        b = random.choice(["氣溫偏高，請穿著短袖並多補充水分。", "太陽較大，外出請注意遮陽防曬。", "天氣炎熱，請預防中暑。", "建議穿著涼爽衣物，並適時休息。", "戶外活動請多喝水，避免脫水。"])
    else:
        b = random.choice(["高溫炎熱，盡量待在陰涼處。", "酷暑來襲，請注意室內通風防暑。", "天氣極熱，非必要請減少戶外活動。", "請多補充水分，預防熱衰竭。", "熱力十足，外出記得攜帶遮陽傘。"])

    return f"\n 💡 提示：{a}\n 🧥 穿搭：{b}"

def get_weather():
    owm_key = os.getenv('OWM_TOKEN')
    line_key = os.getenv('LINE_TOKEN')
    group_id = os.getenv('GROUP_ID')
    lat, lon = 23.497, 121.376
    
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={owm_key}&units=metric&lang=zh_tw"
    
    try:
        res = requests.get(url, timeout=20).json()
        if res.get("cod") != "200": return

        target_slots = {"09:00:00": "早上 (08-12)", "15:00:00": "下午 (12-16)", "21:00:00": "傍晚 (16-20)"}
        msg_parts = [f"🍊 【瑞穗鄉】時段天氣預報", "===================="]
        found_count = 0

        for item in res['list']:
            dt_txt = item['dt_txt']
            date_display = dt_txt[5:10].replace('-', '/')
            time_part = dt_txt[11:19]

            if time_part in target_slots and found_count < 3:
                slot_name = target_slots[time_part]
                temp = round(item['main']['temp'], 1)
                wx = item['weather'][0]['description']
                pop = int(item.get('pop', 0) * 100)
                
                msg_parts.append(f"🕒 {date_display} {slot_name}")
                msg_parts.append(f"☁️ 天氣：{wx}")
                msg_parts.append(f"🌡️ 氣溫：{temp}°C | ☔ 降雨：{pop}%")
                msg_parts.append(get_tips(temp, pop, wx))
                msg_parts.append("-" * 20)
                found_count += 1

        final_msg = "\n".join(msg_parts).strip("- \n")

        if line_key and group_id:
            headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {line_key}'}
            payload = {"to": group_id, "messages": [{"type": "text", "text": final_msg}]}
            requests.post('https://api.line.me/v2/bot/message/push', headers=headers, json=payload)
        else:
            print(final_msg)

    except Exception as e:
        print(f"💥 錯誤: {e}")

if __name__ == "__main__":
    get_weather()

import os
import requests
import random

def get_weather():
    cwa_key = os.getenv('CWA_TOKEN')
    line_key = os.getenv('LINE_TOKEN')

    # 花蓮縣 API (F-D0047-043)
    url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-043?Authorization={cwa_key}"

    try:
        res = requests.get(url).json()

        records = res.get('records', {})
        locations_list = records.get('Locations', []) 
        
        target_loc = None
        for loc_data in locations_list:
            for loc in loc_data.get('Location', []):
                if loc.get('LocationName', '') == '瑞穗鄉':
                    target_loc = loc
                    break
            if target_loc: break

        if not target_loc:
            print("❌ 找不到瑞穗鄉的資料")
            return

        elements = target_loc.get('WeatherElement', [])
        wx_data, pop_data, t_data = [], [], []

        # 【關鍵修正】同時支援簡寫與全名，確保一定抓得到資料！
        for e in elements:
            name = e.get('ElementName', '')
            if name in ['Wx', 'Weather']:
                wx_data = e.get('Time', [])
            elif name in ['PoP12h', 'ProbabilityOfPrecipitation']:
                pop_data = e.get('Time', [])
            elif name in ['T', 'Temperature']:
                t_data = e.get('Time', [])

        def extract_val(data_list, i):
            try:
                # 暴力抓取裡面的數值
                return str(list(data_list[i]['ElementValue'][0].values())[0])
            except:
                return "未知"

        msg_lines = ["🍊 【瑞穗鄉】當日天氣預報", "===================="]
        max_pop = 0
        temps = []

        for i in range(3):
            # 處理時間 (例如把 2026-03-14T06:00:00 轉為 03-14 06:00)
            try:
                start_time = wx_data[i]['StartTime'][5:16].replace('T', ' ')
            except:
                start_time = ["早上", "下午", "晚上"][i]

            wx = extract_val(wx_data, i)
            t = extract_val(t_data, i)
            
            # 避免降雨機率的資料格數比溫度少，做個安全防護
            pop_idx = i if i < len(pop_data) else -1
            pop = extract_val(pop_data, pop_idx)

            if pop.isdigit(): max_pop = max(max_pop, int(pop))
            if t.isdigit(): temps.append(int(t))

            display_pop = pop if pop.isdigit() else "0"

            msg_lines.append(f"🕒 {start_time}")
            msg_lines.append(f"☁️ 狀況：{wx}")
            msg_lines.append(f"🌡️ 氣溫：{t}°C | ☔ 降雨：{display_pop}%")
            msg_lines.append("--------------------")

        msg_lines.append("💡 暖心提醒：")
        
        # 降雨判斷
        if max_pop >= 30:
            msg_lines.append(random.choice([
                "☔ 出門記得帶把傘，別被雨神突襲了！",
                "🌧️ 降雨機率偏高，包包裡塞把傘準沒錯！",
                "🦆 今天可能會下雨，不想變落湯雞就帶傘吧！"
            ]))
        else:
            msg_lines.append(random.choice([
                "☀️ 今天天氣穩定，出門不用帶傘喔！",
                "✨ 降雨機率低，是個乾爽的好日子！",
                "😎 沒什麼雨，盡情享受瑞穗的陽光吧！"
            ]))

        # 溫度判斷
        avg_t = sum(temps) / len(temps) if temps else 20
        if avg_t <= 18:
            msg_lines.append(random.choice([
                "🧣 天氣有點冷，記得穿厚一點，別感冒了！",
                "🧥 瑞穗風冷冷的，保暖外套不可少！",
                "☕ 氣溫偏低，多喝點熱水暖暖身子！"
            ]))
        elif avg_t >= 28:
            msg_lines.append(random.choice([
                "🥤 今天蠻熱的，記得多喝水補充水分喔！",
                "🕶️ 氣溫偏高，出門注意防曬別中暑了！",
                "👕 有點悶熱，穿透氣一點比較舒服！"
            ]))
        else:
            msg_lines.append(random.choice([
                "🌸 氣溫很舒適，是很棒的一天！",
                "🍃 不冷不熱，真是個出遊的好天氣！"
            ]))

        final_msg = "\n".join(msg_lines)

        # 廣播模式，自動發到群組
        line_url = 'https://api.line.me/v2/bot/message/broadcast'
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {line_key}'}
        payload = {"messages": [{"type": "text", "text": final_msg}]}
        
        requests.post(line_url, headers=headers, json=payload)
        print("發送成功")

    except Exception as e:
        print(f"錯誤: {e}")

if __name__ == "__main__":
    get_weather()
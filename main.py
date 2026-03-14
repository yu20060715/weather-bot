import os
import requests
import random

def get_weather():
    cwa_key = os.getenv('CWA_TOKEN')
    line_key = os.getenv('LINE_TOKEN')

    # 改回花蓮縣正確代碼 043，並指定瑞穗鄉
    url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-043?Authorization={cwa_key}&locationName=瑞穗鄉"

    try:
        res = requests.get(url).json()
        
        # 深入挖掘 JSON 層級
        # records -> Locations[0] -> Location[0] (因為指定了瑞穗，所以選第一個)
        records = res.get('records', {})
        locations = records.get('Locations', [{}])[0]
        location = locations.get('Location', [{}])[0]
        elements = location.get('WeatherElement', [])

        if not elements:
            print("❌ 抓不到天氣元素，請檢查 API 代碼是否為 043")
            return

        # 建立數據地圖，把標籤全部轉成小寫方便對比
        weather_map = {e['ElementName']: e['Time'] for e in elements}

        # 這裡根據你的氣象.txt 結構進行精準對位
        # 氣象署在 043/071 結構中，標籤可能是 'Weather' 或 'Wx'
        wx_list = weather_map.get('Weather') or weather_map.get('Wx')
        t_list = weather_map.get('Temperature') or weather_map.get('T')
        pop_list = weather_map.get('ProbabilityOfPrecipitation') or weather_map.get('PoP12h')

        def get_val(data_list, i):
            try:
                # 氣象署結構：ElementValue[0] 裡面可能叫 'value' 或 'Weather' 或 'Temperature'
                # 我們直接取字典裡的第一個數值
                val_obj = data_list[i]['ElementValue'][0]
                return str(list(val_obj.values())[0])
            except:
                return "無資料"

        msg_lines = ["🍊 【瑞穗鄉】今日早中晚預報", "===================="]
        max_pop = 0
        temps = []

        for i in range(3):
            time_str = ["早上", "下午", "晚上"][i]
            wx = get_val(wx_list, i)
            t = get_val(t_list, i)
            pop = get_val(pop_list, i//2) # 降雨通常是 12h 一跳

            if t.isdigit(): temps.append(int(t))
            if pop.isdigit(): max_pop = max(max_pop, int(pop))

            msg_lines.append(f"🕒 {time_str}\n☁️ 狀況：{wx}\n🌡️ 氣溫：{t}°C | ☔ 降雨：{pop}%")
            msg_lines.append("--------------------")

        # 趣味提醒
        msg_lines.append("💡 暖心小語：")
        if max_pop >= 30:
            msg_lines.append(random.choice(["☔ 下雨機率高，傘要帶好喔！", "🌧️ 記得帶傘，別淋濕感冒了！"]))
        else:
            msg_lines.append(random.choice(["☀️ 天氣不錯，適合出門走走！", "😎 陽光普照，心情也要美美的！"]))

        avg_t = sum(temps)/len(temps) if temps else 22
        if avg_t < 18:
            msg_lines.append("🧣 氣溫偏低，多穿一點保暖喔！")
        elif avg_t > 28:
            msg_lines.append("🥤 天氣悶熱，記得多喝水補充水分！")
        else:
            msg_lines.append("🍃 氣溫舒適，祝你有個美好的一天！")

        # 發送廣播
        line_url = 'https://api.line.me/v2/bot/message/broadcast'
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {line_key}'}
        payload = {"messages": [{"type": "text", "text": "\n".join(msg_lines)}]}
        
        r = requests.post(line_url, headers=headers, json=payload)
        print(f"發送狀態: {r.status_code}")

    except Exception as e:
        print(f"解析出錯: {e}")

if __name__ == "__main__":
    get_weather()
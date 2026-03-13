import os
import requests
import random

def get_weather():
    cwa_key = os.getenv('CWA_TOKEN')
    line_key = os.getenv('LINE_TOKEN')

    # 【修正 1】改用 F-D0047-043 (這才是真正的花蓮縣預報！)
    url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-043?Authorization={cwa_key}"

    try:
        res = requests.get(url).json()

        # 【修正 2】根據你提供的 txt，完全對齊大寫開頭的結構
        records = res.get('records', {})
        locations_list = records.get('Locations', []) 
        
        target_loc = None
        for loc_data in locations_list:
            for loc in loc_data.get('Location', []):
                # 尋找瑞穗鄉
                if loc.get('LocationName', '') == '瑞穗鄉':
                    target_loc = loc
                    break
            if target_loc: break

        if not target_loc:
            print("❌ 還是找不到瑞穗鄉，請檢查 API 資料庫")
            return

        elements = target_loc.get('WeatherElement', [])
        wx_data, pop_data, t_data = [], [], []

        # 分類抓取：Wx(天氣)、PoP12h(降雨機率)、T(溫度)
        for e in elements:
            name = e.get('ElementName', '')
            if name == 'Wx': wx_data = e.get('Time', [])
            elif name == 'PoP12h': pop_data = e.get('Time', [])
            elif name == 'T': t_data = e.get('Time', [])

        # 寫一個萬用小工具，無視氣象署亂改標籤名稱，直接硬拔出數值
        def extract_val(data_list, i):
            try:
                # 直接抓 ElementValue 裡面的第一個值
                return list(data_list[i]['ElementValue'][0].values())[0]
            except:
                return "0"

        msg_lines = ["🍊 【瑞穗鄉】當日天氣預報", "===================="]
        max_pop = 0
        temps = []

        # 抓取早中晚 3 個時段
        for i in range(3):
            # 處理時間文字 (將 2026-03-14T06:00:00 轉為 03-14 06:00)
            try:
                start_time = wx_data[i]['StartTime'][5:16].replace('T', ' ')
            except:
                start_time = ["早上", "下午", "晚上"][i]

            wx = extract_val(wx_data, i)
            t = extract_val(t_data, i)
            pop = extract_val(pop_data, i)

            # 記錄最高降雨機率與所有氣溫，供後續趣味提醒判斷
            if pop.isdigit(): max_pop = max(max_pop, int(pop))
            if t.isdigit(): temps.append(int(t))

            msg_lines.append(f"🕒 {start_time}")
            msg_lines.append(f"☁️ 狀況：{wx}")
            msg_lines.append(f"🌡️ 氣溫：{t}°C | ☔ 降雨：{pop}%")
            msg_lines.append("--------------------")

        # ==========================================
        # 【新增功能】亂數趣味提醒 (冷/熱/下雨)
        # ==========================================
        msg_lines.append("💡 暖心提醒：")
        
        # 1. 降雨判斷
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

        # 2. 溫度判斷
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

        # 廣播模式 (發給所有加好友的人與所在群組)
        line_url = 'https://api.line.me/v2/bot/message/broadcast'
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {line_key}'}
        payload = {"messages": [{"type": "text", "text": final_msg}]}
        
        r = requests.post(line_url, headers=headers, json=payload)
        print(f"✅ 發送成功！狀態碼: {r.status_code}")

    except Exception as e:
        print(f"❌ 發生錯誤: {e}")

if __name__ == "__main__":
    get_weather()
import os
import requests
import random

def get_weather():
    cwa_key = os.getenv('CWA_TOKEN')
    line_key = os.getenv('LINE_TOKEN')

    # 網址保持抓取全花蓮 (043)，這最穩定
    url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-043?Authorization={cwa_key}"

    try:
        res = requests.get(url).json()
        
        # 1. 定位 Location 清單
        records = res.get('records', {})
        locations = records.get('Locations', [{}])[0].get('Location', [])
        
        # 2. 尋找瑞穗鄉
        target_loc = None
        for loc in locations:
            if loc.get('LocationName') == '瑞穗鄉':
                target_loc = loc
                break
        
        if not target_loc:
            print("❌ 找不到瑞穗鄉，目前有的地點是:", [l.get('LocationName') for l in locations])
            return

        # 3. 萬用抓取函式：不論標籤叫什麼，只要包含關鍵字就抓
        def find_element_data(keywords):
            for e in target_loc.get('WeatherElement', []):
                name = e.get('ElementName', '')
                # 如果標籤名包含關鍵字 (例如 "T" 或 "Temperature")
                if any(k in name for k in keywords):
                    return e.get('Time', [])
            return []

        # 抓取三種核心數據
        wx_times = find_element_data(['Weather', 'Wx'])
        t_times = find_element_data(['Temperature', 'T'])
        pop_times = find_element_data(['ProbabilityOfPrecipitation', 'PoP'])

        def extract_val(times, i):
            try:
                # 氣象署結構：取 ElementValue[0] 裡面的第一個數值
                val_dict = times[i]['ElementValue'][0]
                # 排除 Measures (單位)，取出真正的數值
                for k, v in val_dict.items():
                    if k != 'Measures': return str(v)
            except:
                return "無資料"

        # 4. 組裝訊息
        msg_parts = ["🍊 【瑞穗鄉】天氣預報", "===================="]
        temps = []
        
        for i in range(3):
            # 取得時間 (截取字串呈現)
            try:
                time_str = t_times[i]['StartTime'][11:16]
            except:
                time_str = f"時段 {i+1}"
            
            wx = extract_val(wx_times, i)
            t = extract_val(t_times, i)
            pop = extract_val(pop_times, i)
            
            if t.replace('-','').isdigit(): temps.append(int(t))
            
            msg_parts.append(f"🕒 {time_str}\n☁️ {wx}\n🌡️ {t}°C | ☔ 降雨：{pop}%")
            msg_parts.append("--------------------")

        msg_parts.append("💡 提醒：")
        msg_parts.append("多喝水、保持好心情！✨")

        final_msg = "\n".join(msg_parts)
        
        # 5. LINE 發送
        line_url = 'https://api.line.me/v2/bot/message/broadcast'
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {line_key}'}
        payload = {"messages": [{"type": "text", "text": final_msg}]}
        
        r = requests.post(line_url, headers=headers, json=payload)
        print(f"✅ 發送狀態: {r.status_code}")
        print("內容預覽：\n", final_msg)

    except Exception as e:
        import traceback
        print(f"💥 解析失敗詳情:\n{traceback.format_exc()}")

if __name__ == "__main__":
    get_weather()   
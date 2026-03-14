import os
import requests
import random

def get_weather():
    cwa_key = os.getenv('CWA_TOKEN')
    line_key = os.getenv('LINE_TOKEN')

    # 使用花蓮縣 API，並指定瑞穗鄉
    url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-043?Authorization={cwa_key}&locationName=瑞穗鄉"

    try:
        res = requests.get(url).json()
        
        # 定位到瑞穗鄉的 WeatherElement 列表
        # 氣象署 043 代碼結構：records -> Locations[0] -> Location[0]
        locations = res.get('records', {}).get('Locations', [{}])[0]
        location = locations.get('Location', [{}])[0]
        elements = location.get('WeatherElement', [])

        if not elements:
            print("❌ 無法定位瑞穗鄉資料，請確認 API 授權碼。")
            return

        # --- 核心算法：萬用提取器 ---
        def get_value_smart(target_names, time_idx):
            """
            target_names: 可能的標籤名列表 (例如 ['Temperature', 'T'])
            time_idx: 時段索引
            """
            for e in elements:
                # 1. 找到對應的元素 (如: 溫度)
                if e.get('ElementName') in target_names:
                    times = e.get('Time', [])
                    if len(times) > time_idx:
                        val_obj = times[time_idx].get('ElementValue', [{}])[0]
                        # 2. 關鍵修正：遍歷字典，抓取第一個「純數值」的內容
                        # 避開 'Measures' (單位) 標籤
                        for k, v in val_obj.items():
                            if k.lower() != 'measures':
                                return str(v)
            return "N/A"

        # --- 開始組合訊息 ---
        msg_parts = ["🍊 【瑞穗鄉】今日早中晚預報", "===================="]
        
        # 準備判斷數據
        temps = []
        max_pop = 0

        # 抓取前三個時段
        for i in range(3):
            time_label = ["早上", "下午", "晚上"][i]
            
            # 這裡傳入你 txt 裡看到的標籤全名
            wx = get_value_smart(['Weather', 'Wx'], i)
            temp = get_value_smart(['Temperature', 'T'], i)
            pop = get_value_smart(['ProbabilityOfPrecipitation', 'PoP12h'], i)

            # 記錄數值供提醒使用
            if temp.isdigit(): temps.append(int(temp))
            if pop.isdigit(): max_pop = max(max_pop, int(pop))

            msg_parts.append(f"🕒 {time_label}\n☁️ 狀況：{wx}\n🌡️ 氣溫：{temp}°C | ☔ 降雨：{pop}%")
            msg_parts.append("--------------------")

        # --- 隨機趣味提醒 ---
        msg_parts.append("💡 暖心小語：")
        if max_pop >= 30:
            msg_lines = ["☔ 出門帶把傘，別被瑞穗的雨突襲了！", "🌧️ 降雨機率高，傘是你的本體喔！"]
        else:
            msg_lines = ["☀️ 天氣穩定，適合去牧場看牛！", "😎 陽光正好，心情也要美美的！"]
        msg_parts.append(random.choice(msg_lines))

        if temps and sum(temps)/len(temps) < 18:
            msg_parts.append("🧣 瑞穗風大，記得多穿一件外套！")
        else:
            msg_parts.append("🥤 記得多喝水，維持一天好體力！")

        # --- 發送 ---
        final_msg = "\n".join(msg_parts)
        line_url = 'https://api.line.me/v2/bot/message/broadcast'
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {line_key}'}
        payload = {"messages": [{"type": "text", "text": final_msg}]}
        
        r = requests.post(line_url, headers=headers, json=payload)
        print(f"✅ 發送狀態: {r.status_code}")
        print("發送內容預覽：\n", final_msg)

    except Exception as e:
        print(f"💥 發生未知錯誤: {e}")

if __name__ == "__main__":
    get_weather()
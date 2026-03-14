import os
import requests
import random
import urllib3

# 關閉 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_weather():

    cwa_key = os.getenv('CWA_TOKEN')
    line_key = os.getenv('LINE_TOKEN')
    group_id = os.getenv('GROUP_ID')

    # 1. 抓取花蓮全縣資料 (F-D0047-043)
    url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-043?Authorization={cwa_key}"
    
    try:
        # 這裡加入 verify=False 防止 GitHub 環境報 SSL 錯誤
        res = requests.get(url, verify=False, timeout=20).json()
        
        # 2. 定位瑞穗鄉
        locations = res['records']['Locations'][0]['Location']
        target_loc = next((l for l in locations if l['LocationName'] == '瑞穗鄉'), None)
        
        # 3. 提取天氣元素並轉為中文索引字典
        elements = {e['ElementName']: e['Time'] for e in target_loc['WeatherElement']}
        
        # 4. 提醒語邏輯函數
        def get_tips(temp, pop, weather):
            tips = []
            t, p = int(temp), int(pop)
            if p >= 30 or "雨" in weather:
                tips.append(random.choice(["外面下雨了，記得帶傘以免變落湯雞 ☔", "出門記得帶傘，瑞穗的雨總是來的很突然 🌧️"]))
            elif p >= 10:
                tips.append("天色陰陰的，保險起見帶把摺疊傘吧 🌂")
            
            if t <= 15:
                tips.append(random.choice(["氣溫很低，要穿厚外套喔 🧣", "真的冷，瑞穗的風不是開玩笑的 🧥"]))
            elif t <= 19:
                tips.append("微涼的天氣，穿件薄長袖比較舒服 🌸")
            elif t >= 28:
                tips.append("太陽很大，記得多喝水避免中暑 ☀️")
            
            if not tips: tips.append("天氣很棒，保持心情愉快！✨")
            return "\n 💡 提醒您: " + "\n        ".join(tips)

        # 5. 組裝訊息內容
        from datetime import datetime
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        # 建立一個暫存字典，用 StartTime 當 Key 來對齊所有資料
        # 這樣就能保證「這一格的時間」配對到「這一格的天氣」
        combined_data = {}

        # 1. 先抓溫度，順便過濾日期
        for t_item in elements['平均溫度']:
            st = t_item['StartTime']
            if st.startswith(today_str):
                combined_data[st] = {
                    'temp': t_item['ElementValue'][0]['Temperature'],
                    'time': st[11:16]
                }

        # 2. 根據 Key (時間) 把天氣和降雨塞進去
        for wx_item in elements['天氣現象']:
            st = wx_item['StartTime']
            if st in combined_data:
                combined_data[st]['wx'] = wx_item['ElementValue'][0]['Weather']

        for pop_item in elements['12小時降雨機率']:
            st = pop_item['StartTime']
            if st in combined_data:
                combined_data[st]['pop'] = pop_item['ElementValue'][0]['ProbabilityOfPrecipitation']

        # 3. 開始排序並輸出 (按時間先後)
        sorted_keys = sorted(combined_data.keys())
        msg_parts = [f"🍊 【瑞穗鄉】({today_str.replace('-', '/')}) 精準預報", "===================="]

        for i, k in enumerate(sorted_keys):
            item = combined_data[k]
            
            # 判斷顯示名稱
            if item['time'] == "06:00":
                display_time = "06:00 - 18:00 (今日白天)"
            else:
                display_time = "18:00 - 06:00 (今日晚上)"

            msg_parts.append(f"🕒 時段：{display_time}")
            msg_parts.append(f"☁️ 狀況：{item['wx']}")
            msg_parts.append(f"🌡️ 氣溫：{item['temp']}°C")
            msg_parts.append(f"☔ 降雨：{item['pop']}%")
            msg_parts.append(get_tips(item['temp'], item['pop'], item['wx']))
            
            if i < len(sorted_keys) - 1:
                msg_parts.append("-" * 20)

        final_msg = "\n".join(msg_parts)

        # 6. LINE 推播 (從 broadcast 改成 push)
        # 網址要改成 push 結尾
        line_url = 'https://api.line.me/v2/bot/message/push'
        
        headers = {
            'Content-Type': 'application/json', 
            'Authorization': f'Bearer {line_key}'
        }
        
        # payload 要加入 "to": group_id，指定發給群組
        payload = {
            "to": group_id, 
            "messages": [{"type": "text", "text": final_msg}]
        }
        
        response = requests.post(line_url, headers=headers, json=payload)
        print(f"✅ 群組發送狀態: {response.status_code}")
        if response.status_code != 200:
            print(f"❌ 錯誤原因: {response.text}")

    except Exception as e:
        print(f"💥 運行出錯: {e}")

if __name__ == "__main__":
    get_weather()
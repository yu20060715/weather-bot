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

        # 5. 組裝訊息內容 (嚴格過濾 06:00 與 18:00 版)
        combined = {}
        target_count = 0
        
        # 遍歷平均溫度，只抓取時間是 06:00 或 18:00 的時段，抓滿 2 個就停
        for t_item in elements['平均溫度']:
            st = t_item['StartTime']
            hour = st[11:16]
            
            # 嚴格判斷：只收 06:00 (白天) 跟 18:00 (晚上)
            if hour in ["06:00", "18:00"]:
                combined[st] = {
                    't': t_item['ElementValue'][0]['Temperature']
                }
                target_count += 1
                
            if target_count == 2:
                break

        # 根據剛剛抓到的時間點 st，去「降雨」和「天氣」找一模一樣時間的資料
        for st in combined.keys():
            wx_data = next((item for item in elements['天氣現象'] if item['StartTime'] == st), None)
            pop_data = next((item for item in elements['12小時降雨機率'] if item['StartTime'] == st), None)
            
            combined[st]['wx'] = wx_data['ElementValue'][0]['Weather'] if wx_data else "未知"
            combined[st]['pop'] = pop_data['ElementValue'][0]['ProbabilityOfPrecipitation'] if pop_data else "0"

        # 排序並輸出
        sorted_times = sorted(combined.keys())
        msg_parts = [f"🍊 【瑞穗鄉】最新天氣預報", "===================="]

        for i, st in enumerate(sorted_times):
            date_display = st[5:10].replace('-', '/')
            hour_display = st[11:16]
            
            # 絕對精準的標籤
            label = "白天" if hour_display == "06:00" else "晚上"
            time_range = "06:00-18:00" if hour_display == "06:00" else "18:00-06:00"
            
            data = combined[st]
            msg_parts.append(f"🕒 時段：{date_display} {time_range} ({label})")
            msg_parts.append(f"☁️ 狀況：{data['wx']}")
            msg_parts.append(f"🌡️ 氣溫：{data['t']}°C")
            msg_parts.append(f"☔ 降雨：{data['pop']}%")
            msg_parts.append(get_tips(data['t'], data['pop'], data['wx']))
            if i < len(sorted_times) - 1: # 最後一筆不加分隔線
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
import os
import requests

def get_weather():
    cwa_key = os.getenv('CWA_TOKEN')
    line_key = os.getenv('LINE_TOKEN')

    # 花蓮縣鄉鎮預報 API
    url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-071?Authorization={cwa_key}&locationName=瑞穗鄉"
    
    try:
        res = requests.get(url).json()
        location_data = res['records']['locations'][0]['location'][0]
        elements = location_data['weatherElement']
        
        # 取得未來三個時段 (0-6h, 6-12h, 12-18h)
        # 天氣現象 Wx
        wx = elements[6]['time']
        # 降雨機率 PoP12h (鄉鎮預報通常是12小時一段)
        pop_list = elements[0]['time']

        # 準備組合訊息
        periods = ["今日白天", "今晚明晨", "明日白天"]
        weather_msg = "🍊 花蓮【瑞穗鄉】詳細預報\n-------------------"
        
        should_bring_umbrella = False
        
        for i in range(3):
            time_range = periods[i]
            desc = wx[i]['elementValue'][0]['value']
            pop = pop_list[0 if i < 1 else 1]['elementValue'][0]['value'] # 鄉鎮預報降雨是12h一段
            
            weather_msg += f"\n【{time_range}】\n☁️ 天氣：{desc}\n☔ 降雨：{pop}%"
            
            if int(pop) > 30: # 只要任一時段降雨機率大於 30% 就提醒
                should_bring_umbrella = True

        weather_msg += "\n-------------------"
        if should_bring_umbrella:
            weather_msg += "\n⚠️ 瑞穗的朋友注意：今日降雨機率高，出門記得帶傘喔！"
        else:
            weather_msg += "\n☀️ 今日天氣不錯，祝你有個美好的一天！"

        # 改用 broadcast (廣播)，不用 User ID
        line_url = 'https://api.line.me/v2/bot/message/broadcast'
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {line_key}'}
        payload = {"messages": [{"type": "text", "text": weather_msg}]}
        
        requests.post(line_url, headers=headers, json=payload)

    except Exception as e:
        print(f"解析失敗: {e}")

if __name__ == "__main__":
    get_weather()
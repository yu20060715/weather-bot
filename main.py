import os
import requests

def get_weather():
    cwa_key = os.getenv('CWA_TOKEN')
    line_key = os.getenv('LINE_TOKEN')

    # 花蓮縣鄉鎮預報 API (瑞穗鄉)
    url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-071?Authorization={cwa_key}&locationName=瑞穗鄉"
    
    try:
        res = requests.get(url).json()
        location_data = res['records']['locations'][0]['location'][0]
        elements = location_data['weatherElement']
        
        # 解析未來三個時段 (通常是 0-12h, 12-24h, 24-36h)
        wx = elements[6]['time']      # 天氣現象
        pop_list = elements[0]['time'] # 降雨機率
        t_list = elements[1]['time']   # 平均氣溫

        msg = "🍊 花蓮【瑞穗鄉】今日天氣報報\n-------------------"
        umbrella_flag = False
        
        # 準備三個時段的標籤
        periods = ["今日白天", "今晚明晨", "明日白天"]

        for i in range(3):
            desc = wx[i]['elementValue'][0]['value']
            pop = pop_list[i]['elementValue'][0]['value']
            temp = t_list[i]['elementValue'][0]['value']
            
            msg += f"\n【{periods[i]}】\n🌡️ 溫度：{temp}°C\n☁️ 狀況：{desc}\n☔ 降雨：{pop}%"
            
            if int(pop) >= 30: # 只要有一個時段降雨 >= 30% 就提醒帶傘
                umbrella_flag = True
            msg += "\n"

        msg += "-------------------"
        if umbrella_flag:
            msg += "\n⚠️ 提醒：瑞穗今日有雨，出門記得帶傘喔！"
        else:
            msg += "\n☀️ 今日天氣穩定，祝你有個愉快的一天！"

        # 使用 broadcast 廣播給所有人/群組
        line_url = 'https://api.line.me/v2/bot/message/broadcast'
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {line_key}'}
        payload = {"messages": [{"type": "text", "text": msg}]}
        
        requests.post(line_url, headers=headers, json=payload)

    except Exception as e:
        print(f"發生錯誤: {e}")

if __name__ == "__main__":
    get_weather()
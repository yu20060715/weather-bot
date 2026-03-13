import os
import requests

def get_weather():
    cwa_key = os.getenv('CWA_TOKEN')
    line_key = os.getenv('LINE_TOKEN')
    # 這裡你可以填入多個 ID，用逗號隔開，例如：'USER_ID,GROUP_ID'
    # 目前我們先從環境變數抓你原本設定好的那個
    target_id = os.getenv('LINE_USER_ID') 

    url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-071?Authorization={cwa_key}&locationName=瑞穗鄉"
    
    try:
        res = requests.get(url).json()
        location_data = res['records']['locations'][0]['location'][0]
        elements = location_data['weatherElement']
        
        wx = elements[6]['time']
        pop_list = elements[0]['time']
        t_list = elements[1]['time']

        msg = "🍊 花蓮【瑞穗鄉】詳細預報\n-------------------"
        umbrella_flag = False
        periods = ["今日白天", "今晚明晨", "明日白天"]

        for i in range(3):
            desc = wx[i]['elementValue'][0]['value']
            pop = pop_list[i]['elementValue'][0]['value']
            temp = t_list[i]['elementValue'][0]['value']
            msg += f"\n【{periods[i]}】\n🌡️ 溫度：{temp}°C\n☁️ 狀況：{desc}\n☔ 降雨：{pop}%"
            if int(pop) >= 30: umbrella_flag = True
            msg += "\n"

        msg += "-------------------"
        msg += "\n⚠️ 提醒：有雨請帶傘！" if umbrella_flag else "\n☀️ 天氣晴朗愉快！"

        # 換回最穩定的 push 模式
        line_url = 'https://api.line.me/v2/bot/message/push'
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {line_key}'}
        
        # 發送對象清單
        payload = {
            "to": target_id,
            "messages": [{"type": "text", "text": msg}]
        }
        
        r = requests.post(line_url, headers=headers, json=payload)
        print(f"發送結果: {r.status_code}, {r.text}")

    except Exception as e:
        print(f"錯誤: {e}")

if __name__ == "__main__":
    get_weather()
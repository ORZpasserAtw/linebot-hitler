import os

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, StickerSendMessage, TemplateSendMessage, FlexSendMessage, URIAction, MessageAction, PostbackAction, MessageTemplateAction, PostbackEvent,
    RichMenu, RichMenuSize, RichMenuArea, RichMenuBounds, CarouselTemplate, CarouselColumn, CarouselContainer, ConfirmTemplate, BubbleContainer, CarouselContainer, BoxComponent, TextComponent, ButtonComponent, ImageComponent
)
import random
from pyowm import OWM
import requests
import ssl
import pandas as pd
import datetime
import pytz

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi(
    "tWtoT0Ov770ISQVJqvjfvB3sElVfLVc+QkFvJ4Ug41CfzhQefISru3q1BAIgN67kO+hfd1kEkYFFVfZiXAekEvSOdgtcGbYOWKIQ5lST9x1QYZYmBPr4JDwUkUXQmydnviHU1FthYD7mcKv1JMzMJwdB04t89/1O/w1cDnyilFU=")
# User id
to = "U6284cec02b95ace9fbdca6547bafadcb"
# Channel Secret
handler = WebhookHandler('747d5974fd7bbae6b9534cffc56e088d')

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

locations = [
    ["威克島", "馬紹爾群島中的小島、北太平洋上的環礁", "晴朗", 99.9,
        "https://upload.wikimedia.org/wikipedia/commons/e/e6/Wake_Island_air.JPG"],
    ["硫磺島", "西太平洋小笠原群島的火山島", "晴朗", 99.9,
        "https://upload.wikimedia.org/wikipedia/commons/4/44/Iwo_Jima_Suribachi_DN-SD-03-11845.JPEG"],
]
owm = OWM('dfbfc697f6af05f728f664111bc07551', version='2.5')
def status2ct(status):
    if (status == "Thunderstorm"):
        return("雷雨")
    elif (status == "Drizzle"):
        return("細雨")
    elif (status == "Rain"):
        return("下雨")
    elif (status == "Snow"):
        return("下雪")
    elif (status == "Mist"):
        return("薄霧")
    elif (status == "Smoke"):
        return("煙霧")
    elif (status == "Haze"):
        return("霧霾")
    elif (status == "Dust"):
        return("灰塵")
    elif (status == "Fog"):
        return("霧氣")
    elif (status == "Sand"):
        return("沙塵")
    elif (status == "Ash"):
        return("灰燼")
    elif (status == "Squall"):
        return("颮")
    elif (status == "Tornado"):
        return("龍捲風")
    elif (status == "Clear"):
        return("晴朗")
    elif (status == "Clouds"):
        return("多雲")

def aqi2rate(aqi):
    if (int(aqi) <= 50):
        return("良好")
    if (int(aqi) <= 100):
        return("普通")
    if (int(aqi) <= 150):
        return("對敏感族群不健康")
    if (int(aqi) <= 200):
        return("對所有族群不健康")
    if (int(aqi) <= 300):
        return("非常不健康")
    if (int(aqi) > 300):
        return("危害")

def uvi2rate(uvi):
    if (round(float(uvi)) <= 2):
        return("低量級")
    if (round(float(uvi)) <= 5):
        return("中量級")
    if (round(float(uvi)) <= 7):
        return("高量級")
    if (round(float(uvi)) <= 10):
        return("過量級")
    if (round(float(uvi)) > 10):
        return("危險級")

def FlexWeatherTemplate(city,url,w,aqiindex,uvi):
    return(
        FlexSendMessage(
        alt_text=city+"-天氣及空氣品質 Flex",
        contents=BubbleContainer(body=BoxComponent(layout="vertical", padding_all="0px",contents=[
                ImageComponent(
                    url=url, 
                    gravity="center",
                    margin="none",
                    size="full",
                    aspectRatio="1:1",
                    aspectMode="cover"
                ),
                BoxComponent(layout="vertical", padding_all="20px", position="absolute", contents=[
                    TextComponent(text=city,size="xl"),
                    TextComponent(text=str(datetime.datetime.now(pytz.timezone('Asia/Taipei')).strftime("%Y/%m/%d %H:%M")),size="xs"),
                    ImageComponent(url="https"+w.get_weather_icon_url()[4:],size="xxs",align="start"),
                    TextComponent(text=status2ct(w.get_status()), size="xxl", weight="bold"),
                    TextComponent(text=w.get_detailed_status(), size="xs"),
                    TextComponent(text="溫度: "+str(round(w.get_temperature(unit='celsius')['temp'],1))+"°C"+"　濕度: "+str(w.get_humidity())+"%", size="xl"),
                    TextComponent(text="空氣品質: "+requests.get('https://data.epa.gov.tw/api/v1/aqx_p_432?api_key=9be7b239-557b-4c10-9775-78cadfc555e9&format=json&limit=1000').json()['records'][aqiindex]['AQI']+"("+aqi2rate(requests.get('https://data.epa.gov.tw/api/v1/aqx_p_432?api_key=9be7b239-557b-4c10-9775-78cadfc555e9&format=json&limit=100').json()['records'][aqiindex]['AQI'])+")"),
                    TextComponent(text="紫外線: "+str(round(float(uvi.json()['records'][0]['UVI'])))+"("+uvi2rate(uvi.json()['records'][0]['UVI'])+")"),
                    TextComponent(text="風速: "+str(round(w.get_wind()['speed']*18/5,1))+"km/h")
                ])
            ])
        )
    )
)

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text == "呼叫助理":
        flex_message = FlexSendMessage(
            alt_text="呼叫助理 Flex",
            contents=BubbleContainer(
                body=BoxComponent(layout="vertical", contents=[
                    TextComponent(text="排程", align="center", weight="bold", size="xl"),
                    BoxComponent(layout="baseline", contents=[
                        TextComponent(text="沒事幹"),
                        TextComponent(text="20/04/31 00:00", align="end")
                        ])
                    ]),
                footer=BoxComponent(layout="horizontal", spacing="md", contents=[
                    ButtonComponent(action=URIAction(
                        label="我要排程", 
                        uri="https://liff.line.me/1654548127-50gGKZyE/Manager"), 
                        style="primary"),
                    ButtonComponent(action=URIAction(
                        label="修改行程", 
                        uri="https://liff.line.me/1654548127-50gGKZyE/Manager"), 
                        style="primary")
                    ])
            )
        )
        line_bot_api.reply_message(event.reply_token, flex_message)
    elif event.message.text == "推薦行程":
        carousel_template = TemplateSendMessage(
            alt_text="Carousel Template 推薦行程",
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnail_image_url=locations[0][4], title=locations[0][0], text="天氣：" +
                        locations[0][2]+"　溫度：" +
                        str(locations[0][3])+"°C"+"\n"+locations[0][1],
                        actions=[
                            MessageTemplateAction(label="開始導航", text="開始導航"+locations[0][0]), 
                            MessageTemplateAction(label="這個我不喜歡", text="不喜歡"+locations[0][0])]
                    ),
                    CarouselColumn(
                        thumbnail_image_url=locations[1][4], title=locations[1][0], text="天氣：" +
                        locations[1][2]+"　溫度：" +
                        str(locations[1][3])+"°C"+"\n"+locations[1][1],
                        actions=[
                            MessageTemplateAction(label="開始導航", text="開始導航"+locations[1][0]), 
                            MessageTemplateAction(label="這個我不喜歡", text="不喜歡"+locations[1][0])]
                    )
                ]
            )
        )
        line_bot_api.reply_message(
            event.reply_token, carousel_template)
    elif "開始導航" in event.message.text:
        if locations[0][0] in event.message.text:
            flex_message = FlexSendMessage(
                alt_text="導航 Flex",
                contents=BubbleContainer(
                    body=BoxComponent(layout="vertical", contents=[
                        TextComponent(text=locations[0][0]+"導航")
                        ]),
                    footer=BoxComponent(layout="horizontal", contents=[
                        ButtonComponent(action=URIAction(
                            label="開啟 Google 地圖", 
                            uri=("https://www.google.com/maps/search/?api=1&query="+locations[0][0])))
                        ])
                )
            )
        elif locations[1][0] in event.message.text:
            flex_message = FlexSendMessage(
                alt_text="導航 Flex",
                contents=BubbleContainer(
                    body=BoxComponent(layout="vertical", contents=[
                        TextComponent(text=locations[1][0]+"導航")
                        ]),
                    footer=BoxComponent(layout="horizontal", contents=[
                        ButtonComponent(action=URIAction(
                            label="開啟 Google 地圖", 
                            uri=("https://www.google.com/maps/search/?api=1&query="+locations[1][0])))
                        ])
                )
            )
        line_bot_api.reply_message(event.reply_token, flex_message)
    elif event.message.text == "記帳小本本":

        money = 69
        budget = 420

        flex_message = FlexSendMessage(
            alt_text="記帳小本本 Flex",
            contents=BubbleContainer(
                body=BoxComponent(layout="vertical", contents=[
                    TextComponent(text="記帳小本本", align="center", weight="bold", size="xl"),
                    BoxComponent(layout="horizontal", contents=[
                        TextComponent(text="當前餘額"),
                        TextComponent(text=str(money) + " 元", align="end")
                        ]),
                    BoxComponent(layout="horizontal", contents=[
                        TextComponent(text="每日可用餘額"),
                        TextComponent(text=str(budget) + " 元", align="end")
                        ])
                    ]
                ),
                footer=BoxComponent(layout="horizontal", spacing="md", contents=[
                    ButtonComponent(action=URIAction(
                        label="開始記帳", 
                        uri="https://liff.line.me/1654548127-50gGKZyE/Account"), 
                        style="primary"),
                    ButtonComponent(action=URIAction(
                        label="餘額設定", 
                        uri="https://liff.line.me/1654548127-50gGKZyE/Account"), 
                        style="primary")
                    ]
                )
            )
        )
        line_bot_api.reply_message(event.reply_token, flex_message)
    elif event.message.text == "天氣及空氣品質":
        flex_message = FlexSendMessage(
            alt_text="天氣及空氣品質 Flex",
            contents=CarouselContainer(contents=[
                    BubbleContainer(size="kilo",body=BoxComponent(layout="vertical", spacing="sm",contents=[
                        BoxComponent(layout="horizontal", spacing="sm", contents=[
                            ButtonComponent(action=PostbackAction(label="臺北", data="臺北-天氣及空氣品質"),style="secondary", color="#94d3e2"),
                            ButtonComponent(action=PostbackAction(label="新北", data="新北-天氣及空氣品質"),style="secondary", color="#94d3e2"),
                            ButtonComponent(action=PostbackAction(label="基隆", data="基隆-天氣及空氣品質"),style="secondary", color="#94d3e2")
                        ]),
                        BoxComponent(layout="horizontal", spacing="sm", contents=[
                            ButtonComponent(action=PostbackAction(label="桃園", data="桃園-天氣及空氣品質"),style="secondary", color="#94d3e2"),
                            ButtonComponent(action=PostbackAction(label="新竹", data="新竹-天氣及空氣品質"),style="secondary", color="#94d3e2"),
                            ButtonComponent(action=PostbackAction(label="苗栗", data="苗栗-天氣及空氣品質"),style="secondary", color="#94d3e2")
                        ]),
                        BoxComponent(layout="horizontal", spacing="sm", contents=[
                            ButtonComponent(action=PostbackAction(label="臺中", data="臺中-天氣及空氣品質"),style="secondary", color="#94d3e2"),
                            ButtonComponent(action=PostbackAction(label="彰化", data="彰化-天氣及空氣品質"),style="secondary", color="#94d3e2"),
                            ButtonComponent(action=PostbackAction(label="南投", data="南投-天氣及空氣品質"),style="secondary", color="#94d3e2")
                        ]),
                    ])),
                    BubbleContainer(size="kilo",body=BoxComponent(layout="vertical", spacing="sm",contents=[
                        BoxComponent(layout="horizontal", spacing="sm", contents=[
                            ButtonComponent(action=PostbackAction(label="雲林", data="雲林-天氣及空氣品質"),style="secondary", color="#94d3e2"),
                            ButtonComponent(action=PostbackAction(label="嘉義", data="嘉義-天氣及空氣品質"),style="secondary", color="#94d3e2"),
                            ButtonComponent(action=PostbackAction(label="臺南", data="臺南-天氣及空氣品質"),style="secondary", color="#94d3e2")
                        ]),
                        BoxComponent(layout="horizontal", spacing="sm", contents=[
                            ButtonComponent(action=PostbackAction(label="高雄", data="高雄-天氣及空氣品質"),style="secondary", color="#94d3e2"),
                            ButtonComponent(action=PostbackAction(label="屏東", data="屏東-天氣及空氣品質"),style="secondary", color="#94d3e2"),
                            ButtonComponent(action=PostbackAction(label="宜蘭", data="宜蘭-天氣及空氣品質"),style="secondary", color="#94d3e2"),
                        ]),
                        BoxComponent(layout="horizontal", spacing="sm", contents=[
                            ButtonComponent(action=PostbackAction(label="花蓮", data="花蓮-天氣及空氣品質"),style="secondary", color="#94d3e2"),
                            ButtonComponent(action=PostbackAction(label="臺東", data="臺東-天氣及空氣品質"),style="secondary", color="#94d3e2"),
                            TextComponent(text="　")
                        ]),
                    ]))
                ])
            )
        line_bot_api.reply_message(event.reply_token, flex_message)
        
    elif event.message.text == "油價":
        try:
            ssl._create_default_https_context = ssl._create_unverified_context
            data = pd.read_html('https://www2.moeaboe.gov.tw/oil102/oil2017/A01/A0108/tablesprices.asp',header=0)[0]  # 取得網頁上的表格資訊
        except:
            ssl._create_default_https_context = ssl._create_unverified_context
            data = pd.read_html('https://www2.moeaboe.gov.tw/oil102/oil2017/A01/A0108/tablesprices.asp',header=0)[0]
            print("Second Try")
        flex_message = FlexSendMessage(
            alt_text="油價 Flex",
            contents=BubbleContainer(size="giga",body=BoxComponent(layout="vertical",contents=[
                    TextComponent(text="今日油價",size="lg",align="center"),
                    TextComponent(text=str(datetime.datetime.now(pytz.timezone('Asia/Taipei')).strftime("%Y/%m/%d %H:%M")),size="xs",align="center"),
                    TextComponent(text="　",size="xxs"),
                    BoxComponent(layout="horizontal", contents=[
                        TextComponent(text="供應商",size="xs"),
                        TextComponent(text="98無鉛",size="xs"),
                        TextComponent(text="95無鉛",size="xs"),
                        TextComponent(text="92無鉛",size="xs"),
                        TextComponent(text="柴油",size="xs"),
                        TextComponent(text="　",size="xs")
                    ]),
                    BoxComponent(layout="horizontal", contents=[
                        TextComponent(text="中油"),
                        TextComponent(text=str(data.iloc[1, 1]), weight="bold"),
                        TextComponent(text=str(data.iloc[1, 2]), weight="bold"),
                        TextComponent(text=str(data.iloc[1, 3]), weight="bold"),
                        TextComponent(text=str(data.iloc[1, 4]), weight="bold"),
                        TextComponent(text="元/公升",size="xs",gravity="bottom")
                    ]),
                    BoxComponent(layout="horizontal", contents=[
                        TextComponent(text="台塑"),
                        TextComponent(text=str(data.iloc[0, 1]), weight="bold"),
                        TextComponent(text=str(data.iloc[0, 2]), weight="bold"),
                        TextComponent(text=str(data.iloc[0, 3]), weight="bold"),
                        TextComponent(text=str(data.iloc[0, 4]), weight="bold"),
                        TextComponent(text="元/公升",size="xs",gravity="bottom")
                    ])
                ])
            )
        )
        line_bot_api.reply_message(event.reply_token, flex_message)
    elif event.message.text == "幫助":
        flex_message = FlexSendMessage(
            alt_text="幫助 Flex",
            contents=CarouselContainer(contents=[
                    BubbleContainer(size="kilo",body=BoxComponent(layout="vertical",spacing="sm",contents=[
                        ButtonComponent(action=PostbackAction(label="呼叫助理", data="呼叫助理-幫助"),style="secondary"),
                        ButtonComponent(action=PostbackAction(label="推薦行程", data="推薦行程-幫助"),style="secondary"),
                        ButtonComponent(action=PostbackAction(label="記帳小本本", data="記帳小本本-幫助"),style="secondary")
                    ])),
                    BubbleContainer(size="kilo",body=BoxComponent(layout="vertical",spacing="sm",contents=[
                        ButtonComponent(action=PostbackAction(label="天氣及空氣品質", data="天氣及空氣品質-幫助"),style="secondary"),
                        ButtonComponent(action=PostbackAction(label="油價", data="油價-幫助"),style="secondary"),
                        TextComponent(text="　")
                    ])),
                ])
            )
        line_bot_api.reply_message(event.reply_token, [
                TextSendMessage(text="歡迎加入Linebot\n讓你輕鬆管理生活大小事\n以下是此行動助理的功能說明"),
                flex_message
                ])

    elif event.message.text == "RNG":
        RNGmsg = ""
        ran = random.randrange(3)
        if ran == 0:
            RNGmsg = "https://youtu.be/keXfiffBzFw"
        elif ran == 1:
            RNGmsg = "https://youtu.be/EWKX3wass9s"
        elif ran == 2:
            RNGmsg = "https://youtu.be/1snEYPg8TXs"
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=RNGmsg))
    elif "=" in event.message.text:
        x = event.message.text.split("=", 1)
        try:
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text=eval(x[0], {"__builtins__": None}, {})))
        except:
            line_bot_api.reply_message(event.reply_token, "計算有誤")
    elif event.message.text == "send nudes":
        message = ImageSendMessage(original_content_url="https://danbooru.donmai.us/data/__atlanta_kantai_collection_drawn_by_rui_shi_rayze_ray__c62475e083da5351641192f3569a3412.jpg",
                                   preview_image_url="https://pbs.twimg.com/media/EdNl79IUYAAh_68?format=jpg&name=small")
        line_bot_api.reply_message(event.reply_token, message)
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="未知Message：\n" + event.message.text))

@handler.add(PostbackEvent)
def handle_postback(event):
    if event.postback.data == "臺北-天氣及空氣品質":
        w = owm.weather_at_place('Taipei,TW').get_weather()
        uvi = requests.get('https://data.epa.gov.tw/api/v1/uv_s_01?format=json&limit=1&api_key=9be7b239-557b-4c10-9775-78cadfc555e9&filters=SiteName,EQ,臺北')
        line_bot_api.reply_message(event.reply_token, FlexWeatherTemplate("臺北市","https://www.tilingtextures.com/wp-content/uploads/2017/03/0504.jpg",w,11,uvi))
    elif event.postback.data == "新北-天氣及空氣品質":
        w = owm.weather_at_place('New Taipei, TW').get_weather()
        uvi = requests.get('https://data.epa.gov.tw/api/v1/uv_s_01?format=json&limit=1&api_key=9be7b239-557b-4c10-9775-78cadfc555e9&filters=SiteName,EQ,板橋')
        line_bot_api.reply_message(event.reply_token, FlexWeatherTemplate("新北市","https://www.tilingtextures.com/wp-content/uploads/2017/03/0504.jpg",w,5,uvi))
    elif event.postback.data == "基隆-天氣及空氣品質":
        w = owm.weather_at_place('Keelung, TW').get_weather()
        uvi = requests.get('https://data.epa.gov.tw/api/v1/uv_s_01?format=json&limit=1&api_key=9be7b239-557b-4c10-9775-78cadfc555e9&filters=SiteName,EQ,基隆')
        line_bot_api.reply_message(event.reply_token, FlexWeatherTemplate("基隆市","https://www.tilingtextures.com/wp-content/uploads/2017/03/0504.jpg",w,0,uvi))
    elif event.postback.data == "桃園-天氣及空氣品質":
        w = owm.weather_at_place('Taoyuan, TW').get_weather()
        uvi = requests.get('https://data.epa.gov.tw/api/v1/uv_s_01?format=json&limit=1&api_key=9be7b239-557b-4c10-9775-78cadfc555e9&filters=SiteName,EQ,桃園')
        line_bot_api.reply_message(event.reply_token, FlexWeatherTemplate("桃園市","https://www.tilingtextures.com/wp-content/uploads/2017/03/0504.jpg",w,16,uvi))
    elif event.postback.data == "新竹-天氣及空氣品質":
        w = owm.weather_at_place('Hsinchu, TW').get_weather()
        uvi = requests.get('https://data.epa.gov.tw/api/v1/uv_s_01?format=json&limit=1&api_key=9be7b239-557b-4c10-9775-78cadfc555e9&filters=SiteName,EQ,新竹')
        line_bot_api.reply_message(event.reply_token, FlexWeatherTemplate("新竹市","https://www.tilingtextures.com/wp-content/uploads/2017/03/0504.jpg",w,23,uvi))
    elif event.postback.data == "苗栗-天氣及空氣品質":
        w = owm.weather_at_place('Miaoli, TW').get_weather()
        uvi = requests.get('https://data.epa.gov.tw/api/v1/uv_s_01?format=json&limit=1&api_key=9be7b239-557b-4c10-9775-78cadfc555e9&filters=SiteName,EQ,苗栗')
        line_bot_api.reply_message(event.reply_token, FlexWeatherTemplate("苗栗市","https://www.tilingtextures.com/wp-content/uploads/2017/03/0504.jpg",w,25,uvi))
    elif event.postback.data == "臺中-天氣及空氣品質":
        w = owm.weather_at_place('Taichung, TW').get_weather()
        uvi = requests.get('https://data.epa.gov.tw/api/v1/uv_s_01?format=json&limit=1&api_key=9be7b239-557b-4c10-9775-78cadfc555e9&filters=SiteName,EQ,臺中')
        line_bot_api.reply_message(event.reply_token, FlexWeatherTemplate("臺中市","https://www.tilingtextures.com/wp-content/uploads/2017/03/0504.jpg",w,31,uvi))
    elif event.postback.data == "彰化-天氣及空氣品質":
        w = owm.weather_at_place('Chang-hua, TW').get_weather()
        uvi = requests.get('https://data.epa.gov.tw/api/v1/uv_s_01?format=json&limit=1&api_key=9be7b239-557b-4c10-9775-78cadfc555e9&filters=SiteName,EQ,彰化')
        line_bot_api.reply_message(event.reply_token, FlexWeatherTemplate("彰化市","https://www.tilingtextures.com/wp-content/uploads/2017/03/0504.jpg",w,32,uvi))
    elif event.postback.data == "南投-天氣及空氣品質":
        w = owm.weather_at_place('Nantou, TW').get_weather()
        uvi = requests.get('https://data.epa.gov.tw/api/v1/uv_s_01?format=json&limit=1&api_key=9be7b239-557b-4c10-9775-78cadfc555e9&filters=SiteName,EQ,南投')
        line_bot_api.reply_message(event.reply_token, FlexWeatherTemplate("南投市","https://www.tilingtextures.com/wp-content/uploads/2017/03/0504.jpg",w,35,uvi))
    elif event.postback.data == "雲林-天氣及空氣品質":
        w = owm.weather_at_place('Douliu, TW').get_weather()
        uvi = requests.get('https://data.epa.gov.tw/api/v1/uv_s_01?format=json&limit=1&api_key=9be7b239-557b-4c10-9775-78cadfc555e9&filters=SiteName,EQ,斗六')
        line_bot_api.reply_message(event.reply_token, FlexWeatherTemplate("雲林縣","https://www.tilingtextures.com/wp-content/uploads/2017/03/0504.jpg",w,36,uvi))
    elif event.postback.data == "嘉義-天氣及空氣品質":
        w = owm.weather_at_place('Chiayi, TW').get_weather()
        uvi = requests.get('https://data.epa.gov.tw/api/v1/uv_s_01?format=json&limit=1&api_key=9be7b239-557b-4c10-9775-78cadfc555e9&filters=SiteName,EQ,嘉義')
        line_bot_api.reply_message(event.reply_token, FlexWeatherTemplate("嘉義市","https://www.tilingtextures.com/wp-content/uploads/2017/03/0504.jpg",w,41,uvi))
    elif event.postback.data == "臺南-天氣及空氣品質":
        w = owm.weather_at_place('Tainan, TW').get_weather()
        uvi = requests.get('https://data.epa.gov.tw/api/v1/uv_s_01?format=json&limit=1&api_key=9be7b239-557b-4c10-9775-78cadfc555e9&filters=SiteName,EQ,臺南')
        line_bot_api.reply_message(event.reply_token, FlexWeatherTemplate("臺南市","https://www.tilingtextures.com/wp-content/uploads/2017/03/0504.jpg",w,45,uvi))
    elif event.postback.data == "高雄-天氣及空氣品質":
        w = owm.weather_at_place('Kaohsiung, TW').get_weather()
        uvi = requests.get('https://data.epa.gov.tw/api/v1/uv_s_01?format=json&limit=1&api_key=9be7b239-557b-4c10-9775-78cadfc555e9&filters=SiteName,EQ,高雄')
        line_bot_api.reply_message(event.reply_token, FlexWeatherTemplate("高雄市","https://www.tilingtextures.com/wp-content/uploads/2017/03/0504.jpg",w,55,uvi))
    elif event.postback.data == "屏東-天氣及空氣品質":
        w = owm.weather_at_place('Hengchun, TW').get_weather()
        uvi = requests.get('https://data.epa.gov.tw/api/v1/uv_s_01?format=json&limit=1&api_key=9be7b239-557b-4c10-9775-78cadfc555e9&filters=SiteName,EQ,屏東')
        line_bot_api.reply_message(event.reply_token, FlexWeatherTemplate("屏東市","https://www.tilingtextures.com/wp-content/uploads/2017/03/0504.jpg",w,57,uvi))
    elif event.postback.data == "宜蘭-天氣及空氣品質":
        w = owm.weather_at_place('Yilan, TW').get_weather()
        uvi = requests.get('https://data.epa.gov.tw/api/v1/uv_s_01?format=json&limit=1&api_key=9be7b239-557b-4c10-9775-78cadfc555e9&filters=SiteName,EQ,宜蘭')
        line_bot_api.reply_message(event.reply_token, FlexWeatherTemplate("宜蘭市","https://www.tilingtextures.com/wp-content/uploads/2017/03/0504.jpg",w,63,uvi))
    elif event.postback.data == "花蓮-天氣及空氣品質":
        w = owm.weather_at_place('Hualien, TW').get_weather()
        uvi = requests.get('https://data.epa.gov.tw/api/v1/uv_s_01?format=json&limit=1&api_key=9be7b239-557b-4c10-9775-78cadfc555e9&filters=SiteName,EQ,花蓮')
        line_bot_api.reply_message(event.reply_token, FlexWeatherTemplate("花蓮市","https://www.tilingtextures.com/wp-content/uploads/2017/03/0504.jpg",w,61,uvi))
    elif event.postback.data == "臺東-天氣及空氣品質":
        w = owm.weather_at_place('Taitung, TW').get_weather()
        uvi = requests.get('https://data.epa.gov.tw/api/v1/uv_s_01?format=json&limit=1&api_key=9be7b239-557b-4c10-9775-78cadfc555e9&filters=SiteName,EQ,臺東')
        line_bot_api.reply_message(event.reply_token, FlexWeatherTemplate("臺東市","https://www.tilingtextures.com/wp-content/uploads/2017/03/0504.jpg",w,60,uvi))
    elif event.postback.data == "呼叫助理-幫助":
         line_bot_api.reply_message(event.reply_token, TextSendMessage(text=
        "【呼叫助理】\n現代人生活忙碌，有時會忘記重要的約會，利用「我要排程」把重要的行程紀錄起來，使生活變得井然有序，檢視「查詢行程」可知今天、本週、本月的所有行程，讓行程不遺漏，行程有變動時，點擊「修改」就可變更和刪除。"))
    elif event.postback.data == "推薦行程-幫助":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=
        "【推薦行程】\n台灣好玩的地方真的很多，這裡推薦北、中、南適合親子同遊的景點，點擊「了解更多」可以知道更多的景點資訊，點擊「我不喜歡」會有多個景點讓你選擇！"))
    elif event.postback.data == "記帳小本本-幫助":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=
        "【記帳小本本】\n點擊「開始記帳」把收支的資訊記錄下來，透過「日期」的查詢，可知當日、本週、本月的結餘和收支的金額。點擊「明細」可知每筆金錢的流向，也可做每筆帳的修改與刪除。\n養成記帳的好習慣，了解自身錢財的流動和消費習慣，進而做好財務的管理。"))
    elif event.postback.data == "天氣及空氣品質-幫助":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=
        "【天氣及空氣品質】\n提供台灣主要城市，每日的天氣概況、空氣品質、紫外線。"))
    elif event.postback.data == "油價-幫助":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=
        "【油價】\n提供當日中油、台塑主要油價。"))
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage("未知Postback：\n" + event.postback.data))  

rich_menu_to_create = RichMenu(
    size=RichMenuSize(width=2500, height=1686),
    selected=True,
    name="圖文選單 1",
    chat_bar_text="查看快捷鍵",
    areas=[RichMenuArea(
        bounds=RichMenuBounds(x=0, y=0, width=854, height=843),
        action=URIAction(label="呼叫助理", uri="https://liff.line.me/1654548127-50gGKZyE/Manager")
        ),
        RichMenuArea(
        bounds=RichMenuBounds(x=854, y=0, width=854, height=843),
        action=URIAction(label="推薦行程", uri="https://liff.line.me/1654548127-50gGKZyE/Travel")
        ),
        RichMenuArea(
        bounds=RichMenuBounds(x=1707, y=0, width=854, height=843),
        action=URIAction(label="記帳小本本", uri="https://liff.line.me/1654548127-50gGKZyE/Account")
        ),
        RichMenuArea(
        bounds=RichMenuBounds(x=0, y=843, width=854, height=843),
        action=MessageAction(label="天氣及空氣品質", text="天氣及空氣品質")
        ),
        RichMenuArea(
        bounds=RichMenuBounds(x=854, y=843, width=854, height=843),
        action=MessageAction(label="油價", text="油價")
        ),
        RichMenuArea(
        bounds=RichMenuBounds(x=1707, y=843, width=854, height=843),
        action=MessageAction(label="message", text="幫助")
        )
    ]
)
rich_menu_id = line_bot_api.create_rich_menu(rich_menu=rich_menu_to_create)
with open("BG.jpg", 'rb') as f:
    line_bot_api.set_rich_menu_image(rich_menu_id, "image/jpeg", f)

rich_menu = line_bot_api.get_rich_menu(rich_menu_id)
print(rich_menu_id)

line_bot_api.set_default_rich_menu(rich_menu_id)

"""message = StickerSendMessage(package_id="11538", sticker_id="51626518")
line_bot_api.push_message(to, message)"""

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

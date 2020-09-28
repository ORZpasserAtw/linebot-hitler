import os
import random

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, StickerSendMessage, TemplateSendMessage, FlexSendMessage, URIAction, MessageAction, MessageTemplateAction, RichMenu, RichMenuSize, RichMenuArea, RichMenuBounds, CarouselTemplate, CarouselColumn, ConfirmTemplate, BubbleContainer, BoxComponent, TextComponent, ButtonComponent, ImageComponent
)

from yahoo_weather.weather import YahooWeather
from yahoo_weather.config.units import Unit
import pandas as pd

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

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text == "呼叫助理":
        flex_message = FlexSendMessage(
            alt_text="Flex Message 呼叫助理",
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
                alt_text="Flex Message 導航",
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
                alt_text="Flex Message 導航",
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
            alt_text="Flex Message 記帳小本本",
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
        data = YahooWeather(
                            APP_ID='h0Hx273a',
                            api_key='dj0yJmk9RlpXbkp0RnJKYWhmJmQ9WVdrOWFEQkllREkzTTJFbWNHbzlNQT09JnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PTgy',
                            api_secret='a73e2929c4728b17e2527438a49740184cdc5665'
                            )
        data.get_yahoo_weather_by_city("台北市", Unit.celsius)

        weatherdice = random.randrange(5)
        wlocation = ["台北市"]
        weather = ["晴朗","多雲","陰天","小雨","大雨"]
        temperature = random.randrange(-50,50)
        rain = random.randrange(100)
        air = random.randrange(500)
        airrate = "錯誤"
        if air <= 50:
            airrate = "良好"
        elif air >= 51 and air <= 100:
            airrate = "普通"
        elif air >= 101 and air <= 150:
            airrate = "敏感不健康"
        elif air >= 151 and air <= 200:
            airrate = "所有不健康"
        elif air >= 201 and air <= 300:
            airrate = "非常不健康"
        elif air >= 301:
            airrate = "危害"
        flex_message = FlexSendMessage(
            alt_text="Flex Message 天氣及空氣品質",
            contents=BubbleContainer(
                body=BoxComponent(layout="vertical", padding_all="0px",contents=[
                    ImageComponent(
                        url="https://w.wallhaven.cc/full/47/wallhaven-477mv3.jpg", 
                        gravity="center",
                        margin="none",
                        size="full",
                        aspectRatio="1:1",
                        aspectMode="cover"
                    ),
                    BoxComponent(layout="vertical", padding_all="20px", position="absolute", contents=[
                        TextComponent(text=wlocation[0], size="sm"),
                        TextComponent(text=data.condition.text, size="xxl"),
                        TextComponent(text="溫度 " + str(data.condition.temperature) + "°C", size="xl"),
                        TextComponent(text="降雨機率 " + str(rain) + "%"),
                        TextComponent(text="空氣品質 " + airrate + " " + str(air))
                    ])
                ])
            )
        )
        line_bot_api.reply_message(event.reply_token, flex_message)
    elif event.message.text == "油價":
        try:
            readData = pd.read_html('https://www2.moeaboe.gov.tw/oil102/oil2017/A01/A0108/tablesprices.asp',header=0)[0]  # 取得網頁上的表格資訊
        except:
            print("ERROR")
        flex_message = FlexSendMessage(
            alt_text="Flex Message 油價",
            contents=BubbleContainer(
                size="giga",body=BoxComponent(layout="vertical",contents=[
                    BoxComponent(layout="horizontal", contents=[
                        TextComponent(text="元/公升"),
                        TextComponent(text="油品供應商"),
                        TextComponent(text=readData.columns.values[0]),
                        TextComponent(text=readData.columns.values[1]),
                        TextComponent(text=readData.columns.values[2]),
                        TextComponent(text=readData.columns.values[3])
                    ]),
                    BoxComponent(layout="horizontal", contents=[
                        TextComponent(text="G"),
                        TextComponent(text="H"),
                        TextComponent(text="I"),
                        TextComponent(text="J"),
                        TextComponent(text="K"),
                        TextComponent(text="L")
                    ]),
                    BoxComponent(layout="horizontal", contents=[
                        TextComponent(text="M"),
                        TextComponent(text="N"),
                        TextComponent(text="O"),
                        TextComponent(text="P"),
                        TextComponent(text="Q"),
                        TextComponent(text="R")
                    ])
                ])
            )
        )
        line_bot_api.reply_message(event.reply_token, flex_message)
    elif event.message.text == "幫助":
        confirm_template = TemplateSendMessage(
            alt_text="Confirm Template 幫助",
            template=ConfirmTemplate(text="你是智障嗎？", actions=[
                MessageTemplateAction(label="是", text="我是智障"), 
                MessageTemplateAction(label="否", text="我不是智障")
                ])
        )
        line_bot_api.reply_message(event.reply_token, confirm_template)
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
        message = ImageSendMessage(original_content_url="https://cdn.donmai.us/original/cc/24/__bismarck_kantai_collection_drawn_by_kuon_kwonchanji__cc246a8e793daf930446af915c187774.jpg",
                                   preview_image_url="https://cdn.donmai.us/preview/cc/24/cc246a8e793daf930446af915c187774.jpg")
        line_bot_api.reply_message(event.reply_token, message)
    else:
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text="未知指令：\n" + event.message.text))


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
        action=URIAction(label="推薦行程", uri="https://liff.line.me/1654548127-50gGKZyE/Account")
        ),
        RichMenuArea(
        bounds=RichMenuBounds(x=0, y=843, width=854, height=843),
        action=MessageAction(label="message", text="天氣及空氣品質")
        ),
        RichMenuArea(
        bounds=RichMenuBounds(x=854, y=843, width=854, height=843),
        action=MessageAction(label="message", text="油價")
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

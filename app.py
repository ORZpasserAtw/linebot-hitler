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
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, StickerSendMessage, RichMenu, RichMenuSize, RichMenuArea, RichMenuBounds, URIAction, MessageAction, TemplateSendMessage, ImageCarouselTemplate, ImageCarouselColumn, PostbackAction
)

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi(
    'tWtoT0Ov770ISQVJqvjfvB3sElVfLVc+QkFvJ4Ug41CfzhQefISru3q1BAIgN67kO+hfd1kEkYFFVfZiXAekEvSOdgtcGbYOWKIQ5lST9x1QYZYmBPr4JDwUkUXQmydnviHU1FthYD7mcKv1JMzMJwdB04t89/1O/w1cDnyilFU=')
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

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text == "呼叫助理":
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text="你好，有甚麼需要分佈的嗎？"))
    elif event.message.text == "推薦行程":
        image_carousel_template_message = TemplateSendMessage(
            alt_text='ImageCarousel template',
            template=ImageCarouselTemplate(
                columns=[
                    ImageCarouselColumn(
                        image_url='https://upload.wikimedia.org/wikipedia/commons/e/e6/Wake_Island_air.JPG',
                        message='威克島',
                        action=PostbackAction(
                            label='postback1',
                            display_text='開始導航',
                            data='action=buy&itemid=1'
                        )
                    ),
                    ImageCarouselColumn(
                        image_url='https://upload.wikimedia.org/wikipedia/commons/4/44/Iwo_Jima_Suribachi_DN-SD-03-11845.JPEG',
                        message='硫磺島',
                        action=PostbackAction(
                            label='postback2',
                            display_text='開始導航',
                            data='action=buy&itemid=2'
                        )
                    )
                ]
            )
        )
        line_bot_api.reply_message(
            event.reply_token, TemplateSendMessage(alt_text="Temple",template=image_carousel_template_message))
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
        ans = 1+1
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=ans))
    elif event.message.text == "send nudes":
        message = ImageSendMessage(original_content_url='https://cdn.donmai.us/original/cc/24/__bismarck_kantai_collection_drawn_by_kuon_kwonchanji__cc246a8e793daf930446af915c187774.jpg',
                                   preview_image_url='https://cdn.donmai.us/preview/cc/24/cc246a8e793daf930446af915c187774.jpg')
        line_bot_api.reply_message(event.reply_token, message)
    else:
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.message.text))


rich_menu_to_create = RichMenu(
    size=RichMenuSize(width=2500, height=1686),
    selected=True,
    name="圖文選單 1",
    chat_bar_text="查看更多資訊",
    areas=[RichMenuArea(
        bounds=RichMenuBounds(x=0, y=0, width=854, height=843),
        action=MessageAction(label="message", text="呼叫助理")),
        RichMenuArea(
        bounds=RichMenuBounds(x=854, y=0, width=854, height=843),
        action=MessageAction(label="message", text="推薦行程")),
        RichMenuArea(
        bounds=RichMenuBounds(x=1707, y=0, width=854, height=843),
        action=URIAction(label="URI", uri="https://www.desmos.com/scientific")),
        RichMenuArea(
        bounds=RichMenuBounds(x=0, y=843, width=854, height=843),
        action=MessageAction(label="message", text="天氣及空氣品質")),
        RichMenuArea(
        bounds=RichMenuBounds(x=854, y=843, width=854, height=843),
        action=MessageAction(label="message", text="油價")),
        RichMenuArea(
        bounds=RichMenuBounds(x=1707, y=843, width=854, height=843),
        action=MessageAction(label="message", text="幫助"))
    ]
)
rich_menu_id = line_bot_api.create_rich_menu(rich_menu=rich_menu_to_create)
with open("BG.png", 'rb') as f:
    line_bot_api.set_rich_menu_image(rich_menu_id, "image/png", f)

rich_menu = line_bot_api.get_rich_menu(rich_menu_id)
print(rich_menu_id)

line_bot_api.set_default_rich_menu(rich_menu_id)

message = StickerSendMessage(package_id='11538', sticker_id='51626518')
line_bot_api.push_message(to, message)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

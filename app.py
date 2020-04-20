import os,random

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, StickerSendMessage, RichMenu, RichMenuSize, RichMenuArea,RichMenuBounds, URIAction, MessageAction, PostbackAction
)

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('tWtoT0Ov770ISQVJqvjfvB3sElVfLVc+QkFvJ4Ug41CfzhQefISru3q1BAIgN67kO+hfd1kEkYFFVfZiXAekEvSOdgtcGbYOWKIQ5lST9x1QYZYmBPr4JDwUkUXQmydnviHU1FthYD7mcKv1JMzMJwdB04t89/1O/w1cDnyilFU=')
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
    if event.message.text == "RNG" :
        RNGmsg = ""
        ran = random.randrange(3)
        if ran == 0 :
            RNGmsg = "https://youtu.be/keXfiffBzFw"
        elif ran == 1:
            RNGmsg = "https://youtu.be/EWKX3wass9s"
        elif ran == 2:
            RNGmsg = "https://youtu.be/1snEYPg8TXs"
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=RNGmsg))
    elif "=" in event.message.text:
        ans = 1+1
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=ans))
    elif event.message.text == "send nudes" :
        message = ImageSendMessage(original_content_url='https://cdn.donmai.us/original/cc/24/__bismarck_kantai_collection_drawn_by_kuon_kwonchanji__cc246a8e793daf930446af915c187774.jpg',preview_image_url='https://cdn.donmai.us/preview/cc/24/cc246a8e793daf930446af915c187774.jpg')
        line_bot_api.reply_message(event.reply_token, message)
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text))

rich_menu_to_create = RichMenu(
    size=RichMenuSize(width=2500, height=843),
    selected=True,
    name="圖文選單 1",
    chat_bar_text="查看更多資訊",
    areas=[RichMenuArea(
        bounds=RichMenuBounds(x=0, y=0, width=2500, height=281),
        action=MessageAction(label="message", text="Ta 152")),
        RichMenuArea(
        bounds=RichMenuBounds(x=0, y=281, width=2500, height=281),
        action=PostbackAction(label="postback", text="Fw 190",data="???")),
        RichMenuArea(
        bounds=RichMenuBounds(x=0, y=562, width=2500, height=281),
        action=URIAction(label="URI", uri="https://youtu.be/l7JF0k4lNdE"))
        ]
)
rich_menu_id = line_bot_api.create_rich_menu(rich_menu=rich_menu_to_create)
with open("BG.jpg", 'rb') as f:
    line_bot_api.set_rich_menu_image(rich_menu_id,"image/jpeg",f)

rich_menu = line_bot_api.get_rich_menu(rich_menu_id)
print(rich_menu_id)

line_bot_api.set_default_rich_menu(rich_menu_id)



message = StickerSendMessage(package_id='11538',sticker_id='51626518')
line_bot_api.push_message(to, message)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
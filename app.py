from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('tWtoT0Ov770ISQVJqvjfvB3sElVfLVc+QkFvJ4Ug41CfzhQefISru3q1BAIgN67kO+hfd1kEkYFFVfZiXAekEvSOdgtcGbYOWKIQ5lST9x1QYZYmBPr4JDwUkUXQmydnviHU1FthYD7mcKv1JMzMJwdB04t89/1O/w1cDnyilFU=')
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
    if event.message.text == "no" :
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="brrrrr"))
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text))

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
import json
import requests

import telegram
from telegram import KeyboardButton, ReplyKeyboardMarkup

from django.conf import settings
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from .models import Pending, Lower, Upper


class TelegramBotView(View):
    """
    View that receives the webhook every time a user write to the chat and
    gives the appropiate response.
    """

    bot_token = settings.BOT_TOKEN
    bot = telegram.Bot(token=bot_token)
    base_frames_url = settings.FRAMES_BASE_URL
    chat_id = ""

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def restart_chat(self):
        Pending.objects.filter(chat_id=self.chat_id).delete()
        Upper.objects.filter(chat_id=self.chat_id).delete()
        Lower.objects.filter(chat_id=self.chat_id).delete()

    def get_lower_limit(self):
        limit = 0
        if Lower.objects.filter(chat_id=self.chat_id).count() > 0:
            limit = Lower.objects.filter(chat_id=self.chat_id).first().frame

        return limit

    def get_upper_limit(self):
        url = settings.FRAMES_BASE_URL
        res = requests.get(url)
        json_data = json.loads(res.text)
        limit = json_data["frames"]
        if Upper.objects.filter(chat_id=self.chat_id).count() > 0:
            limit = Upper.objects.filter(chat_id=self.chat_id).first().frame

        return limit

    def get_limits(self):
        upper = self.get_upper_limit()
        lower = self.get_lower_limit()

        return upper, lower

    def get_frame(self):
        upper, lower = self.get_limits()
        frame = lower + (upper - lower) // 2

        return frame

    def is_launch_frame(self):
        upper, lower = self.get_limits()

        return upper - lower == 1

    def manage_answer(self, text):
        if text == "/start":
            self.restart_chat()

        if Pending.objects.filter(chat_id=self.chat_id).count() > 0:
            pending = Pending.objects.filter(chat_id=self.chat_id).first()

            if text.lower() == "yes":
                Upper.objects.create(chat_id=self.chat_id, frame=pending.frame)

            elif text.lower() == "no":
                Lower.objects.create(chat_id=self.chat_id, frame=pending.frame)

        frame = self.get_frame()
        Pending.objects.create(chat_id=self.chat_id, frame=frame)

        return frame

    def get_reply_markup(self):
        keyboard = [
            [
                KeyboardButton(text="Yes", callback_data="yes"),
                KeyboardButton(text="No", callback_data="no"),
            ]
        ]

        return ReplyKeyboardMarkup(keyboard)

    def send_response(self, frame, chat_id):
        frame_url = f"{self.base_frames_url}/frame/{frame}/"
        message = f"*{frame}* - Did the rocket launch yet?"

        if self.is_launch_frame():
            upper = self.get_upper_limit()
            message = f"*{upper}* - Congrats! You have found the launch frame!"

        data = {
            "chat_id": chat_id,
            "photo": frame_url,
            "caption": message,
            "parse_mode": "Markdown",
            "reply_markup": self.get_reply_markup(),
        }

        self.bot.send_photo(**data)

    def post(self, request, *args, **kwargs):
        # Receive data from the user
        text = ""
        data = json.loads(request.body)
        message = data["message"]
        chat_id = message["chat"]["id"]
        if message.get("text"):
            text = message["text"]
        self.chat_id = chat_id

        # Manage the received answer and send response with the next frame
        frame = self.manage_answer(text)
        self.send_response(frame, chat_id)

        return JsonResponse({"ok": text, "id": chat_id})

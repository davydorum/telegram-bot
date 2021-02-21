from django.conf import settings
from django.urls import path
from .views import TelegramBotView


urlpatterns = [
    path(f"{settings.BOT_TOKEN}/", TelegramBotView.as_view(), name="respond"),
]

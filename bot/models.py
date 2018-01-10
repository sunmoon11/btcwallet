from django.db import models
from django.utils import timezone
from celery.decorators import task
from datetime import datetime, timedelta
import telebot
import json
import re
import requests
from time import sleep

class BotUser(models.Model):
    chat_id = models.BigIntegerField(null=True, blank=True)
    step = models.CharField(max_length=50, null=True, blank=True)
    username = models.CharField(max_length=120, null=True, blank=True)
    fio = models.CharField(max_length=120, null=True, blank=True)

    btc_balance = models.FloatField(default = 0)

    btc_wallet = models.CharField(max_length=120, null=True, blank=True)

    currency = models.CharField(max_length=120, null=True, blank=True, default = 'USD')
    phone_number = models.CharField(max_length=120, null=True, blank=True)

    wallet_btc_withdraw = models.CharField(max_length=120, null=True, blank=True)
    amount_btc_withdraw = models.FloatField(default = 0, null=True, blank=True)

    lang = models.CharField(max_length=50, null=True, blank=True)
    btc_balance = models.FloatField(default=0, null=True, blank=True)

    def __str__(self):
        return 'user_id = ' + str(self.id) + ' chat_id = ' + str(self.chat_id) + ' ' + self.fio + ' ' + self.username

    class Meta:
        verbose_name = 'Telegram User'
        verbose_name_plural = 'Telegram User'


class Settings(models.Model):

    blockio_api_keys_btc     = models.CharField(max_length=250, null=True, blank = True)
    blockio_api_keys_ltc     = models.CharField(max_length=250, null=True, blank = True)
    blockio_sercret_pin      = models.CharField(max_length=250, null=True, blank = True)

    wallet_for_fee           = models.CharField(max_length=250, null=True, blank = True)
    procent_fee              = models.FloatField(default=0.1, null=True, blank = True)

    def __str__(self):
        return 'Установить настройки'

    class Meta:
        verbose_name        = 'Настройки бота'
        verbose_name_plural = 'Настройки бота'

class Log(models.Model):
    bot_user            = models.ForeignKey(BotUser, null=True, blank = True,  on_delete=models.SET_NULL)
    type_log            = models.CharField(max_length=250, null=True, blank = True)
    text                = models.TextField(null=True, blank = True)
    date_in             = models.DateTimeField(auto_now_add = True, auto_now = False, null=True, blank = True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name_plural = 'Логи'


class Txs(models.Model):
    bot_user        = models.ForeignKey(BotUser, null=True, blank = True,  on_delete=models.SET_NULL)
    trans_id        = models.CharField(max_length=250, null=True, blank = True)
    date_in         = models.DateTimeField(auto_now_add = True, auto_now = False, null=True, blank = True)
    wallet          = models.CharField(max_length=250, null=True, blank = True)
    summa           = models.FloatField(null=True, blank = True)
    status          = models.CharField(max_length=50, null=True, blank = True)

    def __str__(self):
        return self.trans_id

    class Meta:
        verbose_name_plural = 'Транзакции'


#####################################
### Селери таск #####################
#####################################

@task
def send(text, text_eng):

    try:
        bot = telebot.TeleBot('434214801:AAH67lvsi1k3vFnElT8OlCIBhrXpwDMuE5k')

        for user in BotUser.objects.all():
            
            try:
                if user.lang == 'ru':
                    bot.send_message(user.chat_id, text)
                elif user.lang == 'en':
                    bot.send_message(user.chat_id, text_eng)
            except:
                pass

                sleep(0.25)

    except Exception as e:
        print(e)
        bot.send_message(354691583, str(e))

#####################################

class Compaign(models.Model):

    text            = models.TextField(null=True, blank = True)
    text_eng        = models.TextField(null=True, blank = True)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name        = 'Рассылка'
        verbose_name_plural = 'Рассылка'

    def save(self, *args, **kwargs):
        if self.pk is None:
            send.apply_async((self.text,text_eng))
            
        super(Compaign, self).save(*args, **kwargs)

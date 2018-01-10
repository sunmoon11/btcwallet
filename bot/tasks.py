# -*- coding: utf-8 -*-
from celery.decorators import task
import telebot
from celery.task.schedules import crontab
from celery.decorators import periodic_task
import json
import hashlib
import hmac
import requests
from time import sleep
from datetime import datetime, timedelta
from hashlib import sha256
from .models import *
import requests
from django.utils.translation import ugettext as _
from django.utils.translation import activate
import telebot
from block_io import BlockIo


# @periodic_task(run_every=crontab())
@periodic_task(run_every=crontab())
def every_min():
    try:

        token = '434214801:AAH67lvsi1k3vFnElT8OlCIBhrXpwDMuE5k'
        bot = telebot.TeleBot(token)

        settings = Settings.objects.all().first()
        blockio_api_keys_btc = settings.blockio_api_keys_btc
        blockio_sercret_pin = settings.blockio_sercret_pin
        version = 2  # API version

        block_io = BlockIo(blockio_api_keys_btc, blockio_sercret_pin, version)

        last_25_trans = block_io.get_transactions(type='received')

        if last_25_trans["status"] == "success":
            # print(last_25_trans)
            for trans in last_25_trans["data"]["txs"]:

                trans_id = trans["txid"]
                print(trans)

                if not Txs.objects.filter(trans_id=trans_id).exists():
                    recipient = trans["amounts_received"][0]["recipient"]
                    summa = float(trans["amounts_received"][0]["amount"])
                    # time_in = trans["time"]

                    chat_id = int(block_io.get_address_balance(addresses=recipient)['data']['balances'][0]['label'])
                    user = BotUser.objects.get(chat_id=chat_id)

                    activate(user.lang)

                    Txs.objects.create(bot_user=user, trans_id=trans_id, summa=summa, wallet=recipient,
                                       status='created')

                    bot.send_message(354691583, 'На ваш кошелек был создан перевод на сумму %.8f BTC' % summa)
                    bot.send_message(chat_id, _('На ваш кошелек был создан перевод на сумму %.8f BTC') % summa)

    except Exception as e:
        # print(e)
        bot.send_message(354691583, str(e))

    finally:
        quit()

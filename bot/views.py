from django.shortcuts import render
from django.http import HttpResponse
import telebot
from .models import *
from django.views.decorators.csrf import csrf_exempt
import json
import re
from block_io import BlockIo
from datetime import datetime
import requests
from time import sleep

from django.utils.translation import ugettext as _
from django.utils.translation import activate


def is_digit(string):
    if string.isdigit():
        return True
    else:
        try:
            float(string)
            return True
        except ValueError:
            return False


def isint(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


@csrf_exempt
def bot(request):
    token = '434214801:AAH67lvsi1k3vFnElT8OlCIBhrXpwDMuE5k'
    try:
        bot = telebot.TeleBot(token)
        data = json.loads(request.body.decode('utf-8'))

        if 'callback_query' in data.keys():
            chat_id = data['callback_query']['from']['id']
            callback_data = data['callback_query']['data']
            text = ''
            file_id = ''
            phone_number = ''

        elif 'message' in data.keys():

            if 'contact' in data['message'].keys():
                phone_number = data['message']['contact']['phone_number']
                chat_id = data["message"]["chat"]["id"]
                callback_data = ''
                text = ''
                file_id = ""

            if 'text' in data['message'].keys():
                text = data['message']['text']
                chat_id = data['message']['chat']['id']
                callback_data = ''
                file_id = ''
                phone_number = ''

        else:
            mes = 'Error'
            bot.send_message(chat_id, mes)
            return HttpResponse('OK')

        isOld = BotUser.objects.filter(chat_id=chat_id).count()

        settings = Settings.objects.all().first()
        blockio_api_keys_btc = settings.blockio_api_keys_btc
        blockio_sercret_pin = settings.blockio_sercret_pin
        version = 2  # API version
        block_io = BlockIo(blockio_api_keys_btc, blockio_sercret_pin, version)

        if isOld != 0:
            user = BotUser.objects.get(chat_id=chat_id)

        if text == '/start':
            try:
                username = data["message"]["from"]["username"]

            except:
                username = ""

            try:
                fio1 = data["message"]["from"]["first_name"]

            except:
                fio1 = ""

            try:
                fio2 = data["message"]["from"]["last_name"]

            except:
                fio2 = ""

            fio = fio1 + ' ' + fio2

            if isOld == 0:

                try:
                    response = block_io.get_new_address(label=str(chat_id))

                    if response["status"] == "success":
                        btc_wallet = response["data"]["address"]
                    else:
                        btc_wallet = None

                except:  # response["status"] == "fail":

                    try:
                        response2 = block_io.get_address_by(label=str(chat_id))

                        if response2["status"] == "success":
                            btc_wallet = response2["data"]["address"]
                        else:
                            btc_wallet = None
                    except:

                        bot.send_message(354691583, 'Не выдается кошелек BTC для пополнения')
                        btc_wallet = None
                        return HttpResponse('OK')

                user = BotUser.objects.create(chat_id=chat_id, fio=fio, username=username, step="home",
                                              btc_wallet=btc_wallet)

            else:
                BotUser.objects.filter(chat_id=chat_id).update(step="home")

            mes = 'Choose language / Выберите язык'
            button = telebot.types.ReplyKeyboardMarkup(True, False)
            button.row('Русский')
            button.row('English')
            bot.send_message(chat_id, mes, reply_markup=button)

            user.step = 'home'
            user.save()

            return HttpResponse('OK')

        if text == 'Русский' or text == 'English':

            if text == 'Русский':
                user.lang = 'ru'
                user.save()
            elif text == 'English':
                user.lang = 'en'
                user.save()

            activate(user.lang)

            mes = _('BeeWallet является самым защищенным и самым быстрым кошельком. Отправляя средства внутри BeeWallet вы мгновенно получаете доступ к средствам без необходимости дожидаться подтверждения сети. Пригласите своих друзей в BeeWallet и экономьте до 40% на плате за транзакцию.')
            button = telebot.types.ReplyKeyboardMarkup(True, False)
            button.row(_('Баланс'), _('История'))
            button.row(_('Отправить'), _('Получить'))
            button.row(_('Настройки'), _('Поддержка'))
            bot.send_message(chat_id, mes, reply_markup=button)

            user.step = 'menu'
            user.save()
            return HttpResponse('OK')

        ###################
		# Установить язык #
		###################
        activate(user.lang)
        ###################

        if text == _('Главное меню') or callback_data == 'to_home':

            mes = _('BeeWallet является самым защищенным и самым быстрым кошельком. Отправляя средства внутри BeeWallet вы мгновенно получаете доступ к средствам без необходимости дожидаться подтверждения сети. Пригласите своих друзей в BeeWallet и экономьте до 40% на плате за транзакцию.')
            button = telebot.types.ReplyKeyboardMarkup(True, False)
            button.row(_('Баланс'), _('История'))
            button.row(_('Отправить'), _('Получить'))
            button.row(_('Настройки'), _('Поддержка'))
            bot.send_message(chat_id, mes, reply_markup=button)

            user.step = 'menu'
            user.save()
            return HttpResponse('OK')

        if user.btc_wallet is None:

            try:
                response = block_io.get_new_address(label=str(chat_id))

                is_Error = False

                if response["status"] == "success":
                    btc_wallet = response["data"]["address"]
                else:
                    is_Error = True

            except:  # response["status"] == "fail":

                try:
                    response2 = block_io.get_address_by(label=str(chat_id))

                    if response2["status"] == "success":
                        btc_wallet = response2["data"]["address"]
                    else:
                        is_Error = True

                except:

                    bot.send_message(354691583, 'Не выдается кошелек BTC для пополнения')
                    Log.objects.create(bot_user=user, type_log="error_btc", text=str(e))
                    mes = _('Возникла ошибка. Обратитесь в службу поддержки @beeqb')
                    bot.send_message(user.chat_id, mes)
                    return HttpResponse('OK')

            if is_Error:
                bot.send_message(354691583, 'Не выдается кошелек BTC для пополнения')
                Log.objects.create(bot_user=user, type_log="error_btc", text=str(e))
                mes = _('Возникла ошибка. Обратитесь в службу поддержки @beeqb')
                bot.send_message(user.chat_id, mes)
                return HttpResponse('OK')

            user.btc_wallet = btc_wallet
            user.save()

        if phone_number != "":
            mes = _('Теперь вам могут переводить средства внутри BeeWallet, просто указав ваш номер телефона.')

            user.phone_number = phone_number.replace('+', '').replace(')', '').replace('(', '').replace('-',
                                                                                                        '').replace(' ',
                                                                                                                    '')
            user.save()

            bot.send_message(chat_id, mes)

            return HttpResponse('OK')

        if text == _('Баланс'):

            try:
                response = block_io.get_address_balance(labels=str(chat_id))
                print(response)
                if response["status"] == "success":
                    available_balance = float(response["data"]["available_balance"])
                    pending_received_balance = float(response["data"]["pending_received_balance"])
                else:
                    Log.objects.create(bot_user=user, type_log="error_btc", text=str(e))
                    mes = _('Возникла ошибка. Обратитесь в службу поддержки @beeqb')
                    bot.send_message(user.chat_id, mes)

            except Exception as e:
                Log.objects.create(bot_user=user, type_log="error_btc", text=str(e))
                mes = _('Возникла ошибка. Обратитесь в службу поддержки @beeqb')
                bot.send_message(user.chat_id, mes)

            try:
                kurs = json.loads(
                    requests.get('https://api.coinmarketcap.com/v1/ticker/bitcoin/?convert=%s' % user.currency).text)[
                    0]['price_' + user.currency.lower()]
                s1 = '~ %.2f %s' % (round(float(kurs) * available_balance, 2), user.currency)
                s2 = '~ %.2f %s' % (round(float(kurs) * pending_received_balance, 2), user.currency)
            except:
                s1 = ''
                s2 = ''

            mes = _('Ваш баланс:\n%.8fBTC\n%s\n\n') % (available_balance, s1)
            mes += _('Ожидает подтверждения:\n%.8fBTC\n%s') % (pending_received_balance, s2)

            bot.send_message(chat_id, mes)

            return HttpResponse('OK')

        if text == _('Получить'):
            mes = _('Адрес вашего кошелька:\n%s\n\nQR код вашего кошелька:') % user.btc_wallet
            bot.send_message(chat_id, mes)
            bot.send_photo(chat_id, 'http://www.btcfrog.com/qr/bitcoinPNG.php?address=%s' % user.btc_wallet)

            return HttpResponse('OK')

        if text == _('Настройки'):
            mes = _(
                'Здесь вы можете:\n-изменить язык интерфейса\n-привязать телефон, чтобы Вам могли совершать переводы по телефону\n-изменить валюту эквивалента для биткоина')
            button = telebot.types.ReplyKeyboardMarkup(True, False)
            b1 = telebot.types.KeyboardButton(text=_('Изменить язык'))
            b2 = telebot.types.KeyboardButton(text=_('Привязать телефон'), request_contact=True)
            b3 = telebot.types.KeyboardButton(text=_('Изменить валюту'))
            b4 = telebot.types.KeyboardButton(text=_('Главное меню'))
            button.add(b1, b2, b3, b4)
            bot.send_message(chat_id, mes, reply_markup=button)
            return HttpResponse('OK')

        if text == _('Изменить язык'):
            mes = 'Choose language / Выберите язык'
            button = telebot.types.ReplyKeyboardMarkup(True, False)
            button.row('Русский')
            button.row('English')
            bot.send_message(chat_id, mes, reply_markup=button)
            return HttpResponse('OK')

        if text == _('Изменить валюту'):
            mes = _('Выберите валюту')
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.row_width = 5
            b1 = telebot.types.InlineKeyboardButton(text='USD', callback_data='currencyUSD')
            b2 = telebot.types.InlineKeyboardButton(text='BRL', callback_data='currencyBRL')
            b3 = telebot.types.InlineKeyboardButton(text='CAD', callback_data='currencyCAD')
            b4 = telebot.types.InlineKeyboardButton(text='CHF', callback_data='currencyCHF')
            b5 = telebot.types.InlineKeyboardButton(text='AUD', callback_data='currencyAUD')
            keyboard.add(b1, b2, b3, b4, b5)
            b1 = telebot.types.InlineKeyboardButton(text='CNY', callback_data='currencyCNY')
            b2 = telebot.types.InlineKeyboardButton(text='CZK', callback_data='currencyCZK')
            b3 = telebot.types.InlineKeyboardButton(text='DKK', callback_data='currencyDKK')
            b4 = telebot.types.InlineKeyboardButton(text='EUR', callback_data='currencyEUR')
            b5 = telebot.types.InlineKeyboardButton(text='GBP', callback_data='currencyGBP')
            keyboard.add(b1, b2, b3, b4, b5)
            b1 = telebot.types.InlineKeyboardButton(text='HKD', callback_data='currencyHKD')
            b2 = telebot.types.InlineKeyboardButton(text='HUF', callback_data='currencyHUF')
            b3 = telebot.types.InlineKeyboardButton(text='IDR', callback_data='currencyIDR')
            b4 = telebot.types.InlineKeyboardButton(text='ILS', callback_data='currencyILS')
            b5 = telebot.types.InlineKeyboardButton(text='INR', callback_data='currencyINR')
            keyboard.add(b1, b2, b3, b4, b5)
            b1 = telebot.types.InlineKeyboardButton(text='JPY', callback_data='currencyJPY')
            b2 = telebot.types.InlineKeyboardButton(text='KRW', callback_data='currencyKRW')
            b3 = telebot.types.InlineKeyboardButton(text='MXN', callback_data='currencyMXN')
            b4 = telebot.types.InlineKeyboardButton(text='MYR', callback_data='currencyMYR')
            b5 = telebot.types.InlineKeyboardButton(text='NOK', callback_data='currencyNOK')
            keyboard.add(b1, b2, b3, b4, b5)
            b1 = telebot.types.InlineKeyboardButton(text='NZD', callback_data='currencyNZD')
            b2 = telebot.types.InlineKeyboardButton(text='PHP', callback_data='currencyPHP')
            b3 = telebot.types.InlineKeyboardButton(text='RUB', callback_data='currencyRUB')
            b4 = telebot.types.InlineKeyboardButton(text='SEK', callback_data='currencySEK')
            b5 = telebot.types.InlineKeyboardButton(text='CLP', callback_data='currencyCLP')
            keyboard.add(b1, b2, b3, b4, b5)
            b1 = telebot.types.InlineKeyboardButton(text='SGD', callback_data='currencySGD')
            b2 = telebot.types.InlineKeyboardButton(text='THB', callback_data='currencyTHB')
            b3 = telebot.types.InlineKeyboardButton(text='TRY', callback_data='currencyTRY')
            b4 = telebot.types.InlineKeyboardButton(text='TWD', callback_data='currencyTWD')
            b5 = telebot.types.InlineKeyboardButton(text='ZAR', callback_data='currencyZAR')
            keyboard.add(b1, b2, b3, b4, b5)
            bot.send_message(chat_id, mes, reply_markup=keyboard)
            return HttpResponse('OK')

        if callback_data.find('currency') != -1:
            currency = callback_data[8:]
            user.currency = currency
            user.save()

            mes = _('Вы изменили валюту эквивалента на %s') % currency
            bot.edit_message_text(chat_id=data["callback_query"]["message"]["chat"]["id"],
                                  message_id=data["callback_query"]["message"]["message_id"], text=mes)

            return HttpResponse('OK')

        if text == _('Поддержка'):
            mes = _('Если у вас возникли вопросы или трудности при использовании кошелька, обратитесь в официальный чат @beeqb')
            bot.send_message(user.chat_id, mes)
            return HttpResponse('OK')

        if text == _('История'):

            try:

                response = block_io.get_transactions(type='sent', addresses=user.btc_wallet)

                if response["status"] == "success":
                    # print(response)
                    mes = _("Исходящие:\n")
                    txs = response["data"]["txs"]
                    if txs == []:
                        mes += _('Пусто')

                    for tx in txs:
                        # print(tx)
                        mes += _('Дата: %s\n') % datetime.fromtimestamp(int(tx['time'])).strftime('%Y-%m-%d %H:%M:%S')
                        mes += _('Сумма: %sBTC\n') % tx['amounts_sent'][0]['amount']
                        # print(mes)
                        # from_wallet = tx['senders'][0]
                        # try:
                        #     from_wallet = BotUser.objects.get(btc_wallet = from_wallet).fio #.decode("utf-8")
                        # except:
                        #     pass
                        # mes += 'От: %s\n' % from_wallet
                        to_wallet = tx['amounts_sent'][0]['recipient']
                        # print(to_wallet)
                        try:
                            u = BotUser.objects.get(btc_wallet=to_wallet)
                            print(u)
                            to_wallet = u.fio
                            if u.username is not None or u.username == '':
                                to_wallet += ' (@%s)' % u.username
                            if u.phone_number is not None or u.phone_number == '':
                                to_wallet += ' %s' % u.phone_number
                        except Exception as e:
                            print(str(e))
                            pass
                        mes += _('Кому: %s\n\n') % to_wallet

                    bot.send_message(user.chat_id, mes)

                else:
                    Log.objects.create(bot_user=user, type_log="error_btc", text=json.dumps(response))
                    mes = _('Возникла ошибка. Обратитесь в службу поддержки @beeqb')
                    bot.send_message(user.chat_id, mes)

            except Exception as e:
                try:
                    Log.objects.create(bot_user=user, type_log="error_btc", text=str(e))
                    mes = _('Возникла ошибка. Обратитесь в службу поддержки @beeqb')
                    bot.send_message(user.chat_id, mes)
                except:
                    pass

            sleep(0.5)

            try:

                response = block_io.get_transactions(type='received', addresses=user.btc_wallet)

                # print(response)

                if response["status"] == "success":
                    mes = _("Входящие:\n")
                    txs = response["data"]["txs"]
                    # print(txs)
                    if txs == []:
                        mes += _('Пусто')

                    for tx in txs:
                        # print(tx)
                        mes += _('Дата: %s\n') % datetime.fromtimestamp(tx['time']).strftime('%Y-%m-%d %H:%M:%S')
                        # mes += 'Подтверждений: %s' % tx['confirmations']
                        mes += _('Сумма: %sBTC\n') % tx['amounts_received'][0]['amount']
                        from_wallet = tx['senders'][0]
                        try:
                            u = BotUser.objects.get(btc_wallet=from_wallet)
                            print(u)
                            from_wallet = u.fio
                            if u.username is not None or u.username == '':
                                from_wallet += ' (@%s)' % u.username
                            if u.phone_number is not None or u.phone_number == '':
                                from_wallet += ' %s' % u.phone_number
                        except Exception as e:
                            print(str(e))
                            pass
                        mes += _('От: %s\n\n') % from_wallet

                        # to_wallet = tx['amounts_received'][0]['recipient']
                        # try:
                        #     to_wallet = BotUser.objects.get(btc_wallet = to_wallet).fio #.decode("utf-8")
                        # except:
                        #     pass
                        # mes += 'Кому: %s\n\n' % to_wallet

                    bot.send_message(chat_id, mes)

                else:
                    Log.objects.create(bot_user=user, type_log="error_btc", text=json.dumps(response))
                    mes = _('Возникла ошибка. Обратитесь в службу поддержки @beeqb')
                    bot.send_message(user.chat_id, mes)

            except Exception as e:
                try:
                    Log.objects.create(bot_user=user, type_log="error_btc", text=str(e))
                    mes = _('Возникла ошибка. Обратитесь в службу поддержки @beeqb')
                    bot.send_message(user.chat_id, mes)
                except:
                    pass

        if text == _('Отправить'):

            try:
                response = block_io.get_address_balance(labels=str(chat_id))
                print(response)
                if response["status"] == "success":
                    available_balance = float(response["data"]["available_balance"])
                else:
                    Log.objects.create(bot_user=user, type_log="error_btc", text=str(e))
                    mes = _('Возникла ошибка. Обратитесь в службу поддержки @beeqb')
                    bot.send_message(user.chat_id, mes)

            except Exception as e:
                Log.objects.create(bot_user=user, type_log="error_btc", text=str(e))
                mes = _('Возникла ошибка. Обратитесь в службу поддержки @beeqb')
                bot.send_message(user.chat_id, mes)

            mes = _('Ваш баланс %.8fBTC.\nВведите адрес кошелька или номер телефона в формате “+12223334455” или имя пользователя в формате "@username" кому хотите перевести деньги.') % available_balance

            # mes = 'Введите сумму BTC, которую хотите перевести:'
            button = telebot.types.ReplyKeyboardMarkup(True, False)
            button.row(_('Главное меню'))
            bot.send_message(chat_id, mes, reply_markup=button)

            user.step = 'input_whom_btc_withdraw'
            user.save()

            return HttpResponse('OK')

        if user.step == 'input_whom_btc_withdraw':

            text = text.replace('+', '').replace(')', '').replace('(', '').replace('-', '').replace(' ', '')

            match = re.search(r'^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$', text)
            if match is not None:
                mes = _('Введите сумму BTC, которую хотите перевести:')
                user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
                user_markup.row(_('Главное меню'))
                bot.send_message(chat_id, mes, reply_markup=user_markup)
                # user.wallet_btc = text
                user.step = 'input_amount_btc_withdraw'
                user.wallet_btc_withdraw = text
                user.save()
                return HttpResponse('OK')

            else:

                if text[0] == '@':

                    try:
                        u = BotUser.objects.get(username__iexact=text[1:].lower())

                        mes = _('Введите сумму BTC, которую хотите перевести:')
                        user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
                        user_markup.row(_('Главное меню'))
                        bot.send_message(chat_id, mes, reply_markup=user_markup)
                        # user.wallet_btc = text
                        user.step = 'input_amount_btc_withdraw'
                        user.wallet_btc_withdraw = str(u.chat_id)
                        user.save()

                    except:

                        mes = _('Ошибка! Пользователь с таким именем не зарегистрирован.')
                        user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
                        user_markup.row(_('Главное меню'))
                        bot.send_message(chat_id, mes, reply_markup=user_markup)

                else:

                    match = re.search(r'^[0-9]{5,14}$', text)

                    if match is not None:
                        try:
                            u = BotUser.objects.get(phone_number=text)

                            mes = _('Введите сумму BTC, которую хотите перевести:')
                            user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
                            user_markup.row(_('Главное меню'))
                            bot.send_message(chat_id, mes, reply_markup=user_markup)
                            # user.wallet_btc = text
                            user.step = 'input_amount_btc_withdraw'
                            user.wallet_btc_withdraw = str(u.chat_id)
                            user.save()

                        except:

                            mes = _('Ошибка! Пользователь с таким телефоном не зарегистрирован.')
                            user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
                            user_markup.row(_('Главное меню'))
                            bot.send_message(chat_id, mes, reply_markup=user_markup)
                    else:

                        mes = _('Ошибка! Некорректное значение.')
                        user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
                        user_markup.row(_('Главное меню'))
                        bot.send_message(chat_id, mes, reply_markup=user_markup)

            return HttpResponse('OK')

        if user.step == 'input_amount_btc_withdraw':

            text = text.replace(',', '.').replace(' ', '')

            if not is_digit(text):
                mes = _('Ошибка: Значение должно быть числовым. Введите другую сумму.')
                user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
                user_markup.row(_('Главное меню'))
                bot.send_message(chat_id, mes, reply_markup=user_markup)
                return HttpResponse('OK')

            try:

                response = block_io.get_address_balance(labels=str(chat_id))
                print(response)

                if response["status"] == "success":
                    available_balance = float(response["data"]["available_balance"])
                else:
                    Log.objects.create(bot_user=user, type_log="error_btc", text=str(e))
                    mes = _('Возникла ошибка. Обратитесь в службу поддержки @beeqb')
                    bot.send_message(user.chat_id, mes)
                    return HttpResponse('OK')

            except Exception as e:
                Log.objects.create(bot_user=user, type_log="error_btc", text=str(e))
                mes = _('Возникла ошибка. Обратитесь в службу поддержки @beeqb')
                bot.send_message(user.chat_id, mes)

            summa = float(text)

            if summa < 0.00001:
                mes = _('Ошибка! Минимальная сумма - 0.00001BTC. Введите другую сумму.')
                user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
                user_markup.row(_('Главное меню'))
                bot.send_message(chat_id, mes, reply_markup=user_markup)
                return HttpResponse('OK')

            # available_balance = 1

            if summa > available_balance:
                mes = _('Ошибка! У вас недостаточно средств на счету')
                user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
                user_markup.row(_('Главное меню'))
                bot.send_message(chat_id, mes, reply_markup=user_markup)
                return HttpResponse('OK')

            bot.send_message(chat_id, _('Ожидайте...'))

            if isint(user.wallet_btc_withdraw):
                u = BotUser.objects.get(chat_id=int(user.wallet_btc_withdraw))
                mes = _('Вы уверены, что хотите перевести %.8f BTC пользователю %s?\n') % (summa, str(u.fio))
                to_wallet = u.btc_wallet
            else:
                mes = _('Вы уверены, что хотите перевести %.8f BTC на кошелек %s?\n') % (summa, user.wallet_btc_withdraw)
                u = None
                to_wallet = user.wallet_btc_withdraw

            procent_fee = settings.procent_fee
            procent_amount = summa * procent_fee

            if procent_amount < 0.00001:
                procent_amount = 0.00001

            procent_wallet = settings.wallet_for_fee

            amounts_str = '%.8f' % summa + ',' + '%.8f' % procent_amount
            print(amounts_str)
            #print(wallet_str)

            wallet_str = to_wallet + ',' + procent_wallet

            print(wallet_str)

            try:
                response = block_io.get_network_fee_estimate(amounts='%.8f' % summa, to_addresses=to_wallet,
                                                             priority='low')
                print(response)
                lowfee = response["data"]["estimated_network_fee"]
            except Exception as e:
                bot.send_message(chat_id, str(e))
                return HttpResponse('OK')

            if BotUser.objects.filter(btc_wallet=to_wallet).exists():

                medfee = None
                highfee = None

            else:

                try:

                    sleep(0.5)
                    response = block_io.get_network_fee_estimate(amounts='%.8f' % summa, to_addresses=to_wallet,
                                                                 priority='medium')
                    medfee = response["data"]["estimated_network_fee"]

                except Exception as e:
                    medfee = None

                try:
                    sleep(0.5)
                    response = block_io.get_network_fee_estimate(amounts='%.8f' % summa, to_addresses=to_wallet,
                                                                 priority='high')
                    highfee = response["data"]["estimated_network_fee"]
                except Exception as e:
                    highfee = None

            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.add(telebot.types.InlineKeyboardButton(text=_('Перевести за %sBTC') % lowfee,
                                                            callback_data='yes_btc_withdraw_lowfee'))
            if medfee is not None:
                keyboard.add(telebot.types.InlineKeyboardButton(text=_('Перевести за %sBTC') % medfee,
                                                         callback_data='yes_btc_withdraw_medfee'))
            if highfee is not None:
                keyboard.add(telebot.types.InlineKeyboardButton(text=_('Перевести за %sBTC') % highfee,
                                                            callback_data='yes_btc_withdraw_highfee'))

            # keyboard.add(telebot.types.InlineKeyboardButton(text=_('Да, переводить!') , callback_data = 'yes_btc_withdraw' ))
            keyboard.add(telebot.types.InlineKeyboardButton(text=_('Отмена'), callback_data='to_home'))

            bot.send_message(chat_id, mes, reply_markup=keyboard)

            user.step = 'home'
            user.amount_btc_withdraw = summa
            user.save()

            return HttpResponse('OK')

        if callback_data.find('yes_btc_withdraw') != -1:

            try:

                if isint(user.wallet_btc_withdraw):
                    u = BotUser.objects.get(chat_id=int(user.wallet_btc_withdraw))
                    to_wallet = u.btc_wallet
                else:
                    u = None
                    to_wallet = user.wallet_btc_withdraw

                procent_fee = settings.procent_fee

                amount = user.amount_btc_withdraw
                procent_amount = amount * procent_fee

                if procent_amount < 0.00001:
                    procent_amount = 0.00001

                procent_wallet = settings.wallet_for_fee

                amounts_str = '%.8f' % amount + ',' + '%.8f' % procent_amount
                wallet_str = to_wallet + ',' + procent_wallet

                print(amounts_str)
                print(wallet_str)

                if callback_data.find('lowfee') != -1:
                    priority = 'low'
                elif callback_data.find('medfee') != -1:
                    priority = 'medium'
                elif callback_data.find('highfee') != -1:
                    priority = 'high'

                try:
                    #response = block_io.withdraw(amounts=amounts_str, to_addresses=wallet_str, priority=priority)
                    response = block_io.withdraw(amounts='%.8f' % amount, to_addresses=to_wallet, priority=priority)
                except Exception as e:
                    bot.send_message(chat_id, str(e))
                    return HttpResponse('OK')

                print(response)

                if response["status"] == "success":
                    mes = _('Вы успешно отправили: %sBTC') % user.amount_btc_withdraw
                    bot.edit_message_text(chat_id=data["callback_query"]["message"]["chat"]["id"],
                                          message_id=data["callback_query"]["message"]["message_id"], text=mes,
                                          reply_markup=keyboard)

                    if u is not None:
                        bot.send_message(u.chat_id, _("%s вам перевел %.8fBTC.") % (user.fio, amount))

                    # History.objects.create(bot_user = user, trans_id = response["data"]["txid"], trans_type = 'withdraw', wallet_type = 'BTC', summa = summa)
                else:
                    Log.objects.create(bot_user=user, type_log="error_btc", text=json.dumps(response))
                    mes = _('Возникла ошибка. Обратитесь в службу поддержки @beeqb')
                    bot.send_message(user.chat_id, mes)

            except Exception as e:
                try:
                    Log.objects.create(bot_user=user, type_log="error_btc", text=str(e))
                    mes = _('Возникла ошибка. Обратитесь в службу поддержки @beeqb')
                    bot.send_message(user.chat_id, mes)
                except:
                    pass

            user.wallet_btc_withdraw = ''
            user.save()

            return HttpResponse('OK')

        return HttpResponse('OK')


    except Exception as e:
        print(e)
        bot.send_message(354691583, str(e))
        return HttpResponse('OK')

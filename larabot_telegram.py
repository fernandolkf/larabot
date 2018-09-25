import os
import datetime
import subprocess
import re
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram import ParseMode
from telegram.constants import MAX_MESSAGE_LENGTH

token = os.environ['TELEGRAM_TOKEN']
know_usernames = {'fernandolkf': 'Papai',
                  'liviamorim': 'Mamãe',
                  'kfasolin': 'Dinda',
                  'fdettoni': 'Dindo',
                  }
updater = Updater(token=token)
dispatcher = updater.dispatcher


def _in_week(date_event):
    """
    Check if date is in current week

        :param date_event: date in d/m/Y format to check week
        :return bool: if date is the current week
    """

    return datetime.datetime.strptime(date_event, '%d/%m/%Y').isocalendar()[1] == datetime.datetime.now().isocalendar()[1]


def _is_today(date_event):
    """
    Check if date is today

        :param date_event: date in d/m/Y format to check week
        :return bool: if date is today
    """

    return datetime.datetime.strptime(date_event, '%d/%m/%Y').date() == datetime.datetime.now().date()


def _is_weekend(date_event):
    """
    Check if date is weekend

        :param date_event: date in d/m/Y format to check week
        :return bool: if date on the weekend from current week
    """

    if datetime.datetime.strptime(date_event, '%d/%m/%Y').weekday() in [5, 6]:
        return _in_week(date_event)

    return False


def _has_passed(date_event):
    """
    Check if date has already passd

        :param date_event: date in d/m/Y format to check week
        :return bool: if date older then now
    """

    return datetime.datetime.strptime(date_event, '%d/%m/%Y').date() < datetime.datetime.now().date()


def help(bot, update):
    """
    Send the list of bot commands
        :param bot: the bot object
        :param update: the origin of the command
    """

    msg = 'LaraBot, o bot para pegar eventos infantis em Florianópolis. Comandos:\n'
    msg = msg+'/start: dar oi ;)\n'
    msg = msg+'/mes: pega todos eventos do mês\n'
    msg = msg+'/semana: pega todos eventos da semana\n'
    msg = msg+'/fim: pega todos eventos do fim de semana\n'
    msg = msg+'/hoje: pega todos eventos do dia\n'

    send_message(bot, update, msg)


def start(bot, update):
    """
    Bot greetings message
        :param bot: the bot object
        :param update: the origin of the command
    """

    name = update.message.from_user.first_name
    if update.message.from_user.username in know_usernames.keys():
        name = know_usernames[update.message.from_user.username]
    msg = 'Oi {}'.format(name)
    send_message(bot, update, msg)


def mes(bot, update):
    """
    Send all future events from current month
        :param bot: the bot object
        :param update: the origin of the command
    """

    bot.send_message(chat_id=update.message.chat_id,
                     text='Buscando eventos do mês')
    events = get_events()
    msg = ''
    for dia, eventos in events.items():

        if not _has_passed(dia):
            msg = msg + \
                'Dia *{}* tem *{}* eventos:\n\n'.format(dia, len(eventos))

            for evento, local in eventos:
                msg = msg+'*O que*: {}\n*Onde*: {}\n\n'.format(evento, local)

    send_message(bot, update, msg)


def semana(bot, update):
    """
    Send all future events from current week
        :param bot: the bot object
        :param update: the origin of the command
    """

    bot.send_message(chat_id=update.message.chat_id,
                     text='Buscando eventos da semana')
    events = get_events()
    msg = ''
    for dia, eventos in events.items():

        if (_in_week(dia)) and (not _has_passed(dia)):

            msg = msg + \
                'Dia *{}* tem *{}* eventos:\n\n'.format(dia, len(eventos))
            for evento, local in eventos:
                msg = msg+'*O que*: {}\n*Onde*: {}\n\n'.format(evento, local)

    send_message(bot, update, msg)


def fim(bot, update):
    """
    Send all future events from next weekend
        :param bot: the bot object
        :param update: the origin of the command
    """

    bot.send_message(chat_id=update.message.chat_id,
                     text='Buscando eventos do fim de semana')
    events = get_events()
    msg = ''
    for dia, eventos in events.items():
        print(dia)
        print(_has_passed(dia))
        print(_is_weekend(dia))
        if (_is_weekend(dia)) and (not _has_passed(dia)):

            msg = msg + \
                'Dia *{}* tem *{}* eventos:\n\n'.format(dia, len(eventos))
            for evento, local in eventos:
                msg = msg+'*O que*: {}\n*Onde*: {}\n\n'.format(evento, local)

    send_message(bot, update, msg)


def hoje(bot, update):
    """
    Send all future events from today
        :param bot: the bot object
        :param update: the origin of the command
    """

    bot.send_message(chat_id=update.message.chat_id,
                     text='Buscando eventos de hoje')
    events = get_events()
    msg = ''
    for dia, eventos in events.items():

        if _is_today(dia):

            if len(eventos) == 0:
                msg = 'Não tem eventos cadastrados hoje (*{}*)'.format(
                    dia, len(eventos))
                break

            msg = 'Dia *{}* tem *{}* eventos:\n\n'.format(dia, len(eventos))
            for evento, local in eventos:
                msg = msg+'*O que*: {}\n*Onde*: {}\n\n'.format(evento, local)

            break
    send_message(bot, update, msg)


def send_message(bot, update, msg):
    """
    Send message for telegram chat. Split long messages 
        :param bot: the bot object
        :param update: the origin of the command
        :param msg: message to send
    """

    if len(msg) > MAX_MESSAGE_LENGTH:
        send_message(bot, update, msg[:MAX_MESSAGE_LENGTH])
        send_message(bot, update, msg[MAX_MESSAGE_LENGTH:])
    else:
        try:
            bot.send_message(chat_id=update.message.chat_id,
                             text=msg, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            print(e)
            bot.send_message(chat_id=update.message.chat_id,
                             text='Erro {} :('.format(str(e)))


def get_events():
    """
    Get all events from current month using scrapy framework
    """

    events = {}
    bash_command = 'scrapy runspider scrapy_test.py'
    date_regex = re.compile(r'\d?\d/\d?\d/\d\d\d\d')

    process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
    output, _ = process.communicate()

    has_date = False
    date_event = None
    lines = output.decode('utf-8').split('\n')
    for line in lines:

        if line:
            date_match = date_regex.search(line)

            if date_match:
                date_event = date_match.group()
                events[date_event] = []
                has_date = True

            elif has_date:
                events[date_event].append(line.split('\t'))

    return events


def main():

    handles = [CommandHandler('start', start),
               CommandHandler('mes', mes),
               CommandHandler('hoje', hoje),
               CommandHandler('semana', semana),
               CommandHandler('help', help),
               CommandHandler('fim', fim)]

    for handle in handles:
        dispatcher.add_handler(handle)

    updater.start_polling()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()

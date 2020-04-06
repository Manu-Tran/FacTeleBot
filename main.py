import asyncio
import re
import time
import os
import logging
from os.path import dirname


from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

import telegram
from telegram.ext import Updater
from telegram.ext import MessageHandler, Filters
from telegram.ext import CommandHandler

from mcrcon import MCRcon

logger = logging.getLogger('telegram')
logger.setLevel(logging.DEBUG)


class FacTeleBot():
    # Interacts with telegram
    def __init__(self, channel_id, data_dir, bot_token, host):
        self.channel_id = channel_id
        self.data_dir = data_dir
        self.host = host
        self.updater = Updater(bot_token, use_context=True)
        with open(data_dir + "/config/rconpw", "r") as f:
            self.pw = f.readline().strip()


    def send_to_factorio(self, update, context):
        msg = "{}: {}".format(update.message.from_user.first_name, update.message.text)

        logger.debug("Msg from telegram: \"{}\"".format(msg))
        with MCRcon(self.host, self.pw, port=27015) as rcon:
            resp = rcon.command(msg)
            logger.debug("Response from factorio: '%s'", resp)

    def send_to_telegram(self, text):
        self.updater.bot.sendMessage(chat_id=self.channel_id, text=text)

    def run(self):
        self.updater.dispatcher.add_handler(MessageHandler(Filters.text, self.send_to_factorio))
        self.updater.start_polling()
        self.updater.idle()


class FacLogHandler(PatternMatchingEventHandler):
    # Watches a log file for useful events
    def __init__(self, fbot, logfile):
        self.fbot = fbot
        self.log_loc = logfile
        self.logfile = None

        super().__init__([logfile])
        self.spin_up()
        self.observer = Observer()
        self.observer.schedule(self, dirname(self.log_loc), recursive=False)
        self.observer.start()

    def spin_up(self):
        # When the bridge first starts up, wait for factorio to start and
        # create the log file, then read to the end so we don't duplicate
        # any messages

        self.logfile = None
        elapsed = 0
        while self.logfile is None:
            try:
                self.logfile = open(self.log_loc, 'r')
            except:
                time.sleep(1)
                if elapsed > 20:
                    raise Exception("Timed out opening log file!")

        # read up to last line before EOF
        for line in self.logfile:
            pass

    def on_modified(self, event):
        # When a line is written to the log, handle any action needed.
        # Right now, there's only chat.
        for line in self.logfile:
            m = re.match("^[-0-9: ]+\[([A-Z]+)\] (.+)$", line)
            if m is None:
                continue
            # Skip messages from server
            if  "[CHAT] <server>:" in line :
                continue
            self.default_handler(m.group(1), m.group(2))

    def default_handler(self, kind, text):
        logger.debug("Factorio sent '%s': '%s'", kind, text)
        self.fbot.send_to_telegram(text)

if __name__ == "__main__":
    logger.info("Starting telegram/factorio bridge....")
    data_dir = os.environ.get("FACTORIO_DIR_PATH", ".")
    fb = FacTeleBot(os.environ['TELEGRAM_CHANNEL_ID'],
                    data_dir,
                    os.environ["TELEGRAM_BOT_TOKEN"],
                    os.environ.get("FACTORIO_HOST", '127.0.0.1'))
    bot = FacLogHandler(fb, data_dir + "/console.log")
    fb.run()

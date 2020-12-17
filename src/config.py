import os

from enum import Enum

BOT_API_SECRET_NAME = 'LATEX_AUTO_BOT_AUTH'

WEBHOOK_HOST = 'latex-telegram-bot-idss7f3isa-ey.a.run.app'
WEBHOOK_PORT = int(os.environ.get('PORT', 80))
WEBHOOK_LISTEN = '0.0.0.0'

WEBHOOK_URL_BASE = "https://%s" % (WEBHOOK_HOST)

DATABASE_FILE = 'local_db.sqlite'

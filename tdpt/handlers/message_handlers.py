import logging

from telegram.ext import Filters, MessageHandler


class UploadNewTorrent(MessageHandler):

    filters = Filters.document.mime_type('application/x-bittorrent')

    def __init__(self, client):
        self.client = client
        super().__init__(self.filters, self.callback)

    def callback(self, update, context):
        torrent = update.message.document.get_file()
        file_name = update.message.document.file_name
        self.client.add_torrent(file_name, torrent)
        logging.info('Added new torrent file %s', file_name)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Added *{}*'.format(update.message.document.file_name),
            parse_mode='markdown')

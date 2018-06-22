import json
import requests
import logging
import logging.handlers

import traceback


def bg_cb(sess, resp):
    """ Don't do anything with the response """
    pass


class SlackHandler(logging.Handler):
    def __init__(self, config):

        defaults = {'channel': 'notifications',
                    'icon_emoji': ':atom_symbol:',
                    'username': 'reactor-bot'}
        if not isinstance(config, dict):
            config = {}
        defaults.update(config)

        if defaults['channel'].find('#') == -1:
            defaults['channel'] = '#' + defaults['channel']

        self.settings = defaults
        super(SlackHandler, self).__init__()

    def get_full_message(self, record):
        if record.exc_info:
            return '\n'.join(traceback.format_exception(*record.exc_info))
        else:
            return record.getMessage()

    # async post
    # def emit(self, record):
    #     log_entry = self.format(record)
    #     webhook_url = self.settings.get('webhook', None)
    #     payload = {'text': log_entry,
    #                'icon_emoji': self.settings.get('icon_emoji',
    #                                                ':robot_face:'),
    #                'channel': self.settings.get('channel',
    #                                             '#notifications'),
    #                'username': self.settings.get('username',
    #                                              'reactor-bot')}
    #     if webhook_url is not None:
    #         try:
    #             session.post(webhook_url, data=payload,
    #                          headers={"Content-type": "application/json"},
    #                          background_callback=bg_cb)
    #         except (KeyboardInterrupt, SystemExit):
    #             raise
    #         except Exception:
    #             self.handleError(record)

    def emit(self, record):
        log_entry = self.format(record)
        webhook_url = self.settings.get('webhook', None)
        payload = {'text': log_entry,
                   'icon_emoji': self.settings.get('icon_emoji',
                                                   ':robot_face:'),
                   'channel': self.settings.get('channel',
                                                '#notifications'),
                   'username': self.settings.get('username',
                                                 'reactor-bot')}
        if webhook_url is not None:
            try:
                requests.post(webhook_url,
                              data=json.dumps(payload),
                              headers={"Content-type": "application/json"}
                              ).content
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception:
                self.handleError(record)
        else:
            print("_REACTOR_SLACK_WEBHOOK not defined")

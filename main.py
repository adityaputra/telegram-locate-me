import StringIO
import json
import logging
import random
import urllib
import urllib2

# for sending images
from PIL import Image
import multipart

# standard app engine imports
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
import webapp2

# token and others
import defines

# location services
import location


# ================================

class EnableStatus(ndb.Model):
    # key name: str(chat_id)
    enabled = ndb.BooleanProperty(indexed=False, default=False)
    uname = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)


# ================================

def setEnabled(chat_id, yes, uname):
    es = EnableStatus.get_or_insert(str(chat_id))
    es.enabled = yes
    es.uname = uname
    es.put()

def getEnabled(chat_id):
    es = EnableStatus.get_by_id(str(chat_id))
    if es:
        return es.enabled
    return False


# ================================

class MeHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(defines.BASE_URL + 'getMe'))))


class GetUpdatesHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(defines.BASE_URL + 'getUpdates'))))


class SetWebhookHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(json.dumps(json.load(urllib2.urlopen(defines.BASE_URL + 'setWebhook', urllib.urlencode({'url': url})))))


class WebhookHandler(webapp2.RequestHandler):
    def post(self):
        urlfetch.set_default_fetch_deadline(60)
        body = json.loads(self.request.body)
        logging.info('request body:')
        logging.info(body)
        self.response.write(json.dumps(body))

        update_id = body['update_id']
        message = body['message']
        message_id = message.get('message_id')
        date = message.get('date')
        text = message.get('text')
        fr = message.get('from')
        chat = message['chat']
        chat_id = chat['id']
        latlang = message.get('location')
        if latlang:
            latitude = latlang['latitude']
            longitude = latlang['longitude']


        def reply(msg=None, img=None):
            if msg:
                resp = urllib2.urlopen(defines.BASE_URL + 'sendMessage', urllib.urlencode({
                    'chat_id': str(chat_id),
                    'text': msg.encode('utf-8'),
                    'disable_web_page_preview': 'true',
                    'reply_to_message_id': str(message_id),
                })).read()
            elif img:
                resp = multipart.post_multipart(defines.BASE_URL + 'sendPhoto', [
                    ('chat_id', str(chat_id)),
                    ('reply_to_message_id', str(message_id)),
                ], [
                    ('photo', 'image.jpg', img),
                ])
            else:
                logging.error('no msg or img specified')
                resp = None

            logging.info('send response:')
            logging.info(resp)

        if not text:
            logging.info('no text')
            if latlang:
                logging.info('latlang: ')
                logging.info(latlang)
                logging.info(latitude)
                logging.info(longitude)
                location.setLocation(chat_id, latlang, latitude, longitude)
                logging.info('update location: ')
                reply('Alright, what do you need?\n1. /hospital\n2. /school')

            return


        def displayList(resultSet):
            text = ''
            i = 0
            for data in resultSet['places']:
                i = i+1
                text += str(i) + '.\t' + json.dumps(data['title']) + '\n'
                text += '\tWikimapia: http://wikimapia.org/' + json.dumps(data['id']) + '/\n'
                text += '\tGoogle Maps: https://maps.google.com/maps?q=' + json.dumps(data['location']['lat']) + ',' + json.dumps(data['location']['lon']) + '&ll=' + json.dumps(data['location']['lat']) + ',' + json.dumps(data['location']['lon']) + '&z=15\n'

                if i == 10:
                    break;
            if i == 0:
                reply('No result nearby. Sorry.')

            else:
                resp = urllib2.urlopen(defines.BASE_URL + 'sendMessage', urllib.urlencode({
                    'chat_id': str(chat_id),
                    'text': text.encode('utf-8'),
                    'disable_web_page_preview': 'true',
                    'reply_to_message_id': str(message_id),
                })).read()
                logging.info('send response:')
                logging.info(resp)

        def getResult(category):
            latlangparam = location.getLocation(chat_id)
            if latlangparam:
                nearest = location.getNearest(str(category), str(latlangparam))
                displayList(nearest)
            else:
                reply('Please send me your location')

        if text.startswith('/'):
            if text == '/start':
                reply('Now, send me your current location')
                setEnabled(chat_id, True, fr['username'])
            elif text == '/stop':
                reply('Bot disabled')
                setEnabled(chat_id, False, fr['username'])
            elif text == '/help':
                reply('Hello. I will help you to find places you need.\nTo begin, type /start then send your current location. After that, type any command below to find nearest local places that you need: \n1. /hospital\n2. /school')
            elif text == '/hospital':
                getResult('287')
            elif text == '/fuel':
                getResult('6644')
            elif text == '/transportation':
                getResult('2134')
            elif text == '/restaurant':
                getResult('74')
            elif text == '/shop':
                getResult('7')
            elif text == '/hotel':
                getResult('50')
            elif text == '/religion':
                getResult('1663')
            elif text == '/school':
                getResult('203')
            elif text == '/leisure':
                getResult('4')
            elif text == '/pharmacy':
                getResult('787')
            elif text == '/image':
                img = Image.new('RGB', (512, 512))
                base = random.randint(0, 16777216)
                pixels = [base+i*j for i in range(512) for j in range(512)]  # generate sample image
                img.putdata(pixels)
                output = StringIO.StringIO()
                img.save(output, 'JPEG')
                reply(img=output.getvalue())
            else:
                reply('What command?')

        # CUSTOMIZE FROM HERE

        elif 'who are you' in text:
            reply('LocateMe Bot, created by adityaputra: https://github.com/adityaputra/telegram-locate-me')
        elif 'what time' in text:
            reply('look at the top-right corner of your screen!')
        else:
            if getEnabled(chat_id):
                try:
                    resp1 = json.load(urllib2.urlopen('http://www.simsimi.com/requestChat?lc=en&ft=1.0&req=' + urllib.quote_plus(text.encode('utf-8'))))
                    back = resp1.get('res')
                except urllib2.HTTPError, err:
                    logging.error(err)
                    back = str(err)
                if not back:
                    reply('okay...')
                elif 'I HAVE NO RESPONSE' in back:
                    reply('you said something with no meaning')
                else:
                    reply(back)
            else:
                logging.info('not enabled for chat_id {}'.format(chat_id))


app = webapp2.WSGIApplication([
    ('/me', MeHandler),
    ('/updates', GetUpdatesHandler),
    ('/set_webhook', SetWebhookHandler),
    ('/webhook', WebhookHandler),
], debug=True)

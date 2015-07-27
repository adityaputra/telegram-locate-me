import StringIO
import json
import logging
import urllib
import urllib2
from google.appengine.api import urlfetch
from google.appengine.ext import ndb

# ==========================
class LocationStatus(ndb.Model):
    # location = ndb.StringProperty()
    chat_id = ndb.StringProperty()
    latitude = ndb.StringProperty()
    longitude = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)

# ==========================
def setLocation(chat_id, coordinate, latitude, longitude):
    loc = LocationStatus(parent=ndb.Key("LocationUpdate",
                                           "LocationUpdate"),
                            chat_id = str(chat_id),
                            # location=coordinate,
                            latitude = str(latitude),
                            longitude = str(longitude))

    setloc = loc.put()
    logging.info(setloc)

# =============================
def getLocation(chatId):

    ls = LocationStatus.query(LocationStatus.chat_id == str(chatId)).order(-LocationStatus.date)
    if ls:
        logging.info('getLocation: ')
        for l in ls:
            logging.info(l.latitude)
            logging.info(l.longitude)
            latlangparam = '&lat='+str(l.latitude)+'+&lon='+str(l.longitude)
            logging.info(latlangparam)
            return (latlangparam)
    else:
        logging.info('getLocation: ls empty')
        return False

# =============================
def getNearest(category, latlang):
    getNearestUrl = 'http://api.wikimapia.org/?key=example&function=place.getnearest'+str(latlang)+'&format=json&pack=&language=en&count=50&category='+str(category)
    urlfetch.set_default_fetch_deadline(60)
    result = json.load(urllib2.urlopen(getNearestUrl))
    logging.info(result)
    logging.info('getNearest done')
    return result

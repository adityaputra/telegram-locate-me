import logging
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

    # loc = LocationStatus.get_or_insert(str(chat_id), str(coordinate))
    # loc.enabled = yes
    setloc = loc.put()
    logging.info(setloc)

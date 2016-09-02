import requests
import time
from config import config

base_url = 'https://api.twitter.com/'
limit = 200
upper_limit = limit
screen_name = 'realDonaldTrump'

hold_time = 5

class Punctuation:
    items = {
        '!': 0,
        '?': 0,
        ',': 0,
        '.': 0,
        "'": 0,
        'none': 0,
        'total': 0
    }
    def count(self, string):
        found = False
        for key, val in self.items.iteritems():
            if key in ['none', 'total']:
                continue
            if found is False and string.count(key) is not 0:
                self.items[key] = val + string.count(key)
                found = True
        if found is False:
            self.items['none'] = self.items['none'] + 1
        self.items['total'] = self.items['total'] + 1

class BaseRequest:
    def __init__(self, base_url, resource, config):
        self.resource = base_url + resource
        self.config = config

    def buildString(self):
        string = self.config['consumer_key'] + ":" + self.config['consumer_secret']
        return string.encode('base64', 'strict')

    def buildAuthorizationString(self, data={'type': '', 'value': ''}):
        typeStr = data['type'] or 'Basic'
        valStr = data['value'] or self.buildString()
        return typeStr + ' ' + valStr

    def buildHeader(self, data=None):
        authorization = self.buildAuthorizationString()
        user_agent = 'Dat App'
        authorization = authorization.replace('\n', '')
        return {'Authorization': authorization,'User-Agent': user_agent}

class Auth(BaseRequest):
    def get(self):
        headers = self.buildHeader()
        r = requests.post(self.resource, headers=headers, data={'grant_type': 'client_credentials'})
        response = r.json()
        headers['Authorization'] = self.buildAuthorizationString({'type': 'Bearer', 'value': response['access_token']})
        return headers


class Tweets(BaseRequest):
    payload = {
        'screen_name': screen_name,
        'count': limit
    }

    def get(self, screen_name):
        r = requests.get(self.resource, params=self.payload, headers=self.config)
        tweets = r.json()
        self.payload['max_id'] = tweets[-1]['id']
        return tweets

class Count(BaseRequest):
    def get(self, screen_name):
        r = requests.get(self.resource, params={'screen_name': screen_name}, headers=self.config)
        temp = r.json()
        return temp['statuses_count']

parser = Punctuation()

auth = Auth(base_url, 'oauth2/token', config)
auth_obj = auth.get()

count = Count(base_url, '1.1/users/show.json', auth_obj)
num = count.get(screen_name)
#num = 1000

tweets = Tweets(base_url, '1.1/statuses/user_timeline.json', auth_obj)
while (upper_limit < num):
    collection = tweets.get(screen_name)
    for item in collection:
        try:
            item['retweeted_status']
            item['quoted_status']
        except Exception, e:
            parser.count(item['text'])
    print str(upper_limit) + "\n"
    print parser.items
    upper_limit = upper_limit + limit
    time.sleep(5)


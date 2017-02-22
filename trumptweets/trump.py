import requests
import time
from config import config

base_url = 'https://api.twitter.com/'
limit = 200
upper_limit = limit
screen_name = 'realDonaldTrump'

hold_time = 5

class Punctuation:
    symbols = {
        '!': 0,
        '?': 0,
        ',': 0,
        '.': 0,
        "'": 0
    }
    items = {
        'symbols': symbols.copy(),
        'last': symbols.copy(),
        'none': 0,
        'total': 0,
        'device': {
            'iphone': 0,
            'web': 0,
            'android': 0,
            'iPad': 0
        }
    }
    def device(self, string):
        if 'iphone' in string:
            return 'iphone'
        if 'android' in string:
            return 'android'
        if 'Web' or 'TweetDeck' in string:
            return 'web'
        if 'iPad' in string:
            return 'iPad'
        if 'Ads' in string:
            return False
        if 'Periscope' in string:
            return False
        if 'Studio' in string:
            return False
        if 'Instagram' in string:
            return False
        print string
        exit()

    def count(self, tweet):
        string = tweet['text']
        source = tweet['source']
        if self.device(source) is False:
            return
        found = False
        for key, val in self.items['symbols'].iteritems():
            if string.count(key) is not 0:
                self.items['symbols'][key] = val + string.count(key)
                if string.endswith(key):
                    try:
                        self.items['last']['total'] = self.items['last']['total'] + 1
                    except:
                        self.items['last']['total'] = 0
                    self.items['last'][key] = val + 1
                found = True

        if found is False:
            self.items['none'] = self.items['none'] + 1
        # print self.device(source)
        self.items['device'][self.device(source)] =  self.items['device'][self.device(source)] + 1
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
        try:
            if self.payload['max_id'] == int(tweets[-1]['id_str']):
                print tweets
                print 'this is happening naow'
                return False
        except:
            pass
        self.payload['max_id'] = int(tweets[-1]['id_str'])
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
i = 0
tweets = Tweets(base_url, '1.1/statuses/user_timeline.json', auth_obj)
check = True
while (upper_limit < num and check == True):
    collection = tweets.get(screen_name)
    if collection == False:
        check = False
        collection = []
    i = i + 1
    print "\n**************\n"
    print i
    print "\n**************\n"
    for item in collection:
        try:
            item['retweeted_status']
            item['quoted_status']
        except Exception, e:
            parser.count(item)
    # print str(upper_limit) + "\n"
    print parser.items
    upper_limit = upper_limit + limit
    time.sleep(5)



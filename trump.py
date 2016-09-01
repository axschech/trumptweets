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
		'.': 0
	}
	def count(self, string):
		for key, val in self.items.iteritems():
			self.items[key] = val + string.count(key)

class BaseRequest:
	def __init__(self, base_url, resource, config):
		self.resource = base_url + resource
		self.config = config

	def buildString(self):
		string = self.config['consumer_key'] + ":" + self.config['consumer_secret']
		return string.encode('base64', 'strict')

	def buildHeader(self, data=None):
		authorization = data or 'Basic ' + self.buildString()
		user_agent = 'Dat App'
		return {
			'Authorization': authorization,
			'User-Agent': user_agent
		}

class Auth(BaseRequest):
	def get(self):
		headers = self.buildHeader()
		headers['Authorization'] = headers['Authorization'].replace('\n', '')
		r = requests.post(self.resource, headers=headers, data={'grant_type': 'client_credentials'})
		response = r.json()
		return self.buildHeader('Bearer ' + response['access_token'])


class Tweets(BaseRequest):
	def get(self, screen_name):
		r = requests.get(self.resource, params={'screen_name': screen_name, 'count': limit}, headers=self.config)
		return r.json()

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

tweets = Tweets(base_url, '1.1/statuses/user_timeline.json', auth.get())
while (upper_limit < num):
	collection = tweets.get(screen_name)
	for item in collection:
		try:
			item['retweeted_status']
			item['quoted_status']
		except Exception, e:
			parser.count(item['text'])
	upper_limit = upper_limit + limit
	print str(upper_limit) + "\n"
	print parser.items
	time.sleep(5)


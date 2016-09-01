import requests
from config import config

base_url = 'https://api.twitter.com/'
limit = 200

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
		authorization = data or self.buildString()
		authorization = 'Basic ' + authorization
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
		headers['Authorization'] = 'Bearer ' + response['access_token']
		return headers


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
num = count.get('axschech')

tweets = Tweets(base_url, '1.1/statuses/user_timeline.json', auth.get())
collection = tweets.get('axschech')
i = 0
for item in collection:
	i = i + 1
	try:
		item['retweeted_status']
		item['quoted_status']
	except Exception, e:
		parser.count(item['text'])

print parser.items


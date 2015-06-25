import tweepy

redirect_url = '/login/success'
auth = tweepy.OAuthHandler('evjLPx6LKFgjotMaRUNaQtTc0','eQ5BGR6GG2XtHDhCFN9dwA8UEjNjrdMqRCMyFnIqfUSMemZQMA',redirect_url)

try:
	r_url = auth.get_authorization_url()
	print 'Redirect url is %s' % r_url
	#token = session.get('request_token')
	print 'Token is %s' % token
except:
	print 'error getting redirect url'



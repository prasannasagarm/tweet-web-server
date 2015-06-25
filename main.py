import time
import BaseHTTPServer
from pprint import pprint
import urlparse
import tweepy
from SocketServer import ThreadingMixIn
from logger import log # logger.py file in the same directory as this file

HOST_NAME = '0.0.0.0'
PORT_NUMBER = 8003
BASE_URL = 'http://justchillout.in:%s'%PORT_NUMBER

# TODO: Need to encrypt these tokens
CONSUMER_KEY = 'xxxxxxxxxxx' # fill with correct key
CONSUMER_SECRET = 'xxxxxxxxxx' # fill with correct secret

REDIRECT_CALLBACK_URL  = '%s/login/complete'%BASE_URL
LATEST_TWEET_COUNT = 10


class ThreadedHTTPServer(ThreadingMixIn, BaseHTTPServer.HTTPServer):
	pass

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	
	auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET,REDIRECT_CALLBACK_URL)
	oauth_tokens = {} # key is (s.client_address,oauth_token). value is (access_token,access_secret)

	def authenticate(s):	
		twitter_login_redirect_url = MyHandler.auth.get_authorization_url()

        def do_HEAD(s):
                s.send_response(200)
                s.send_header("Content-type", "text/html")
                s.end_headers()

        def do_GET(s):
                """Respond to a GET request."""
		if s.path.startswith('/login/complete'):
			query = urlparse.urlparse(s.path).query
			param = dict(qc.split("=") for qc in query.split("&") if qc)
			log.debug('Parameters: %s' % param)
			oauth_token = param.get('oauth_token')
			if oauth_token not in MyHandler.oauth_tokens:
			#if 'oauth_verifier' in s.path:
				log.info('Redirected from twitter')
				""" Redirected from twitter """
				try:
					# use the verifier to get the access token and rock 'n' roll	
					verifier = param.get('oauth_verifier')
					log.info('Verifier = %s, OAuth_token = %s' % (verifier,oauth_token))
					print 'Verifier = %s, oauth token = %s' %(verifier,oauth_token)
					print 'Before access_token = %s' % MyHandler.auth.access_token
					MyHandler.auth.get_access_token(verifier)
					print 'After access_toke = %s' % MyHandler.auth.access_token	
					MyHandler.oauth_tokens[oauth_token] = (MyHandler.auth.access_token,MyHandler.auth.access_token_secret)
					#MyHandler.oauth_tokens[s.client_address[0]] = (MyHandler.auth.access_token,MyHandler.auth.access_token_secret)
				except tweepy.TweepError as e:
					print 'Failed while authenticating: %s' % str(e) 
					s.send_response(401)
					s.send_header("Content-type","text/html")
					s.end_headers()
					s.wfile.write("<html><head><title>Authentication Failed</title></head>")
					s.wfile.write("<body><p>Authentication failed due to : %s</p></body></html>" % str(e))
					return


			MyHandler.auth.set_access_token(MyHandler.oauth_tokens[oauth_token][0],MyHandler.oauth_tokens[oauth_token][1])

			api = tweepy.API(MyHandler.auth)
			user = api.me()
			log.info('User "%s" logged in' % user.name)

			#print 'User object : %s' % api.me()

               		s.send_response(200)
               		s.send_header("Content-type", "text/html")
               		s.end_headers()
               		s.wfile.write("<html><head><title>Project Place Task.</title></head>")
			
                	s.wfile.write("<body><p><b>Successfully logged in '%s' using Twitter</b></p><form action='/tweet?oauth_token=%s&' method='POST'><label>Tweet: </label><input name='tweet' type='text' value='Type text to tweet' style='width: 450px;'/><br/><br/><br/><input type='submit' value='Post Tweet'/></form>" % (user.name,MyHandler.auth.request_token['oauth_token']))

			# get the lastest tweets
			s.latest_tweets()

                	s.wfile.write("</body></html>")

		elif s.path in ('/'):
			"""
			The root page
			"""
                	s.send_response(200)
                	s.send_header("Content-type", "text/html")
                	s.end_headers()
                	s.wfile.write("<html><head><title>Project Place Task.</title></head>")
                	s.wfile.write("<body><p><b>Simple page to tweet</b></p><form action='/login' method='POST'><br/><br/><input type='submit' value='Login to Twitter'/></form>")
                	# If someone went to "http://something.somewhere.net/foo/bar/",
                	# then s.path equals "/foo/bar/".
                	#print "GET: accessed path: %s" % s.path
                	log.info("GET: accessed path: %s" % s.path)
                	s.wfile.write("</body></html>")
                	#pprint (vars(s))
			log.debug(vars(s))
		else:
			s.unknown_page()

	def login(s):
		try:
			MyHandler.auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, REDIRECT_CALLBACK_URL)
			twitter_login_redirect_url = MyHandler.auth.get_authorization_url()
			log.debug('Redirection URL for twitter authentication: %s' % twitter_login_redirect_url)
			print 'Redirection URL for twitter authentication: %s' % twitter_login_redirect_url

			s.send_response(301)
			s.send_header('Location', twitter_login_redirect_url)
			s.end_headers()
		except tweepy.TweepError as e:
			print 'Error! Failed to get url to login to Twitter.'
			print e
			log.error('Tweepy Error: %s' % str(e))
			s.send_response(401)
			s.send_header('Content-type','text/html')
			s.wfile.write('<html><head/><body><p>Twitter login failed</p></body></html>')
			s.end_headers()


        def do_POST(s):
                """Respond to a POST request."""
		#print 'POST: Path is: %s'%s.path
		log.info('POST: Path is: %s' % s.path)
               	#pprint (vars(s))
               	log.debug(vars(s))
                #pprint (vars(s.headers))
                log.debug(vars(s.headers))

		if s.path.startswith('/login'):
		#if s.path in ('/login','/login/'):
			# use tweepy to redirect the page for twitter login
			query = urlparse.urlparse(s.path).query
			param = dict(qc.split("=") for qc in query.split("&") if qc)
			oauth_token = param.get('oauth_token')
			# check if the user has already logged in from the client machine
			if oauth_token in MyHandler.oauth_tokens:
				MyHandler.auth.set_access_token(MyHandler.oauth_tokens[oauth_token][0],
								MyHandler.oauth_tokens[oauth_token][1])
				try:
					""" Token from this client still valid """
					api = tweepy.API(MyHandler.auth)
					s.send_response(301)
					s.send_header('Location','/login/complete?oauth_token=%s&' % oauth_token)
					s.end_headers()
				except tweepy.TweepError as e:
					print 'Token expired for client : %s. Logging in again' % MyHandler.oauth_tokens[oauth_token]
					log.error('Token expired for client : %s. Logging in again' % MyHandler.oauth_tokens[oauth_token])
					(key,secret) = MyHandler.oauth_tokens.pop(oauth_token)
					s.login()
			else:
				s.login()

		elif s.path.startswith('/tweet'):
		#elif s.path in ('/tweet'):
			query = urlparse.urlparse(s.path).query
			param = dict(qc.split("=") for qc in query.split("&") if qc)
			oauth_token = param.get('oauth_token')
			print 'oauth_token: %s' % oauth_token
			log.debug('Tweet oauth_token: %s' % oauth_token)
			length = int(s.headers['Content-Length'])

			post_data = urlparse.parse_qs(s.rfile.read(length).decode('utf-8'))
			#print "Parsed tweet : '%s'" % post_data
			log.info("Parsed tweet : '%s'" % post_data)
			tweet = post_data.get('tweet',[''])[0].strip()
			
                	s.send_response(200)
                	s.send_header("Content-type", "text/html")
                	s.end_headers()
                	s.wfile.write("<html><head><title>Project Place Task.</title></head>")
			
                	s.wfile.write("<body><form action='/tweet?oauth_token=%s&' method='POST'><label>Tweet: </label><input name='tweet' type='text' value='Type text to tweet' style='width: 450px;'/><br/><br/><br/><input type='submit' value='Post Tweet'/></form>" % oauth_token)

			# set the status
			if tweet not in ('','Type text to tweet'):
				try:
					api = tweepy.API(MyHandler.auth)
					#print 'Sending tweet: %s' % tweet
					log.info('Sending tweet: %s' % tweet)
					res = api.update_status(status=tweet)
					#print '\nUpdated the status: %s\n' % res.text
					log.info('\nUpdated the status: %s\n' % res.text)
					s.wfile.write('<p>Successfully posted tweet : "%s"</p>' % res.text)
					
					# get the lastest tweets
					s.latest_tweets()

				except tweepy.TweepError as e:
					print 'Error: Failed to update status '
					print e
					log.error('Tweepy Error: %s' % str(e))
					s.wfile.write("<p><b>Failed to tweet: %s</b></p>" % str(e))
			else:
				#print 'Invalid tweet'
				log.error('Invalid tweet')

                	s.wfile.write("</body></html>")
		else:
			s.unknown_page()	
	
	def latest_tweets(s):
		try:
			api = tweepy.API(MyHandler.auth)	
			tweets = api.user_timeline(id=api.me().id,count=LATEST_TWEET_COUNT)
			s.wfile.write('<div><h4>Latest %s Tweets</h4></div>' % LATEST_TWEET_COUNT)
			s.wfile.write('<div>')
			if tweets:
				#print 'Status object attributes: %s' % dir(tweets[0])
				pass
			else:
				#print 'No tweets'
				log.info('No tweets')
				s.wfile.write('No tweets of this user')
			for index,tweet in enumerate(tweets,start=1):
				s.wfile.write('<ul>%s. "%s" - Posted at %s</ul>' %(index,tweet.text,tweet.created_at))
			s.wfile.write('</div>')
					
		except tweepy.TweepError as e:
			print 'Failed to get latest tweets'
			print e
			log.error('Tweepy Error: %s' % str(e))
			s.wfile.write("<p>Failed to get latest tweets: %s</p>" % str(e))

	def unknown_page(s):
		s.send_response(404)
		s.send_header("Content-type", "text/html")
		s.end_headers()
		s.wfile.write("<html><head><title>Project Place Task.</title></head>")
		s.wfile.write("<body><p>Page doesn't exist: %s</p>" % s.path)
		s.wfile.write("</body></html>")

if __name__ == '__main__':
        #server_class = BaseHTTPServer.HTTPServer
        server_class = ThreadedHTTPServer
        httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
        print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
        log.info( "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER))
        try:
                httpd.serve_forever()
        except KeyboardInterrupt:
                pass
	finally:
        	httpd.server_close()
        print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)
        log.info( "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER))

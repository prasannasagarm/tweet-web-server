Simple python web server to post tweets from client
===================================================
Author: Prasanna Maddu
Date: 23-06-2015

Prerequisites for the running
---------------------------
1. Tweepy


Running the Server:
-----------------
1. Install the prerequisites (preferably on virtualenv)
2. Request the author for the Twitter consumer key and consumer secret.
3. Set them in the file main.py for the global variables CONSUMER_KEY, CONSUMER_SECRET
4. Change global variables HOST_NAME, HOST_PORT, BASE_URL etc., according to the target environment
4. cd to the directory where the zip was extracted 
5. sudo python main.py - This will start the http server


Connecting to the server from browser
-------------------------------------
1. Type value in BASE_URL variable along with port (For example, I've hosted the server on AWS with domain name google.com and port 8003, so the complete url would be http://google.com:8003)

2. Login using twitter - this will take the user to the twitter login page

3. On successful login, the client will be redirected to our server and can tweet from there 

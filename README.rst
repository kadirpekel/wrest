wrest
=====

Thin rest client with no dependencies

Usage
-----
Here is a sample usage::

  from wrest import Client
  client = Client('https://api.twitter.com/1')
  tweets = client.get('statuses', 'user_timeline.json', screen_name='ThePSF', count=10)
  for tweet in tweets:
    print(tweet.get('text'))

Licence
-------
http://www.gnu.org/licenses/gpl-3.0.txt

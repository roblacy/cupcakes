"""Code to fetch and organize cupcake data from the twitter API

uses python-twitter package
"""
import dateutil.parser as date_parser
import HTMLParser
import re
import twitter


# twitter api info
CONSUMER_KEY = 'CONSUMER KEY HERE'
CONSUMER_SECRET = 'CONSUMER SECRET HERE'
ACCESS_TOKEN_KEY = 'ACCESS TOKEN KEY HERE'
ACCESS_TOKEN_SECRET = 'ACCESS TOKEN SECRET HERE'

# some config values for fetching & parsing data
MAX_FETCH_AMOUNT = 365
FETCH_SIZE = 200
SCREEN_NAME = 'gtowncupcake'
FLAVOR_REGEX = re.compile('flavor is\s+((\#|\@)\w+\s+)?(?P<flavor>[^!]*)!* Order')
HTML_PARSER = HTMLParser.HTMLParser()


def get_free_flavors(screen_name, max_needed):
    """Returns flavor/date pairs going into the past
    """
    api = twitter.Api(consumer_key=CONSUMER_KEY,
                      consumer_secret=CONSUMER_SECRET,
                      access_token_key=ACCESS_TOKEN_KEY,
                      access_token_secret=ACCESS_TOKEN_SECRET)

    flavors = []

    tweet_data = api.GetUserTimeline(screen_name=screen_name,
                                     include_rts=False,
                                     exclude_replies=True,
                                     count=200)

    while tweet_data and len(flavors) < max_needed:
        for row in tweet_data:
            process_row(row, flavors)
        oldest_id = tweet_data[-1].id - 1
        tweet_data = api.GetUserTimeline(screen_name=screen_name,
                                         include_rts=False,
                                         exclude_replies=True,
                                         count=FETCH_SIZE,
                                         max_id=oldest_id)

    return flavors


def process_row(row, flavors):
    """Parses and adds row data to flavors if this is a free cupcake tweet
    """
    flavor_name = parse_flavor(row.text)
    if flavor_name:
        flavor_name = HTML_PARSER.unescape(flavor_name)
        flavor_name = flavor_name.replace('"', '')
        date = date_parser.parse(row.created_at)
        flavors.append([
            flavor_name,
            date.strftime('%Y/%m/%d'),
            date.strftime('%A'),
            date.strftime('%B'),
        ])


def parse_flavor(tweet_text):
    """Parses flavor name from text of a tweet
    """
    match = FLAVOR_REGEX.search(tweet_text)
    if match:
        return match.group('flavor')


if __name__ == '__main__':
    flavor_data = get_free_flavors(SCREEN_NAME, MAX_FETCH_AMOUNT)
    with open('cupcakes.csv', 'wb') as data_file:
        for row in flavor_data:
            data_file.write('%s\n' % ','.join(row))

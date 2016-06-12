# -*- coding: utf-8 -*-
import tweepy
import PyRSS2Gen
import os
from urlparse import urlparse

from config import *

def recursive_link_extractor(url, n_deep = 5):
    """
    Returns an HTML-formatted string following links in case they are
    references to other tweets (and returns a reference to the last
    tweet in the chain).
    
    Inputs:
    - url: the url to process
    
    Output:
    - text: HTML formatted string.
    """
    
    original_url = url
    ref_tweet = None
    
    origin = urlparse(url).netloc

    while (origin == "www.twitter.com" or origin == "twitter.com") \
          and url and n_deep > 0:
              
        ref_tweet = url
        url = get_single_link(url)        
        if url:
            origin = urlparse(url).netloc
        n_deep = n_deep - 1
        
    # If we found some link, let's format it and return.
    # If there was nothing, or we reached the bottom of the possible
    # depth and didn't find anything, just return the original one in its
    # original form.
    
    if not url or not ref_tweet or n_deep == 0:
        text = '<li><a href="%s">%s</a></li>' % (original_url, original_url)
    else:
        text = '<li><a href="%s">%s</a> (from <a href="%s">%s</a>)</li>' % \
               (url, url, ref_tweet, ref_tweet)
               
    return(text)
    
def get_single_link(tweet_url):
    """
    Gets the first link from the tweet_url passed as argument.
    
    Inputs:
    - tweet_url: a Twitter UrL
    
    Outputs:
    - The first link contained within this status message.
    """
    
    global api
    
    # Get tweet id
    tweet_id = urlparse(tweet_url).path.split("/")[-1]
    
    status = api.get_status(int(tweet_id))
    
    if status.entities['urls']:
        return status.entities['urls'][0]['expanded_url']
    else:
        return None
    
    

def generate_html(screen_name, text, urls, tweet_url, image):
    """
    Generates a very simple HTML output with the text of the tweet
    and the URLs, if present.

    Inputs:
    - screen_name: the screen name of the user tweeting this status
    - text: a string with the text of the tweet.
    - urls: a list containing the URLs linked in the tweet. Can be None.
    - tweet_url: the URL of the original tweet
    - image: the URL for the image linked in the tweet. Can be None.

    Output:
    - text: HTML formatted string.
    """
    text = '<a href="%s">@%s</a>: %s' % (tweet_url, screen_name, text)
    if urls:
        text += "<p>Referenced URLs:</p><ul>"
        for url in urls:
            text += recursive_link_extractor(url)
        text += "</ul>"
    if image:
        text += '<p><a href="%s"><img src="%s" /></a></p>' % (image, image)
    return(text)

def process_tweet_items(list_items):
    """
    Generates a list of dictionaries with selected elements
    from the tweet items.

    Inputs:
    - list_items: a list of statuses.

    Ouputs:
    - res: a list of dictionaries containing selected fields
           and transformations.
    """
    res = []
    for l in list_items:
        urls = [x['expanded_url'] for x in l.entities['urls']] \
               if l.entities['urls'] else None
        image = l.entities['media'][0]['media_url'] \
                if 'media' in l.entities and l.entities['media'] else None
        tweet_url = "https://www.twitter.com/%s/status/%s" % \
                    (l.user.screen_name, l.id_str)
        text_html = generate_html(l.user.screen_name, l.text, urls, 
                                  tweet_url, image)
        d = dict(user = l.user.name,
                 screen_name = l.user.screen_name,
                 created_at = l.created_at,
                 text = l.text,
                 text_html = text_html,
                 urls = urls,
                 image = image,
                 source_url = l.source_url)
        if not only_links or (only_links and urls):
            res.append(d)
    return(res)
    
def tweet_to_rss_item(tweet_data):
    """
    Converts a single tweet to an RSS item.

    Inputs:
    - tweet_data: a dictionary with selected status fields, coming
                  from process_tweet_items().

    Outputs:
    - rss_item: a properly formatted PyRSS2Gen.RSSItem object.
    """
    link = tweet_data['urls'][0] if tweet_data['urls'] else tweet_data['source_url']
    title = "@%s: %s" % (tweet_data['screen_name'], tweet_data['text'])
    rss_item = PyRSS2Gen.RSSItem(title = title,
                                 link = link,
                                 guid = PyRSS2Gen.Guid(link),
                                 pubDate = tweet_data['created_at'],
                                 description = tweet_data['text_html'])
    return(rss_item)

def process_rss(data, path, trigger):
    """
    Processes a list of status messages and writes the corresponding RSS file.

    Inputs:
    - data: a list of dictionaries coming from process_tweet_items().
    - path: the path to save the file to.
    - trigger: the parameters used to obtain the list of tweets. It will
               be either a 2-tuple (for a user / list pair) or a search
               string.

    Outputs:
    Doesn't return anything, just writes the RSS data to file.
    """
    
    if len(trigger) == 2:
        title = "List %s from user %s" % (l[1], l[0])
    else:
        title = "Search %s" % s
        
    last_date = max([x['created_at'] for x in data])
    
    rss = PyRSS2Gen.RSS2(title = title,
                         link = "",
                         lastBuildDate = last_date,
                         description = "",
                         items = map(tweet_to_rss_item, data))
                         
    with open(path, "w") as f:
        rss.write_xml(f)

api = None

if __name__ == "__main__":
    
    # Get the authenticated API
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    
    # Are we using a prefix? Get the lists that match, then    
    if prefix:
        my_user = api.me().screen_name
        mylists = api.me().lists()
        for ml in mylists:
            if ml.name.find(prefix) == 0:
                get_lists.append((my_user, ml.name))
    
    # Process each list in the following way:
    # But first remove any potential duplicate
    get_lists = set(get_lists)
    
    for l in get_lists:
        list_data = tweepy.Cursor(api.list_timeline, l[0], l[1]).items(n_items)
        list_data = process_tweet_items(list_data)
        list_path = os.path.join(output_folder, "%s_%s.xml" % \
                                 (l[0].lower(), l[1].lower()))
        process_rss(list_data, list_path, l)
    
    # Same thing for searches
    for s in get_searches:
        search_data = tweepy.Cursor(api.search, s).items(n_items)
        search_data = process_tweet_items(search_data)
        search_path = os.path.join(output_folder, "search_%s.xml" %\
                                   s.lower().replace(" ", "_"))
        a = process_rss(search_data, search_path, s)
        

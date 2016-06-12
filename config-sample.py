# Create these on https://apps.twitter.com/ and paste them here.
# The application you create does not need to have write permissions
consumer_key = 'x'
consumer_secret = 'x'
access_token = 'x'
access_token_secret = 'x'

# How many items to process per list
n_items = 30

# If we are interested only in tweets that contain links, 
# set this to True (default). Otherwise, it will gather all
# links.
only_links = True

# The folder to write the XML files
output_folder = "."

# A list of lists to obtain, with elements in format (user, listname). If
# you include your own lists, they can be private.
get_lists = [('user1', 'list1'),
             ('user1', 'list2'),
             ('user2', 'list3')]

# We can also obtain lists (from our own user) that use a given prefix
# in their names. If we don't want to use this option, set it to None
prefix = 'rss-'

# A list of searches to include. To disable, set it to None.
get_searches = ["morning briefing from:nytimes"]

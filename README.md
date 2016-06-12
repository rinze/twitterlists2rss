# twitterlists2rss

`twitterlists2rss` is a simple Python script designed to convert Twitter lists and searches to RSS files in a very simple way, so these results can then be fed to RSS readers.

It will obtain the timeline for a given set if lists or searches and will extract the links within each status message. If the status message contains an image, it will include it in the RSS item. If the status message contains a link to other tweets, it will go after those tweets (and the tweets within, up to a certain depth) to find the originating link.

The purpose of this library is to be able to keep up-to-date with people that share interesting links on Twitter without needing to access Twitter itself.

# Installation

Simply download the current code and copy `config-sample.py` to `config.py`. Then proceed to [Twitter's apps admin page](https://apps.twitter.com/), create a set of credentials and include them in the file.

You can then set up a cron to run this script periodically. If you are in a shared hosting environment, you might need to use [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/). I have done so myself on [DreamHost](https://www.dreamhost.com) with no problems.

Once the .xml files have been generated, just use an RSS reader to keep up to date.

## Dependencies

You will need the following extra libraries (you can install them using `pip install --user` or directly `pip install` if you are using a virtualenv.

* [PyRSS2Gen](https://pypi.python.org/pypi/PyRSS2Gen).
* [Tweepy](http://www.tweepy.org/).

# Configuration

All the options are pretty straightforward and are commented in the `config-sample.py` file. Just read the description and drop me a line if you have any doubts. I will improve the comments if people think some more info could be added.

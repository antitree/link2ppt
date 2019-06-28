#!/usr/bin/python
# Title: Link2PPT
# Description: Automatic PPTX generator used by
# Rochester2600 group to build a list of links
# Each month.
# Usage: ./l2ppt links.csv
# CSV format:
# url, date, authors

#from __future__ import absolute_import
#from __future__ import division, print_function, unicode_literals
import argparse 
import logging, sys
#import re
import time, datetime
import unicodedata

import nltk.data
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
#from HTMLParser import HTMLParser  # works in python2
from html.parser import HTMLParser
import random
import os
import calendar
from dateutil.relativedelta import relativedelta

import categorizer

import remark

try:
    import instalink
except:
    print("No Instapaper support")
#import urllib2
from bs4 import BeautifulSoup

from feedly.api_client.session import FeedlySession
from feedly.api_client.stream import StreamOptions
from feedly.api_client.session import FileAuthStore
from pathlib import Path

logging.basicConfig(level="INFO")



OUTPUT = ""
CREDS = "./creds"
LAZYLIST = [
    "slashdot.org",
    ]
TESTMODE = False


def main():
    global OUTPUT
    global TESTMODE
    # Handle arguments
    parser = argparse.ArgumentParser(description="Download instapaper and do cool things with it.")
    parser.add_argument('-i',
        dest='icreds',
        help='File with creds for instapaper')
    parser.add_argument('-f',
        dest='fcreds',
        help="Path to feedly auth creds"
    )
    parser.add_argument('--tag',
        dest='ftag',
        help="Optional feedly board name")
    parser.add_argument('--full',
        help="Download full list from instapaper",
        action="store_true")
    parser.add_argument('-t', 
        dest='testmode',
        help="Enable test mode",
        action="store_true")

    args = parser.parse_args()

    if args.testmode: 
        TESTMODE = True
        logging.basicConfig(level="DEBUG")

    content = []

    if args.ftag: 
        tag = args.ftag
    else:
        tag = "2600"

    if args.icreds:
        if args.full:
            full = True
        else:
            full = False
        creds = open(args.icreds).read().splitlines()
        content = get_instapaper(creds, full)
    elif args.fcreds:
        content = get_feedly(args.fcreds, tag=tag)
    else:
        creds = []
        full = False
        try: 
            creds.append(os.environ['INSTA1'])
            creds.append(os.environ['INSTA2'])
            creds.append(os.environ['INSTA3'])
            creds.append(os.environ['INSTA4'])
        except: 
            logging.error("Missing INSTA[1-4] env vars")
            sys.exit()
        content = get_instapaper(creds, full)

    build_remarks(content, 'build/%s.md' % tag)

def build_remarks(content, path):
    r = remark.Remark()
    # Summarize common categories
    #cats = [x["category"] for x in content]
    #counter = collections.Counter(cats)
    #print(counter.most_common(3))
    for slide in content:
        r.add_slide(slide)
    output = r.build()
    ### Convert from unstripped unicode shit
    #re.sub('<[^<]+?>', '', text)
    #output = unicodedata.normalize('NFKD', output).encode('ascii', 'ignore') ## python2
    #output = output.decode("utf-8", "backslashreplace")
    cleanoutput = teh_security(output)
    f = open(path, 'w')
    try:
        f.writelines(cleanoutput)
    except TypeError:
        print(type(cleanoutput))
        print("Couldn't print this out for some reason")
    f.close()

def desperate_summarizer(content):
    """ Sumy implementation that tries to guess
    what the content means """
    return []
    LANGUAGE = "english"
    SENTENCES_COUNT = 5
    parser = PlaintextParser.from_string(content, Tokenizer(LANGUAGE))
    stemmer = Stemmer(LANGUAGE)

    summarizer = Summarizer(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)

    #highlights = [cs]
    for sentence in summarizer(parser.document, SENTENCES_COUNT):
        highlights.append(sentence._text)
        logging.debug(sentence)

    return highlights


def lazy_summarizer(content):
    """Take the first 8 sentences"""
    #highlights = [re.sub('[\t|\n]','', x[:250].strip(' \t\n\r')) for x in content.split('. ')[:8]]
    try: 
        tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    except LookupError:
        logging.error("Missing Punkt NLTK data. Downloading now...")
        nltk.download('punkt')
        tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    
    highlights = tokenizer.tokenize(content)[:8]
    #print('-'*20)
    #print(content)
    #print('-'*20)
    #print(highlights)
    return highlights

def get_feedly(auth, tag="2600", full=False):
    sopts = StreamOptions()  # 
    os.environ["TZ"] = "US/Eastern"
    time.tzset()
    t = datetime.datetime.today()
    last = t - relativedelta(months=1)  # get last month from now
    sopts.newerThan = int(first_friday_finder(last.year, last.month).timestamp())*1000
    logging.info("Finding stories newer than: %s" % sopts.newerThan)
    logging.info("Current time: %s" % time.time())
    #sopts.newerThan = 1556731092000  ## TODO fix
    auth_path = Path("./auth")
    auth = FileAuthStore(auth_path)
    fsess = FeedlySession(auth)
    board =fsess.user.get_tag(tag)
    content = [x for x in board.stream_contents(sopts)]

    try: 
        c = categorizer.Categorize()
        try_categorize = True
    except:
        logging.error("Google Creds were not found")
        try_categorize = False


    for indx, line in enumerate(content):
        if "content" in line.json.keys():
            htmltext = line["content"]["content"]
        elif "fullContent" in line.json.keys():
            htmltext = line["fullContent"]
        elif "summary" in line.json.keys():
            htmltext = line["summary"]["content"]
        else: 
            logging.error(line.json.keys())
            logging.error("-"*20)
            logging.error(line.json)
            raise KeyError("Content nor fullcontent is in the json")
            break
        text = BeautifulSoup(htmltext, "lxml").get_text()

        if try_categorize:
            # Assign a category from google API
            content[indx]["category"] = [x.name for x in c.classify_text(text[:1000].replace('  ',''))]
            #content[indx]["category"] = ["butts"]
        else: content[indx]["category"] = ["unknown"]
            
        # Summarize the first few lines
        content[indx]["highlights"] = lazy_summarizer(text)

        if "canonicalUrl" in line.json.keys():
            url = line["canonicalUrl"]
        elif "alternate" in line.json.keys():
            url = line["alternate"][0]["href"]
        # Feedly JSON is completely random. Things are in different places
        content[indx]["url"] = url
        content[indx]["time"] = int(line["published"])/1000.0
    return content

def get_instapaper(creds, full=False):
    logging.warning("INSTAPAPER is deprecated and might now work")
    global TESTMODE
    if TESTMODE:
        content = [{
            "highlights": ["FAKE NEWS"],
            "summarizer": "lazy",
            "bookmark_id": "42",
            "text": "Weird butts",
            "title": "SOMEONE FAILED ME",
            "url": "https://www.antitree.com",
            "time": '1513216677',
            "category": ["butts","butts","notbutts"]
            }]
        return content
    ilink = instalink.Instalink(creds)
    ilink.login()
    il = ilink.getlinks()
    links = ilink.handlelinks(il)
    # Only get the last 22 days
    if not full:
        t = datetime.datetime.today()
        last = t - relativedelta(months=-1)  # get last month from now
        ff = first_friday_finder(last.year, last.month)  # find last month's FF
        timesinceff = t - ff  #  The difference between today and last FF
        logging.info("Seconds since last first friday: %s" % timesinceff)
        last_ff_date = time.time() + timesinceff.total_seconds()
        logging.info("Last FF was found to be: %s" % last_ff_date)
        content = list(s for s in links if s["time"] > last_ff_date)
        content = list(s for s in links if s["time"] > time.time() - 2592000) # Fuck it back to 30 days
        logging.info("Found %s articles" % len(content))
    else:
        content = list(s for s in links)

    c = categorizer.Categorize()
    for indx, line in enumerate(content):
        #if not line["highlights"]: ## TODO missing what do do if there are highlights
        if True:
            logging.debug("No highlights found. adding some")
            logging.info("line[bookmarkid]= %s" % line["bookmark_id"])
            htmltext = ilink.gettext(line["bookmark_id"])
            text = BeautifulSoup(htmltext, "lxml").get_text()
            #text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore')
            # this randomly choosing how to summarize. Great
            # yeah i took that out. IT fucked me because I forgot about it. 
            if content[indx]["summarizer"] == "lazy":
               content[indx]["highlights"] = lazy_summarizer(text)
               #content[indx]["highlights"].append("LAZYBOT")
               #print("used the lazy summarizer")
            elif content[indx]["summarizer"] == "special":
               content[indx]["highlights"] = "todo"
            else:
           #content[indx]["highlights"] = desperate_summarizer(text)
               #content[indx]["highlights"] = honest_summarizer(text)
               content[indx]["highlights"] = lazy_summarizer(text)
               #content[indx]["highlights"].append("SUMYBOT9000")
               #print("Used the fail over summarizer")
        content[indx]["category"] = [x.name for x in c.classify_text(text[:1000].replace('  ',''))]
        
    return content

def teh_security(badness):
    #s = Stripper()
    # try: 
    #     s.feed(badness)
    # except:
    #     print("Teh Security Failed!")
    #     print(badness)
    #     sys.exit()
    #goodness = s.get_data()
    #print("Before: \n\n%s" % badness)
    #goodness = Stripper3(badness)
    #print("After: \n\n%s" % goodness)
    goodness = badness  # yup I did that. 

    
    return goodness

def first_friday_finder(year, month):
    #find next first friday
    os.environ["TZ"] = "US/Eastern"
    time.tzset()
    c = calendar.Calendar(firstweekday=calendar.SUNDAY)
    monthcal = c.monthdatescalendar(year, month)
    firstfriday = [day for week in monthcal for day in week if day.weekday() == calendar.FRIDAY and day.month 
== month][0]
    firstfriday = datetime.datetime.combine(firstfriday, datetime.datetime.min.time())
    firstfriday = firstfriday.replace(hour=22,minute=00)
    return firstfriday



# def get_title(url):
#     try:
#         # 3s timeout
#         f = urllib2.urlopen(url, tmeout=3000)
#         soup = BeautifulSoup(f)
#         f.close()

#         if soup.title.string:
#             logging.debug("Title found as: %s" % soup.title.string)
#             return soup.title.string
#         else:
#             return "No title found"
#     except:
#         logging.error("URL: %s had an error" % url)
#         return "Blank"


# def parse_csv(file):
#     # is csv file?
#     #csvobj = []
#     with open(file, 'rb') as csvfile:
#         urllist = csv.reader(csvfile, delimiter=',', quotechar='|')
#         content = []
#         for row in urllist:
#             ## If url TODO
#             record = {}
#             record["url"] = row[0]
#             try:
#                 record["author"] = row[1]
#             except IndexError:
#                 record["author"] = None

#             try:
#                 record["date"] = row[2]
#             except IndexError:
#                 record["date"] = None
#             record["title"] = get_title(row[0])

#             ## add to slide
#             content.append(record)
#             #add_slide(record)
#         return content



class Stripper(HTMLParser):
    '''clASS TO summon thE STRpper for tEH STR1PIN'''
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def Stripper3(badness):
    import string
    printable = set(string.printable)
    filter(lambda x: x in printable, badness)        

if __name__ == '__main__':
    # init main
    main()

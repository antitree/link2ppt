#!/usr/bin/python
# Title: InstaLink
# Description: Collect links and highlights from Instapaper.
# Usage:
#   import instalink
#   ilink = instalink.instalink()
#   ilink.login()
#   ilink.getlinks(daterange)
import argparse
import requests
import logging
import time
from requests_oauthlib import OAuth1

__BASE__ = "https://www.instapaper.com"
__API_VERSION__ = "1.1"
__ENDPOINT__ = __BASE__ + "/api/" + __API_VERSION__ + "/"

#logging.basicConfig(level="DEBUG")

class Instalink:
    def __init__(self, creds):
        self.ckey = creds[0]
        self.csecret = creds[1]
        self.email = creds[2]
        self.password = creds[3]
        self.osecret = None
        self.otoken = None
        #logging.basicConfig(level=logging.DEBUG)

    def _xauth(self):
        # try to authenticate with instapaper
        logging.debug("xauth")
        header = {'x_auth_username': self.email, 'x_auth_password': self.password} ##TODO do I need the xauth client type here?
        return header

    def _oauth(self):
        # If we don't have a token pair then just create the request
        if not self.osecret and not self.otoken:
            oauth = OAuth1(self.ckey, self.csecret)
        elif self.osecret and self.otoken:
            oauth = OAuth1(self.ckey, self.csecret, self.otoken, self.osecret)
        else:
            raise(Exception)
        return oauth

    def login(self):
        data = self._xauth() # Get the body of the request
        auth = self._oauth() # get the authorization header
        r = self._request(
            "https://www.instapaper.com/api/1.1/oauth/access_token",
            data=data,
            auth=auth
            )
        ## TODO add status code check
        resp = str(r.text)
        oauth_tokens = resp.split("&")
        self.osecret = oauth_tokens[0].split("=")[1]
        self.otoken = oauth_tokens[1].split("=")[1]


    def getlinks(self, folder="archive"):
        '''Returns a list of links from the
        from the instapaper archive'''
        url = __ENDPOINT__ + "bookmarks/list"
        data = {
            "limit": 500, ## TODO 
            "folder_id": folder
        }
        r= self._request(url, data=data, auth=self._oauth())
        logging.debug(r.text)

        return(r.json())

    def gettext(self, bookmark_id):
        url = __ENDPOINT__ + "bookmarks/get_text"
        data = {
            "bookmark_id": bookmark_id
        }
        r = self._request(url, data=data, auth=self._oauth())
        text = self._clean(r.text)
        return(text)

    def _clean(self, text):
        # replace ^M's
        text = ' '.join(text.split(r'\r'))
        # remove big spaces
        text = ' '.join(text.split())
        return text


    def handlelinks(self, r):
        ''' take in the json response a reduce it
        down to only the necessary text'''
        l_tor = [
            " tor ",
            " tor project",
            " tbb ",
            "anonymity",
            "anonymous",
            "silk road",
            "deep web",
            "onion",
            ]
        l_mobile = [
            "android",
            " ios ",
            "windows phone",
            "blackberry",
            "mobile",
            "samsung",
            "motorola",
            " sms ",
            " sim card",
            " 4g ",
            " 5g ",
            " 6g ",
            " 3g ",
            " phone",
            "SS7",
            "smartphone",
            "cyanogenmod"
            ]
        l_privacy = []
        l_politics = []
        l_netsec = []
        l_dark = [
            "coin ",
            "silk road",
        ]
        l_infosec = [
            "owasp ",
            "vulnerability",
            "infosec",
            "information security",
            "cyber ",
            "breach",
            "exploit",
            "xss ",
            " overflow ",
            " buffer ",
            " audit",
        ]

        links = []
        for b in r["bookmarks"]:
            logging.debug("Found new bookmark")
            link = {}
            link["bookmark_id"] = b["bookmark_id"]
            link["title"] = b["title"]
            link["url"] = b["url"]
            link["starred"] = b["starred"]
            # time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(1347517370))
            link["time"] = b["time"]
            # Get the highlights text if there is any
            highlights = list(
                h["text"] for h in r["highlights"] if h["bookmark_id"] == b["bookmark_id"]
                )
            link["highlights"] = highlights
            ## Choose a summarizer that best fits the content
            ## ie slashdot can use lazy
            import tldextract
            link["domain"] = tldextract.extract(link["url"])
            summarize_lazy = [
            "slashdot.org",
            ]
            summarize_special = []
            if link["domain"] in summarize_lazy:
                link["summarizer"] = "lazy"
            elif link["domain"] in summarize_special:
                link["summarizer"] = "special"
            else:
                link["summarizer"] = "default"
            ## Categorize content
            ## TODO search through highlights too
            fuckit = True  # screw this. It just confuses everyone
            if not fuckit:
                if any(x in link["title"].lower() for x in l_tor):
                    link["category"] = "Tor"
                elif any(x in link["title"].lower() for x in l_mobile):
                    link["category"] = "Mobile"
                elif any(x in link["title"].lower() for x in l_infosec):
                    link["category"] = "Infosec"
                elif any(x in link["title"].lower() for x in l_dark):
                    link["category"] = "Dark"
                else:
                    link["category"] = "Unknown"
            else:
                    link["category"] = "FuckItMode_Enabled"
            logging.debug(link)
            links.append(link)

        links.sort(key=lambda x:x["category"])
        return(links)

    def _request(self, url, data, auth):
        r = requests.post(url, data=data, auth=auth) ##TODO clean up
        return r

    def getfolders(self):
        folderurl = __BASE__ + "/api/" + __API_VERSION__ + "/folders/list"
        ## TODO


def main():
    parser = argparse.ArgumentParser(
        description='Instapaper link grabber')
    parser.add_argument('-f',
        dest='creds',
        help="File with consumer key, consumer secret, email, and password in that order on separate lines")

    args = parser.parse_args()

    creds = open(args.creds,'r').read().splitlines()

    ipaper = Instalink(creds)
    ipaper.login()
    ipaper.getlinks()

# init main
if __name__ == '__main__':
    main()

# antitree
# module to get a random related giphy image

import requests, json


class giphy():

    def __init__(self):
        self.GIPHYBASE = 'https://api.giphy.com/v1/gifs/search?q=%s&api_key=%s'
        self.GIPHYAPI = 'dc6zaTOxFJmzC'
        self.GYFCATBASE = 'https://api.gyfcat.com/v1/oauth/token'
        self.GYFCATCID = '2_WX20zG'
        self.GYFCATSECRET = 'DCTNUduwG0CSB0VBqJ--udKcYGPxQU_52lcM05D4VDGtvnyJqK54ZE98XwHuQR3s'
        self.GYFCATTOKEN = ""
        self.MODE = "whatever"

    def get_image(self, terms):
        if not self.MODE == "gyfcat":
            return self.get_more_image(terms)

        search = '+'.join(terms)
        image = ""
        url = self.GIPHYBASE % (search, self.GIPHYAPI)
        try:
            r = requests.get(url)
            images = r.json()
            image = str(images["data"][0]["images"]["original"]["url"])
        except Exception as e:
            print("Failed to get image, switching to gyfcat %s:" % e)
            self.MODE = gyfcat 
            image = self.get_more_images(terms)

        return image
    
    def get_more_image(self, terms):
        if self.GYFCATTOKEN == "":
            self._gyfcat_reauth_()
        searchurl = 'https://api.gfycat.com/v1/gfycats/search?search_text={}'.format(terms)
        auth_header = {"Bearer": self.GYFCATTOKEN}
        r = requests.get(searchurl, headers=auth_header)
        response = json.loads(r.text)
        
        image = response["gfycats"][0]["max2mbGif"]
        return image
        #print("ok I'm ready ", self.GYFCATTOKEN)
        #authheader = 
        #curl -v -X POST https://api.gfycat.com/v1/oauth/token
        #-d '{"code":"{code}", "client_id":"{clientId}", "client_secret": "{clientSecret}", "grant_type": "authorization_code","redirect_uri":"{redirectUri}"}'

    def _gyfcat_reauth_(self):
         url = 'https://api.gfycat.com/v1/oauth/token'
         body = {
            "grant_type":"client_credentials",
            "client_id":"{}".format(self.GYFCATCID),
            "client_secret":"{}".format(self.GYFCATSECRET),
        }
         r = requests.post(url,data=json.dumps(body))
         response = json.loads(r.text)
         self.GYFCATTOKEN = response["access_token"]


if __name__ == '__main__':
  print("Classy...looking for balls")
  a = giphy()
  b = a.get_image(["balls","donkey","and","yup","ok"])
  print(b)
  print('Im done?')
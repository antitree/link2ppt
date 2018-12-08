#!/usr/bin/python
# Title: Remark.py
# Description: Class to convert to remarkjs presentations


### TODO Change this
## planned on implementing: sourceUrl: 'markdown.md'

import time
import rimage
import collections

class Remark:
    def __init__(self, template=None):
        ## Create new remark instance
        self.slides = []
        self.md = []

    def build_slides(self):
        """ Receive a dict containing title, highlights(list), and url
        slide["title"], slide["url"], slide["higlights"] """
        md = ""
        for slide in reversed(self.slides):
            content = []
            #content.append("class: center, middle") ##TODO change to dynamic
            lurl = self.inject_giphy(slide["title"])
            #if lurl:
            #    bg_base = 'background-image: url(%s)'
            #    content.append(bg_base % lurl)
            #    content.append('background-position: bottom;')
            #    content.append('background-repeat: no-repeat;')
            #    content.append('background-size: contain;')
            content.append("## " + slide["title"])
            if lurl:
                  content.append('![lurl](%s)' % lurl)
                  #content.append("---")

            #highlights = []
            for h in slide["highlights"]:
                ## TODO If the title starts with a quote this also applies. SHouldn't.
                if h.startswith('"'):
                    content.append("> " + h)
                else:
                    content.append("- " + h)
            content.append("[" + slide["url"] + "](" + slide["url"] + ")")
            content.append(
                ".footnote[%s - %s]" % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(slide["time"]))), slide["category"]))

            content.append("---")

            for line in content:
              md += line + "\n\n"
        return md

    def inject_giphy(self, search):
        if True:
            # Get the first 2 words in the title
            search = search.split()[:2]
            giphy = rimage.giphy()
            url = giphy.get_image(search)
            return url
        else:
            return False

    def add_slide(self, slide):
        self.slides.append(slide)

    def _test_slide(self):
        slide = {}
        slide["title"] = "Test title"
        slide["url"] = "http://www.google.com"
        highlights = [
            "Highlight item #1",
            "this is a long highlight about something or other. It's not very interesting",
            "Something else"
        ]
        slide["highlights"] = highlights
        return slide

    def summarize_categories(self):
        '''Return a count of the most common categories'''
        categories = []
        for slide in self.slides:
            categories += slide["category"]
        #categories = [x for x in categories]
        #print(categories)
        counter = collections.Counter(categories)
        return counter.most_common(5)

    def add_agenda(self):
        category_chart = self.summarize_categories()
        slide = {}
        slide["title"] = "Agenda"
        titles = []
        #for s in self.slides:
        #    titles.append(s["title"])
        for cat in category_chart:
            titles.append("%s: %s" % (cat[0], cat[1]))
        slide["highlights"] = titles
        slide["url"] = ""
        slide["time"] = time.time()
        slide["category"] = "Agenda"
        self.add_slide(slide)

    def build(self):
        """ Returns just the MD of the slides"""
        self.add_agenda()
        md = self.build_slides()
        return md

if __name__ == '__main__':
    print("No, it's the other one")

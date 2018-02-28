from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
import six
import logging

class Categorize:
    def __init__(self):
        """Classifies content categories of the provided text."""
        self.client = language.LanguageServiceClient()

    def classify_text(self, text):
        if isinstance(text, six.binary_type):
            text = text.decode('utf-8')

            if len(text) < 100:
                return self._empty()

        document = types.Document(
            content=text.encode('utf-8'),
            type=enums.Document.Type.PLAIN_TEXT)

        try: 
            categories = self.client.classify_text(document).categories
        except:
            categories = self._empty("ERROR")
            logging.info("ERROR caused by: %s" % document)

        if len(categories) == 0:
            categories = self._empty("NONE FOUND")

            logging.info(u'=' * 20)
            logging.info(text)


        for category in categories:
            logging.info(u'=' * 20)
            logging.info(u'{:<16}: {}'.format('name', category.name))
            logging.info(u'{:<16}: {}'.format('confidence', category.confidence))
        
        return categories

    def _empty(self, reason="WHATEVER"):
        e = empty()
        e.name = reason
        e.confidence = "0.01"
        return [e]

class Empty:
    def __init__(self):
        self.name, self.confidence = "", ""

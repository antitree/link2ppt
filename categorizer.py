from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
import six
import logging

class Categorize:
	def __init__(self):
		print("Yep")
		self.content = content


	def classify_text(self, text):
	    """Classifies content categories of the provided text."""
	    text = self.content
	    client = language.LanguageServiceClient()

	    if isinstance(text, six.binary_type):
	        text = text.decode('utf-8')

	    document = types.Document(
	        content=text.encode('utf-8'),
	        type=enums.Document.Type.PLAIN_TEXT)

	    categories = client.classify_text(document).categories

	    for category in categories:
	        logging.info(u'=' * 20)
	        logging.info(u'{:<16}: {}'.format('name', category.name))
	        logging.info(u'{:<16}: {}'.format('confidence', category.confidence))
	    return categories

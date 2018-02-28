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

	    document = types.Document(
	        content=text.encode('utf-8'),
	        type=enums.Document.Type.PLAIN_TEXT)

	    categories = self.client.classify_text(document).categories
	    if len(categories) == 0:
	    	return ["GOOGLE FAILED"]
	    	logging.info(u'=' * 20)
	    	logging.info(text)


	    for category in categories:
	        logging.info(u'=' * 20)
	        logging.info(u'{:<16}: {}'.format('name', category.name))
	        logging.info(u'{:<16}: {}'.format('confidence', category.confidence))
	    
	    return categories

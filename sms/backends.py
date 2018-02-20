import os
import urllib
import logging
import requests
from urllib.parse import urlparse
from abc import abstractmethod
from datetime import timedelta, datetime
from collections import defaultdict

from django.conf import settings

from suds.client import Client

from sms.models import Message
from sms import i18n

from kavenegar import *


class BaseBackend(object):
	def enqueue_messages(self, recipients, text, job, description, force=False):
		recipients = map(normalize_number, recipients)
		backend = self.get_backend()
		messages = []
		for recipient in recipients:
			message = Message(text=text, to=recipient, state='P',
							  job_type=job, backend=backend,
							  description=description)
			messages.append(message)
		try:
			if force:
				self.send_messages(messages)
		finally:
			for message in messages:
				message.save()

	def retry_sending_messages(self):
		backend = self.get_backend()
		one_hour_ago = datetime.now() - timedelta(hours=1)
		pending_messages = Message.objects.filter(backend=backend, state='P',
												  created__gt=one_hour_ago)
		try:
			self.send_messages(pending_messages)
		finally:
			for message in pending_messages:
				message.save()

	@abstractmethod
	def get_backend(self):
		pass

	@abstractmethod
	def send_messages(self, messages):
		pass


class ConsoleBackend(BaseBackend):
	def get_backend(self):
		return 'Console'

	def send_messages(self, messages):
		for message in messages:
			print('SMS Sent to: {} (job: {}):\n {}'.format(message.to, message.job_type,
														   message.text))
			# TODO
			#     logging.info('SMS Sent to: %(to)s (job: %(job_type)s):\n%(text)s' % vars(message))
		#     message.state = 'D'



class KavenegarBackend(BaseBackend):
	BACKEND_URL = 'http://ws3584.isms.ir/'
	MAX_RECIPIENT = 100
	POSSIBLE_ERRORS = {
		  0: 'The Http method must be POST',
		  1: 'The moblies parameter must be array',
		  2: 'the mobiles parameter must be less than 1000 or equal 1000',
		  3: 'Username or Password is invalid',
		  4: 'The Web service is not activated',
		  5: 'The ip is forbidden',
		  6: 'The total account is not enough',
		  7: 'You called service operation without enough delay',
		  11: 'Sender is not valid',
		  12: 'Number is not valid',
		  13: 'Default number is not set',
		  14: 'This number is not activate'}

	# def send_messages(self, messages):
	# 	for cluster in messages:
	# 		self.send_chunk(cluster)


	# def send_chunk(self, chunk):

	# 	api = KavenegarAPI('6951385871546338356E7A45742B38744A397A6561343666354D2B4A4F5A6871')
	# 	text = chunk
	# 	numbers = [message.to for message in chunk]
	# 	params = {
	# 	'sender': '100065995',
	# 	'receptor': numbers,
	# 	'message' : text
	# 	}
	# 	response = api.sms_send(params)




		# numbers = [message.to for message in chunk]
		# url = self.BACKEND_URL + 'sendWS'
		# try:
		# 	data = {
		# 	  'username':settings.SMS_USERNAME,
		# 	  'password':settings.SMS_PASSWORD,
		# 	  'mobiles[]': numbers,
		# 	  'body':text,
		# 	  'sender':settings.SMS_NUMBER}
		# 	res = requests.post(url,data)
		# 	result = res.json()
		# except Exception as e:
		# 	raise Exception('Error sending SMS: %s' % e)
		# ids = result['ids']
		# for message, id in zip(chunk, ids):
		# 	message.state = 'S'
		# 	message.reference_code = id



	def check_delivery_state(self):
		 three_days_ago = datetime.now() - timedelta(hours=72)
		 non_delivered_messages = Message.objects.filter(backend=self.get_backend(), state='S',
														 created__gt=three_days_ago)
		 reference_codes = non_delivered_messages.values_list('reference_code', flat=True)
		 reference_code_chunks = [reference_codes[x:x + self.MAX_RECIPIENT] for x in
								  range(0, len(reference_codes), self.MAX_RECIPIENT)]
		 url = self.BACKEND_URL + 'reportWS'
		 for reference_code_chunk in reference_code_chunks:
			 data = {'username':settings.SMS_USERNAME,'password':settings.SMS_PASSWORD,'ids[]':map(int, reference_code_chunk)}
			 result = requests.post(url,data)
	
	@staticmethod
	def find_similar_messages(messages):
		text_map = defaultdict(list)
		for message in messages:
			text_map[message.text].append(message)
		return text_map.values()
 
	def get_send_balance(self):
		url = self.BACKEND_URL + 'creditWS'
		data = {username:settings.SMS_USERNAME, password:settings.SMS_PASSWORD}
		result = requests.post(url, data)
 
	def get_backend(self):
		return 'Kavenegar'




class AFEBackend(BaseBackend):
	# BACKEND_URL = 'http://www.afe.ir/WebService/V7/BoxService.asmx?wsdl'
	BACKEND_URL = 'http://www.afe.ir/WebService/V4/BoxService.asmx'
	MAX_RECIPIENT = 89
	TIMEOUT = 15
	POSSIBLE_ERRORS = (
		'username or password wrong',
		'username or password is null',
		'wrong number',
		'virtual number is empty',
		'mobile array is empty',
		'mobile array is null',
		'more than 89 mobile numbers',
		'no credit',
		'user not enable',
		'message is too long',
		'checkingmessageid array is not correct format'
	)

	def __init__(self):
		self._client = None

	def get_backend(self):
		return 'AFE'

	def send_messages(self, messages):
		clusters = self.find_similar_messages(messages)
		for cluster in clusters:
			self.send_cluster(cluster)

	def send_cluster(self, cluster):
		chunks = [cluster[x:x + self.MAX_RECIPIENT] for x in range(0, len(cluster), self.MAX_RECIPIENT)]
		for chunk in chunks:
			self.send_chunk(chunk)

	def send_chunk(self, chunk):
		client = self.__get_soap_client__()
		text = chunk[0].text
		numbers = [message.to for message in chunk]

		try:
			result = client.service.SendMessage(Username=settings.SMS_USERNAME,
												Password=settings.SMS_PASSWORD,
												Number=settings.SMS_NUMBER,
												Mobile=self.__string_array__(numbers),
												Message=text,
												Type=1,
												CheckingMessageID=self.__long_array__(range(len(chunk))), )
		except Exception as e:
			raise Exception('Error sending SMS: %s', e)

		result_array = result.string
		if len(result_array) == 1 and result_array[0].lower in self.POSSIBLE_ERRORS:
			raise Exception('Error sending SMS: %s' % result_array[0])

		if len(result_array) != len(chunk):
			raise Exception('Error sending SMS: size of result array not matched size of target numbers (%s): %s'
							% (len(chunk), result_array))

		for message, result_item in zip(chunk, result_array):
			if is_numeric(result_item):
				message.state = 'S'
				message.reference_code = result_item
			else:
				message.state = 'F'
				message.error = result_item

	@staticmethod
	def find_similar_messages(messages):
		text_map = defaultdict(list)
		for message in messages:
			text_map[message.text].append(message)
		return text_map.values()

	def __get_soap_client__(self):
		if self._client is None:
			self._client = Client(self.BACKEND_URL, timeout=self.TIMEOUT)
		return self._client

	def __string_array__(self, strings):
		client = self.__get_soap_client__()
		array_of_string = client.factory.create('ArrayOfString')
		array_of_string.string = strings
		return array_of_string

	def __long_array__(self, longs):
		client = self.__get_soap_client__()
		array_of_long = client.factory.create('ArrayOfLong')
		array_of_long.long = longs
		return array_of_long

	def check_delivery_state(self):
		three_days_ago = datetime.now() - timedelta(hours=72)
		non_delivered_messages = Message.objects.filter(backend=self.get_backend(), state='S',
														created__gt=three_days_ago)
		reference_codes = non_delivered_messages.values_list('reference_code', flat=True)
		client = self.__get_soap_client__()
		reference_code_chunks = [reference_codes[x:x + self.MAX_RECIPIENT] for x in
								 range(0, len(reference_codes), self.MAX_RECIPIENT)]
		for reference_code_chunk in reference_code_chunks:
			result = client.service.GetMessagesStatus(Username=settings.SMS_USERNAME,
													  Password=settings.SMS_PASSWORD,
													  SmsID=self.__string_array__(reference_code_chunk))
			result_array = result.string
			for reference_code, result_item in zip(reference_code_chunk, result_array):
				message = Message.objects.get(reference_code=reference_code)
				if result_item == 'SentToMobile':
					message.state = 'D'
				else:
					message.error = result_item
				message.save()


class ISMSBackend(BaseBackend):
	BACKEND_URL = 'http://ws3584.isms.ir/'
	MAX_RECIPIENT = 100
	POSSIBLE_ERRORS = {
		  0: 'The Http method must be POST',
		  1: 'The moblies parameter must be array',
		  2: 'the mobiles parameter must be less than 1000 or equal 1000',
		  3: 'Username or Password is invalid',
		  4: 'The Web service is not activated',
		  5: 'The ip is forbidden',
		  6: 'The total account is not enough',
		  7: 'You called service operation without enough delay',
		  11: 'Sender is not valid',
		  12: 'Number is not valid',
		  13: 'Default number is not set',
		  14: 'This number is not activate'}

	def send_messages(self, messages):
		clusters = self.find_similar_messages(messages)
		for cluster in clusters:
			self.send_cluster(cluster)

	def send_cluster(self, cluster):
		chunks = [cluster[x:x + self.MAX_RECIPIENT] for x in range(0, len(cluster), self.MAX_RECIPIENT)]
		for chunk in chunks:
			self.send_chunk(chunk)

	def send_chunk(self, chunk):
		text = chunk[0].text
		text = text.replace(u'\u200c', ' ')
		numbers = [message.to for message in chunk]
		url = self.BACKEND_URL + 'sendWS'
		try:
			data = {
			  'username':settings.SMS_USERNAME,
			  'password':settings.SMS_PASSWORD,
			  'mobiles[]': numbers,
			  'body':text,
			  'sender':settings.SMS_NUMBER}
			res = requests.post(url,data)
			result = res.json()
		except Exception as e:
			raise Exception('Error sending SMS: %s' % e)
		ids = result['ids']
		for message, id in zip(chunk, ids):
			message.state = 'S'
			message.reference_code = id

	def check_delivery_state(self):
		 three_days_ago = datetime.now() - timedelta(hours=72)
		 non_delivered_messages = Message.objects.filter(backend=self.get_backend(), state='S',
														 created__gt=three_days_ago)
		 reference_codes = non_delivered_messages.values_list('reference_code', flat=True)
		 reference_code_chunks = [reference_codes[x:x + self.MAX_RECIPIENT] for x in
								  range(0, len(reference_codes), self.MAX_RECIPIENT)]
		 url = self.BACKEND_URL + 'reportWS'
		 for reference_code_chunk in reference_code_chunks:
			 data = {'username':settings.SMS_USERNAME,'password':settings.SMS_PASSWORD,'ids[]':map(int, reference_code_chunk)}
			 result = requests.post(url,data)
	
	@staticmethod
	def find_similar_messages(messages):
		text_map = defaultdict(list)
		for message in messages:
			text_map[message.text].append(message)
		return text_map.values()
 
	def get_send_balance(self):
		url = self.BACKEND_URL + 'creditWS'
		data = {username:settings.SMS_USERNAME, password:settings.SMS_PASSWORD}
		result = requests.post(url, data)
 
	def get_backend(self):
		return 'ISMS'


class ADPBackend(BaseBackend):
	BACKEND_URL = 'https://ws.adpdigital.com/services/MessagingService?wsdl'
	MAX_RECIPIENT = 89
	TIMEOUT = 15
	POSSIBLE_ERRORS = {
		1: 'Invalid Username',
		2: 'Invalid Password',
		3: 'Invalid Short Number',
		4: 'Invalid Port Number',
		5: 'Not Enough Credit',
		6: 'Unsupported Message Type',
		7: 'Illegal Parameters',
		8: 'Too Many Messages',
		9: 'No Default Number',
		10: 'Disabled Account',
		11: 'Too Long Message Content',
		15: 'Too Many Requests',
	}

	def __init__(self):
		self._client = None

	def send_messages(self, messages):
		clusters = self.find_similar_messages(messages)
		for cluster in clusters:
			self.send_cluster(cluster)

	def send_cluster(self, cluster):
		chunks = [cluster[x:x + self.MAX_RECIPIENT] for x in range(0, len(cluster), self.MAX_RECIPIENT)]
		for chunk in chunks:
			self.send_chunk(chunk)

	def send_chunk(self, chunk):
		client = self.__get_soap_client__()
		text = chunk[0].text
		text = text.replace(u'\u200c', ' ')
		numbers = [message.to for message in chunk]

		try:
			result = client.service.send(userName=settings.SMS_USERNAME,
										 password=settings.SMS_PASSWORD,
										 shortNumber=settings.SMS_NUMBER,
										 destNo=numbers,
										 clientId=numbers,
										 messageType=1,
										 encoding=2,
										 longSupported=True,
										 dueTime=datetime.now(),
										 content=text
										 )

		except Exception as e:
			raise Exception('Error sending SMS: %s' % e)

		status = result.status
		if status != 0:
			error = self.POSSIBLE_ERRORS.get(status, 'Unrecognized Error')
			raise Exception('Error sending SMS: %s' % error)

		ids = result.id.id
		for message, id in zip(chunk, ids):
			if id == 0:
				message.state = 'F'
				message.error = ''
			else:
				message.state = 'S'
				message.reference_code = id

	def check_delivery_state(self):
		three_days_ago = datetime.now() - timedelta(hours=72)
		non_delivered_messages = Message.objects.filter(backend=self.get_backend(), state='S',
														created__gt=three_days_ago)
		reference_codes = non_delivered_messages.values_list('reference_code', flat=True)
		client = self.__get_soap_client__()
		reference_code_chunks = [reference_codes[x:x + self.MAX_RECIPIENT] for x in
								 range(0, len(reference_codes), self.MAX_RECIPIENT)]
		for reference_code_chunk in reference_code_chunks:
			result = client.service.statusReport(userName=settings.SMS_USERNAME,
												 password=settings.SMS_PASSWORD,
												 type='id',
												 ids=map(int, reference_code_chunk))
			# result_array = result.string
			# for reference_code, result_item in zip(reference_code_chunk, result_array):
			#     message = Message.objects.get(reference_code=reference_code)
			#     if result_item == 'SentToMobile':
			#         message.state = 'D'
			#     else:
			#         message.error = result_item
			#     message.save()

	@staticmethod
	def find_similar_messages(messages):
		text_map = defaultdict(list)
		for message in messages:
			text_map[message.text].append(message)
		return text_map.values()

	def get_send_balance(self):
		client = self.__get_soap_client__()
		return client.service.getBalance(settings.SMS_USERNAME, settings.SMS_PASSWORD, 2)

	def get_backend(self):
		return 'ADP'

	def __get_soap_client__(self):
		if self._client is None:
			self._client = Client(self.BACKEND_URL, timeout=self.TIMEOUT)
		return self._client


class SmartBackend(BaseBackend):
	BACKEND_URL = 'http://212.16.76.90/ws/sms.asmx?wsdl'
	TIMEOUT = 15

	def __init__(self):
		self._client = None

	def __get_soap_client__(self):
		if self._client is None:
			self._client = Client(self.BACKEND_URL, timeout=self.TIMEOUT)
		return self._client

	def get_backend(self):
		return 'SmartSMS'

	def send_messages(self, messages):
		for message in messages:
			self.send_message(message)

	def send_message(self, message):
		client = self.__get_soap_client__()
		try:
			xml_root = self._create_send_sms_request(message)
			xml_data = etree.tostring(xml_root, pretty_print=True)
			result = client.service.XmsRequest(xml_data)
		except Exception as e:
			raise Exception('Error in sending SMS: %s' % e)

		xms_response = etree.fromstring(result)
		try:
			recipient_element = xms_response.find('body').find('recipient')
			if recipient_element.attrib['status'].startswith('69'):
				message.state = 'F'
				message.error = recipient_element.attrib['status']
			else:
				message.state = 'S'
				message.reference_code = recipient_element.text
		except Exception as e:
			raise Exception('Error in sending SMS: %s' % e)

	@staticmethod
	def _create_xms_request(action_name, body_element):
		root = etree.Element('xmsrequest')
		userid_element = etree.Element('userid')
		userid_element.text = settings.SMS_USERNAME
		password_element = etree.Element('password')
		password_element.text = settings.SMS_PASSWORD
		action_element = etree.Element('action')
		action_element.text = action_name

		root.append(userid_element)
		root.append(password_element)
		root.append(action_element)
		root.append(body_element)

		return root

	@staticmethod
	def _create_send_sms_request(message):
		body = etree.Element('body')
		type_element = etree.Element('type')
		type_element.text = 'oto'
		recipient_element = etree.Element('recipient')
		recipient_element.attrib['mobile'] = SmartBackend._normalize_number(message.to)
		recipient_element.text = message.text

		body.append(type_element)
		body.append(recipient_element)
		root = SmartBackend._create_xms_request('smssend', body)

		return root

	@staticmethod
	def _normalize_number(number):
		return ''.join(['0', number[2:]])


def path2url(path):
	return urlparse.urljoin('file:', urllib.pathname2url(os.path.abspath(path)))


def is_numeric(string):
	try:
		float(string)
		return True
	except:
		return False


def normalize_number(number):
	number = number.strip()
	number = i18n.convert_iranian_digits_to_latin(number)
	if number.startswith('0'):
		number = '98%s' % number[1:]
	elif number.startswith('+'):
		number = number[1:]
	return number


def normalize_number_for_client(number):
	if number.startswith('98'):
		return '0' + number[2:]
	return number

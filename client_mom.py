import pika
import uuid
import signal
import sys

# url = 'amqp://vxlrqipo:JBV3wgIMB0ZkNADD5YIQ3I6F6RJ3F4Tp@cougar.rmq.cloudamqp.com/vxlrqipo'
class CheckGrammarClient(object):
	"""docstring for CheckGrammarClient"""
	def __init__(self, url='amqp://vxlrqipo:JBV3wgIMB0ZkNADD5YIQ3I6F6RJ3F4Tp@cougar.rmq.cloudamqp.com/vxlrqipo'):
		params = pika.URLParameters(url)
		self.connection = pika.BlockingConnection(params)
		self.channel = self.connection.channel()

		result = self.channel.queue_declare(queue='', exclusive=True)
		self.callback_queue = result.method.queue
		
		self.channel.basic_consume(
			queue=self.callback_queue,
			on_message_callback=self.on_response,
			auto_ack=True)

	def on_response(self, ch, method, props, body):
		if self.corr_id == props.correlation_id:
			self.response = body

	def call(self, sentence):
		self.response = None
		self.corr_id = str(uuid.uuid4())
		self.channel.basic_publish(
			exchange='',
			routing_key='mom-soa-queue',
			properties=pika.BasicProperties(
					reply_to=self.callback_queue,
					correlation_id=self.corr_id
				),
			body=sentence)
		while self.response is None:
			self.connection.process_data_events()
		return self.response

def processing_sentence(checker_client, sentence):
	print(f'--------------------\n[x] Processing: {sentence}')
	response = checker_client.call(sentence)
	response = response.decode()
	print(f'Got it, result: {response}')

def exit_signal(signal, frame):
	print('\n[x] Quiting, everything is clean up')
	sys.exit(0)

def main():
	checker_client = CheckGrammarClient()

	# Showing test
	sentences = ['There is some birds on the tree', 
				'I should been at home today', 
				'Thank you i does not have any issue']
	print('[Note] This is test:')
	for sentence in sentences:
		processing_sentence(checker_client, sentence)
	
	# Input from keyboard
	print('--------------------\nNow you can type some thing to checkgrammar'\
		', press Ctr+c then Press Enter to exit')
	while True:
		try:
			sentence = input('Type here: ')
			processing_sentence(checker_client, sentence)
		except KeyboardInterrupt:
			print('\n[x] Quiting, everything is clean up')
			sys.exit(0)

if __name__ == '__main__':
	# signal.signal(signal.SIGINT, exit_signal)
	main()
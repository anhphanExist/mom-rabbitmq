import pika
import sys
import signal

class CheckGrammarServer(object):
	"""docstring for CheckGrammarServer"""
	def __init__(self,url ='amqp://vxlrqipo:JBV3wgIMB0ZkNADD5YIQ3I6F6RJ3F4Tp@cougar.rmq.cloudamqp.com/vxlrqipo'):
		params = pika.URLParameters(url)
		self.connection = pika.BlockingConnection(params)
		self.channel = self.connection.channel()
		self.channel.queue_declare(queue='mom-soa-queue')

		self.start_ch()


	def start_ch(self):
		self.channel.basic_qos(prefetch_count=1)
		self.channel.basic_consume(queue='mom-soa-queue', on_message_callback=self.on_request)

		print('Queue established, awaiting grammar check requests')
		self.channel.start_consuming()
	
	def check_grammar(self, word):
		word = f'{word} after format is {word}ing' 
		return word

	def on_request(self, ch, method, props, body):
		word= body.decode()
		print(f'------------------------\nReceived {word}, checking grammar')
		response = self.check_grammar(word)
		print('Sending back result')
		ch.basic_publish(exchange='',
			routing_key=props.reply_to,
			properties=pika.BasicProperties(correlation_id= props.correlation_id),
			body=response)
		ch.basic_ack(delivery_tag=method.delivery_tag)
		print('Done! Check your result at client\n------------------------')

	# def clean_up(self):
	# 	self.queue_delete(queue='mom-soa-queue')
	# 	self.connection.close()

def exit_signal(signal, frame):
	print('\n[x] Quiting, everything is clean up')
	sys.exit(0)

if __name__ == '__main__':
	signal.signal(signal.SIGINT, exit_signal)
	checker_server = CheckGrammarServer()
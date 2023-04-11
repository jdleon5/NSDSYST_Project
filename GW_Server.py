#This code is from ACTIVITY 2 MESSAGE QUEUE

import pika, json 
credentials = pika.PlainCredentials('rabbituser','rabbit1234')
connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.5.39', 5672 ,'/',credentials))
channel = connection.channel()
channel.exchange_declare(exchange='logs', exchange_type='fanout') 

name=input('Enter your name: ')
msg=input('Enter your message: ') 
msg_dict={'name':name, 'msg':msg}
print (msg_dict)
msg_json=json.dumps(msg_dict) 
channel.basic_publish(exchange='logs', routing_key='', body=msg_json) 
#Specify routing key so we can route which server application takes the data

print(" [x] Sent '%s'",(msg_dict))
connection.close()
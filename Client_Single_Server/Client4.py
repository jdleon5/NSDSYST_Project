import pika, random, json, time
credentials = pika.PlainCredentials('rabbituser', 'rabbit1234')
connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.5.39', 5672 ,'/', credentials))
channel = connection.channel()
channel.queue_declare(queue='singlequeue') 

while True:
    try:
        #DATA GENERATION
        heartRate = random.randint(50, 110)
        longitude = random.uniform(-180.0, 180.0)
        latitude = random.uniform(-90.0, 90.0)
        steps = random.randint(100, 10000)
        distance = random.randint(100, 10000)
        cal = random.randint(500, 1500)
        temperature = random.uniform(34.0, 40.0)

        # msg = "{{\"AppID\":\"1\",\"steps\":\"{}\",\"heart rate\":\"{}\"}}".format(steps, heartRate)
        # print(msg)
        msg_dict={'AppID':1, 'name':'Miguel', 'steps':steps, 'calories':cal}
        print (msg_dict)
        msg_json=json.dumps(msg_dict) 
        channel.basic_publish(exchange='', routing_key='singlequeue', body=msg_json) 
        #Specify routing key so we can route which server application takes the data
        connection.process_data_events() # check for any incoming or outgoing messages
        time.sleep(3)
    except pika.exceptions.ConnectionClosed:
        print("Connection closed. Closing program...")
        break

connection.close()
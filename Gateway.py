import socket
import ssl
# import threading
import time
import json
import re
from datetime import datetime
from _thread import *

# Set up server socket
#HOST = '192.168.1.5'
HOST = '192.168.1.4'
PORT = 443

# Declaration 
policy_number = 0
allowed_keywords_P1 =  []
allowed_keywords_P2  = []
transform_keywords_P1 = []
transform_keywords_P2 = []
attribute_types_P1 = []
attribute_types_P2 = []

#Policy Initialization
def policy_initializer():
    f = open('Policy1.json') #policy file open
    policy_data = json.loads(f.read()) #policy file into python data
    #loop for iterating through json
    commands = policy_data["policy_rules_pm"]
    for command in commands:
        if command['Action'] == "Forward": #blocked or forward and check the resource
            allowed_keywords_P1.append(command['Resource'])
            attribute_types_P1.append(command['attributeType'])
        elif command['Action'] == "Transform":
            allowed_keywords_P1.append(command['Resource'])
            attribute_types_P1.append(command['attributeType'])
            transform_keywords_P1.append(command['Resource'])
    print("Policy 1 Allowed Keywords:\n", allowed_keywords_P1,
          "\nTransform Keywords:\n", transform_keywords_P1,
          "\nData Types:\n", attribute_types_P1)
    f.close()
    
    f = open('Policy2.json') #policy file open
    policy_data = json.loads(f.read()) #policy file into python data
    #loop for iterating through json
    commands = policy_data["policy_rules_ft"]
    for command in commands:
        if command['Action'] == "Forward": #blocked or forward and check the resource
            allowed_keywords_P2.append(command['Resource'])
            #attribute_types_P2.append(command['attributeType'])
        elif command['Action'] == "Transform":
            allowed_keywords_P2.append(command['Resource'])
            attribute_types_P2.append(command['attributeType'])
            transform_keywords_P2.append(command['Resource'])
    print("Policy 2 Allowed Keywords:\n", allowed_keywords_P2,
          "\nTransform Keywords:\n", transform_keywords_P2,
          "\nData Types:\n", attribute_types_P2)
    f.close()
    return

# Load the list of trusted client certificates
#trusted_client_certificates = "client_certs.pem"

    # Set allowed cipher suites
# context.set_ciphers('ECDHE+AESGCM')
    # Set up SSL context
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    # Root CA crt and set verification
# context.load_verify_locations(cafile='ca.pem')
# context.verify_mode = ssl.CERT_REQUIRED
context.load_cert_chain(certfile="server.crt", keyfile="server.key") #server.pem

#Set up session date/time on logs
now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
with open('HealthLogs.txt', 'a') as f:
            f.write("\n\nSession: ")
            f.write(dt_string)
            f.write("\n\n")
            f.close()

#App ID Check
def appID_check(message):
    fullstring = message
    substring1 = "\"AppID\":\"1\""
    substring2 = "\"AppID\":\"2\""

    if substring1 in fullstring:
        #print("Application 1 (Patient Monitoring) detected")
        return 1
    elif substring2 in fullstring:
        #print("Application 2 (Fitness Tracker) detected")
        return 2
    else:
        return 3
    
#Data Filtering
def data_filter(jsondata, policy_number, client_address):
    
    block = True #DEFAULT DENY
    client = client_address
    data_string = jsondata #health data into python string
    
    
    #Keyword Extraction
    Keywords = [] #empty keywords every packet (to refresh extraction)
    Values = [] #empty values every packet (to refresh extraction)
    #Values = [] 
    x = 0 #for index
    KeyValuePair = re.split(r'[,:]',  data_string)
    while x < len(KeyValuePair):
        if(x%2==0):
            Keywords.append(KeyValuePair[x].strip().strip("{").strip("\""))
        else:
            Values.append(KeyValuePair[x].strip().strip("}").strip("\""))
        x+=1
    print(Keywords)
    print(Values)

    #Policy Selection
    try:
        if policy_number == 1:
            allowed_keywords = allowed_keywords_P1
            transform_keywords = transform_keywords_P1
            attribute_types = attribute_types_P1
        elif policy_number == 2: 
            allowed_keywords = allowed_keywords_P2
            transform_keywords = transform_keywords_P2
            attribute_types = attribute_types_P2
        else:
            allowed_keywords = []
            transform_keywords = []
            attribute_types = []


        #Keyword Detection (Pass/Deny)
        x = 0 #index
        word_match = 0 #counter
        censorChar = "*"
        censorIndex = 2  # Start censoring from index 1 (i.e., after the first letter)

        while x < len(Keywords):
            if Keywords[x] in allowed_keywords: 
                word_match += 1
            if Keywords[x] in transform_keywords:
                #data_transform(Keywords[x], Values[x], transform_keywords)
                if Keywords[x] == 'latitude' or Keywords[x] == 'longitude':
                    Values[x] = str(round(float(Values[x]), 1))
                elif Keywords[x] == 'name':
                    Values[x] = Values[x][:censorIndex] + censorChar * (len(Values[x]) - censorIndex)
            x+=1  
            
        #Data Printing in HealthLogs.txt
        with open('HealthLogs.txt', 'a') as f:
            now = datetime.now()
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
            f.write(dt_string)
            f.write(" --- ")
            f.write(str(client))
            f.write("\n")
            #f.write(str(data_string))
            z = 0
            while z < len(Keywords):
                f.write(Keywords[z] + ":")
                f.write(Values[z] + ", ")
                z+=1
            #PASS PACKET
            if (word_match==len(Keywords)):
                if data_validation(Values, attribute_types):
                    f.write("\nPassed Packet")
                else:
                    f.write("\nDenied Packet (Data Validation Fail)")
                block = False
                #BLOCK PACKET
            else:
                f.write("\nDenied Packet (Keyword Detection Fail)")
            f.write("\n\n") 

        
        return
    
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(5)

#Data(Type) Validation
def data_validation(Values, attribute_types):
    print("Values:", Values)
    print("Types:", attribute_types)
    x = 0
    while x < len(Values):
        if (Values[x].isdigit()) and (attribute_types[x] == "integer"):
            print (Values[x], " is an integer")
        elif (Values[x].isascii()) and (attribute_types[x] == "string"):
            print (Values[x], " is a string")
        elif (Values[x].replace(".","").isascii()) and (attribute_types[x] == "decimal"):
            print (Values[x], " is a decimal")
        else:
            return False
        x+=1

    return True


#Data Transformation
# def data_transform(tkey, tval, transform_keys):
#     x = 0
#     while x < len(transform_keys):
#         if tkey[x] == "latitude" or tkey[x] == "longitude":
#             tval = round(tval, 2) # Converts to two decimal places
#         if tkey[x] == "name": 
#             tval = print()#cut the name

# Define client handling function
def handle_client(client_socket, addr):
    while True:
        try:
            # Wrap socket with SSL
            ssl_client_socket = context.wrap_socket(client_socket, server_side=True, do_handshake_on_connect=False)


                # Perform the SSL/TLS handshake
            ssl_client_socket.do_handshake()
            print('SSL/TLS handshake successful')

                #Verify the client's certificate against the root CA certificate
            client_cert = ssl_client_socket.getpeercert()
            if not client_cert:
                print('No client certificate received.')
            else:
                print('Received client certificate:', client_cert['subject'])
                ssl.match_hostname(client_cert, 'esp32-client')


            # Receive and print message from client
            message = ssl_client_socket.recv(1024).decode()
            print(f"Received message from client: {message}")

            # Send response to client
            response = "Hello, client!"
            ssl_client_socket.sendall(response.encode())

            while True:
                message = ssl_client_socket.recv(1024).decode()
                if message == 'Y' or message == 'y':
                    print(f"Client", addr, "disconnected.")
                    break
                #print(message)
                if len(message) > 30: #temp disable for first message data filter
                    data_filter(message, appID_check(message), addr)
                    #data_transform(message, appID_check(message), client_address)

            # Close SSL socket
            ssl_client_socket.close()
            break
        
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
            continue

#CLIENT CONNECTION ACCEPT
def connection_accept(server_socket):
    c, address = server_socket.accept()
    print(f'Connected to: {address[0]}:{str(address[1])}')
    start_new_thread(handle_client, (c, address[0], ))

def start_server(HOST, PORT):
    server_socket = socket.socket() #socket.AF_INET, socket.SOCK_STREAM
    try:
        server_socket.bind((HOST, PORT))
    except socket.error as e:
        print(str(e))
    print(f'Server is listening on port {PORT}...')    
    server_socket.listen(5)

    while True:
        connection_accept(server_socket)

policy_initializer()
start_server(HOST, PORT)
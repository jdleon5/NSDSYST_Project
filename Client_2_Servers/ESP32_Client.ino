#include <WiFi.h>
#include <WiFiClientSecure.h>

// Set up WiFi and TLS
const char* ssid = "InvalidUT";
const char* password = "PLDTWIFIzgxct_1";
const char* serverName = "192.168.1.4";
//ben
// const  char * ssid = "PLDTHOMEFIBR10879" ; 
// const  char * password = "PLDTWIFI21CMO" ;
// const char* serverName = "192.168.1.5";
const int serverPort = 443;

char stopped;
long heartRate, temperature, bloodPNum, bloodPDen, steps, distance, cal;
float longitude, latitude;
int rando, counter;

WiFiClientSecure client;

void setup() {
  Serial.begin(115200);

  // Connect to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(5000);
    Serial.println("Connecting to WiFi...");
  }

  // Verify server certificate
  client.setCACert("/ca.crt");
  client.setInsecure();

  // Load the client certificate and private key
  client.setCertificate("client.crt");
  client.setPrivateKey("client.key");  
}

void loop() {
  // Connect to server
    Serial.println("Connecting to server...");
    if (client.connect(serverName, serverPort)) {
      Serial.println("Connected to server!");
      
      // Send message to server
      client.println("Hello, server!");
      
      while (client.available() || client.connected()) {
        if(Serial.available() > 0)
        {
          stopped = Serial.read();
              if (stopped == 'Y' || stopped == 'y')
              {
                client.print(stopped);
                Serial.println("CLIENT: Stopping...");
                Serial.println("CLIENT: Disconnecting...");
                client.stop(); //Close the client
              }
        }
        heartRate = random(50, 110); //Normal 60-100
        longitude = (random(0,99999999)/1000000.0);//  random(0, 99999999) / 1000000.0;
        latitude = (random(0,99999999)/1000000.0);// random(0, 99999999) / 1000000.0;
        // Serial.println(longitude);
        // Serial.println(latitude);
        steps = 0;
        distance = 0;
        cal = 0;
            temperature = random(340, 400); //Celsius
            do{
                bloodPNum = random(80, 150);
                bloodPDen = random(60, 100);
            }while(bloodPNum < bloodPDen);
        //rando = random(5);   
        
          client.print("{\"AppID\":" + String("\"1\"") + ", " +
                      "\"name\":" + "\"" + "Johnny" + "\"" + ", " +
                      "\"heart rate\":" + "\"" + heartRate + "\"" + ", " + 
                      "\"longitude\":" + "\"" + longitude + "\"" + ", " + 
                      "\"latitude\":" + "\"" + latitude + "\"" + ", " + 
                      "\"blood pressure\":" + "\"" + bloodPNum +"/"+ bloodPDen + "\"" + "}");
          delay(3000);
          // //APP1 PASS         
          // client.print("{\"AppID\":" + String("\"1\"") + ", " +
          //             "\"heart rate\":" + "\"" + heartRate + "\"" + ", " +  
          //             "\"temperature\":" + "\"" + temperature/10.0 + "\"" + "}");
          // // delay(5000);
          // //NO APP ID
          // client.print("{\"AppID\":" + String("\"1\"") + 
          //              ", \"temperature\":" + temperature/10.0 + 
          //              ", \"calories burned\":" + cal+5 + "}");
          delay(3000);
          client.print("{\"AppID\":" + String("\"1\"") + ", " +
                      "\"name\":" + "\"" + "Andrew" + "\"" + ", " +
                      "\"heart rate\":" + "\"" + heartRate + "\"" + "}");
          // //APP 2 PASS
          // client.print("{\"AppID\":" + String("\"2\"") + ", " +
          //             "\"heart rate\":" + "\"" + heartRate + "\"" + ", " + 
          //             "\"number of steps\":" + "\"" + steps+3 + "\"" + ", " + 
          //             "\"distance traveled\":" + "\"" + distance+10 + "\"" + ", " +
          //             "\"calories burned\":" + "\"" + cal+5 + "\"" + "}"); 
          // delay(5000);
          // //APP 1 BLOCK
          // client.print("{\"AppID\":" + String("\"1\"") + ", " +
          //             "\"name\":" + "\"" + "Ben" + "\"" + ", " +
          //             "\"heart rate\":" + "\"" + heartRate + "\"" + ", " + 
          //             "\"respiration rate\":" + "\"" + random (40,60) + "\"" + ", " + 
          //             "\"temperature\":" + "\"" + temperature/10.0 + "\"" + ", " + 
          //             "\"blood pressure\":" + "\"" + bloodPNum +"/"+ bloodPDen + "\"" + "}");
          // delay(5000);
          // //APP 2 BLOCK
          client.print("{\"AppID\":" + String("\"2\"") + ", " +
                      "\"name\":" + "\"" + "Ben" + "\"" + ", " +
                      "\"heart rate\":" + "\"" + heartRate + "\"" + ", " + 
                      "\"number of steps\":" + "\"" + steps+3 + "\"" + ", " + 
                      "\"distance traveled\":" + "\"" + distance+10 + "\"" + ", " +  
                      "\"calories burned\":" + "\"" + cal+5 + "\"" + "}"); 
                      
        delay(3000);     
      }
      Serial.println("CLIENT: Current connection has been closed"); 
      client.stop();  //Close the client 
      while(1)
      {
        //Trap
        delay(2000);
        char ans;
        ans = Serial.read();
        if(ans == 'x')
          break;             
      }
  }
  else {
    Serial.println("CLIENT: Access failed");
    client.stop();
  }
  delay(5000);
}
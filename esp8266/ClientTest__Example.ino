//================================== Libraries =======================================
  #include <ESP8266WiFi.h> 
  #include <ESP8266HTTPClient.h>
//================================== I/O Pins ========================================
  #define       LED0      2
//==================================== WiFi ==========================================
  char* ssid = "TESTE";
  char* password = "123";
//=================================== Server =========================================
  int             ESPServerPort  = 8000;
  IPAddress       ESPServer(192,168,0,202);
  WiFiClient      client;
//====================================================================================

  void setup() 
  {
    Serial.begin(115200);
    
    pinMode(LED0, OUTPUT);
    Serial.println("\nPin Modes set\n");

    //============================ Connection to Network =============================
    if(WiFi.status() == WL_CONNECTED) 
    {
      WiFi.disconnect();
      WiFi.mode(WIFI_OFF);
      delay(50);
    }
    
    WiFi.mode(WIFI_STA);              //Disables Access Point generation
    WiFi.begin(ssid, password);       //SSID and password of the desired network
    Serial.println("!--- Connecting To " + WiFi.SSID() + " ---!");

    checkWiFi();                      //Blinks the LED to show ESP8266 is trying to connect to the network

    digitalWrite(LED0, LOW);
    Serial.println("!-- Client Device Connected --!\n");

    Serial.println("Connected To       : " + String(WiFi.SSID()));
    Serial.println("Signal Strenght    : " + String(WiFi.RSSI()) + " dBm");
    Serial.print  ("Server IP Address  : ");
    Serial.println(ESPServer);
    Serial.print  ("Server Port Number : ");
    Serial.println(ESPServerPort);
    Serial.print  ("Device MAC Address : ");
    Serial.println(String(WiFi.macAddress()));
    Serial.print  ("Device IP Address  : ");
    Serial.println(WiFi.localIP());
    Serial.print  ("\n\n");

	//============================ Connection to Server ==============================
	
    ESPRequest();

	//================================================================================
  }

//====================================================================================
  
  void loop()
  {
    HTTPClient http;
    int state;

        Serial.println("!---[HTTP] begin---!\n");
        http.begin("http://192.168.0.202:8000/GPIO/27/value");
        
        Serial.print("[HTTP] GET...\n");
        int httpCode = http.GET();

        if(httpCode > 0) {
			//Server response was received
            Serial.printf("[HTTP] GET - code: %d\n", httpCode);

            //Prints page information obtained through "GET" method
            if(httpCode == HTTP_CODE_OK) {
                String payload = http.getString();
                state = payload.toInt();
                Serial.println(payload);
            }
        } 
        
        else {
            Serial.printf("[HTTP] GET failed, error: %s\n", http.errorToString(httpCode).c_str());
        }

        if(state == 1)
            digitalWrite(LED0, HIGH);
        else
            digitalWrite(LED0, LOW);

        http.end();
        delay(200);
  }
//====================================================================================

  void checkWiFi()
  {
    while(WiFi.status() != WL_CONNECTED)
    {
      for(int i=0; i < 10; i++)
      {
        digitalWrite(LED0, !HIGH);
        delay(250);
        digitalWrite(LED0, !LOW);
        delay(250);
        Serial.print(".");
      }
      Serial.println("");
    }
  }

//====================================================================================

  void ESPRequest()
  {
    
    client.stop();
    Serial.println("!---Connecting to server---!");
    
    client.connect(ESPServer, ESPServerPort);
	
    if(client.connected())
    {
      Serial.println    ("<CONNECTED>\n");
      client.println ("<CONNECTED>");
    }
  }

//====================================================================================

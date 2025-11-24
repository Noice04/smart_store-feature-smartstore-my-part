# include "DHT.h"
# include <WiFi.h>
# include <PubSubClient.h>
#include <ArduinoJson.h>
#define DHTPIN 4
#define DHTTYPE DHT11

const char* ssid = "SM-G781W9921";
const char* password = "wyjn8694";

<<<<<<< HEAD
const char* mqtt_server = "10.142.122.153";
// const char* mqtt_server = "192.168.2.40";
// const char* mqtt_server = "192.168.0.134";
// const char* mqtt_server = "10.142.122.212";
=======
const char* mqtt_server = "192.168.0.134";
>>>>>>> 35caeed174d51c654adb1cde6058aa532bff8bd0

DHT dht(DHTPIN, DHTTYPE);

WiFiClient espClient;
PubSubClient client(espClient);
long lastMsg = 0;
char msg[50];
int value = 0;

float temperature = 0;
float humidity = 0;

const int ledPin = 4;

void setup() {
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);

  pinMode(ledPin, OUTPUT);
  dht.begin();
}

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* message, unsigned int length) {
  Serial.print("Message arrived on topic: ");
  Serial.print(topic);
  Serial.print(". Message: ");
  String messageTemp;
  
  for (int i = 0; i < length; i++) {
    Serial.print((char)message[i]);
    messageTemp += (char)message[i];
  }
  Serial.println();

  if (String(topic) == "frig2") {
    Serial.print("Changing output to ");
    if(messageTemp == "on"){
      Serial.println("on");
      digitalWrite(ledPin, HIGH);
    }
    else if(messageTemp == "off"){
      Serial.println("off");
      digitalWrite(ledPin, LOW);
    }
  }
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP8266Client")) {
      Serial.println("connected");
      client.subscribe("frig2");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}
void loop() {
<<<<<<< HEAD
  long now = millis();
  if (now - lastMsg > 5000) {
  lastMsg = now;

  client.connect("ESP8266Client");
  Serial.println("connected");
  client.subscribe("frig2");


  float t = dht.readTemperature();
=======
  

  long now = millis();
  if (now - lastMsg > 5000) {
    lastMsg = now;
    
    client.connect("ESP8266Client");
      Serial.println("connected");
      client.subscribe("frig2");
    float t = dht.readTemperature();
>>>>>>> 35caeed174d51c654adb1cde6058aa532bff8bd0
  float h = dht.readHumidity();

  if (isnan(t) || isnan(h)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }

  StaticJsonDocument<128> doc;
  doc["temperature"] = t;
  doc["humidity"] = h;

  char jsonBuffer[128];
  serializeJson(doc, jsonBuffer);

  client.publish("frig2", jsonBuffer);

  Serial.print("Published: ");
  Serial.println(jsonBuffer);
  }
}

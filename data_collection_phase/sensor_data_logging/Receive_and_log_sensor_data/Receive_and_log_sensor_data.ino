/**
 * This program receives the indoor temperature and humidity readings over LoRa,
 * and stores them in a real-time firebase database.
 *  
*/

#include <time.h>

// Turns the 'PRG' button into the power button, long press is off 
#define HELTEC_POWER_BUTTON   // must be before "#include <heltec_unofficial.h>"
#include <heltec_unofficial.h>

// Pause between transmited packets in seconds.
// Set to zero to only transmit a packet when pressing the user button
// Will not exceed 1% duty cycle, even if you set a lower value.
#define PAUSE               100

// Frequency in MHz. Keep the decimal point to designate float.
// Check your own rules and regulations to see what is legal where you are.
#define FREQUENCY           866.3       // for Europe
// #define FREQUENCY           905.2       // for US

// LoRa bandwidth. Keep the decimal point to designate float.
// Allowed values are 7.8, 10.4, 15.6, 20.8, 31.25, 41.7, 62.5, 125.0, 250.0 and 500.0 kHz.
#define BANDWIDTH           250.0

// Number from 5 to 12. Higher means slower but higher "processor gain",
// meaning (in nutshell) longer range and more robust against interference. 
#define SPREADING_FACTOR    9

// Transmit power in dBm. 0 dBm = 1 mW, enough for tabletop-testing. This value can be
// set anywhere between -9 dBm (0.125 mW) to 22 dBm (158 mW). Note that the maximum ERP
// (which is what your antenna maximally radiates) on the EU ISM band is 25 mW, and that
// transmissting without an antenna can damage your hardware.
#define TRANSMIT_POWER      0

String rxdata;
volatile bool rxFlag = false;
long counter = 0;
uint64_t last_tx = 0;
uint64_t tx_time;
uint64_t minimum_pause;


#include <Firebase_ESP_Client.h>
// #include <Arduino.h>
#include <WiFi.h>
#include "time.h"


#define FIREBASE_API_KEY " AIzaSyCwJUMsQhws8eu8AK-UtU4tRsBU6v3V5uM"
#define DATABASE_URL "https://temp-hum-logger-default-rtdb.europe-west1.firebasedatabase.app/ "


const char* ssid = "Glide_Resident";
const char* password = "BuckColdFive";
#define DATABASE_URL "https://temp-hum-logger-default-rtdb.europe-west1.firebasedatabase.app/"
#define FIREBASE_API_KEY "AIzaSyCwJUMsQhws8eu8AK-UtU4tRsBU6v3V5uM"
#define FIREBASE_PROJECT_ID "temp-hum-logger"


// Firebase objects
FirebaseData fbdo;
FirebaseAuth auth;
FirebaseConfig config;

const char* ntpServer = "pool.ntp.org";
const long gmtOffset_sec = 0;  // Adjust for your timezone (e.g., -3600 for GMT-1)
const int daylightOffset_sec = 0;  // Adjust for daylight savings


// Function that gets current epoch time
unsigned long getTime() {
  time_t now;
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    //Serial.println("Failed to obtain time");
    return(0);
  }
  time(&now);
  return now;
}



void setup() {
      
  configTime(0, 0, ntpServer);

  heltec_setup();
  both.println("Radio init");
  RADIOLIB_OR_HALT(radio.begin());
  // Set the callback function for received packets
  radio.setDio1Action(rx);
  // Set radio parameters
  both.printf("Frequency: %.2f MHz\n", FREQUENCY);
  RADIOLIB_OR_HALT(radio.setFrequency(FREQUENCY));
  both.printf("Bandwidth: %.1f kHz\n", BANDWIDTH);
  RADIOLIB_OR_HALT(radio.setBandwidth(BANDWIDTH));
  both.printf("Spreading Factor: %i\n", SPREADING_FACTOR);
  RADIOLIB_OR_HALT(radio.setSpreadingFactor(SPREADING_FACTOR));
  both.printf("TX power: %i dBm\n", TRANSMIT_POWER);
  RADIOLIB_OR_HALT(radio.setOutputPower(TRANSMIT_POWER));
  // Start receiving
  RADIOLIB_OR_HALT(radio.startReceive(RADIOLIB_SX126X_RX_TIMEOUT_INF));

  // ********************** Set up wifi and firebase connection
  // Serial.begin(9600);
  // Serial.println("Connecting to WiFi...");

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    // Serial.println("Connecting to WiFi...");
  }
  // Serial.println("Connected to WiFi");

  // Configure Firebase
  config.api_key = FIREBASE_API_KEY;
  config.database_url = DATABASE_URL;

  // Set Firebase authentication if needed
  auth.user.email = "bouchramohamedcheikh@gmail.com";      // Optional: Use your Firebase email
  auth.user.password = "Bouchra2003"; // Optional: Use your Firebase password

  // Serial.println("Set auth");

  // Initialize Firebase
  Firebase.begin(&config, &auth);
  // Serial.println("Firebase initialized.");

}


void loop() {

  heltec_loop();
  
  // If a packet was received, display it and the RSSI and SNR
  if (rxFlag) {
 
    rxFlag = false;
    radio.readData(rxdata);
    if (_radiolib_status == RADIOLIB_ERR_NONE) {
      both.printf("RX [%s]\n", rxdata.c_str());
    }
    RADIOLIB_OR_HALT(radio.startReceive(RADIOLIB_SX126X_RX_TIMEOUT_INF));


    // ************** Save the received data on the firebase database 
    // Extract temperature value
    int tempStart = rxdata.indexOf("T:") + 2;  // Start after "T:"
    int tempEnd = rxdata.indexOf(" C");        // End before " C"
    String temperatureStr = rxdata.substring(tempStart, tempEnd); // Extract substring
    float temperature = temperatureStr.toFloat();   // Convert to float

    // Extract humidity value
    int humStart = rxdata.indexOf("H:") + 2;   // Start after "H:"
    int humEnd = rxdata.indexOf(" %");         // End before " %"
    String humidityStr = rxdata.substring(humStart, humEnd); // Extract substring
    float humidity = humidityStr.toFloat();         // Convert to float

    // Get the current timestamp
    time_t timestamp = time(nullptr);

    FirebaseJson data;
    data.set("temperature", temperature);  
    data.set("humidity", humidity); 
    data.set("timestamp", timestamp);    

    String path = "/sensorData";      // Path in the Realtime Database
    
    if (Firebase.RTDB.pushJSON(&fbdo, path.c_str(), &data)) {
      // Serial.println("Data saved successfully to Firebase.");
    } else {
      // Serial.print("Error saving data: ");
      // Serial.println(fbdo.errorReason());
      
      ESP.restart(); // Reboot the ESP32 if when Firebase token is invalid 
    }

  }
}

// Can't do Serial or display things here, takes too much time for the interrupt
void rx() {
  rxFlag = true;
}



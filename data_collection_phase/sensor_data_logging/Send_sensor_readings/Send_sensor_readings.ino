/**
 * This program is run on the ESP32 connected to DHT11 sensor.
 * It reads temperature and humidity from this sensor and sends it over LoRa. 
 *  
*/


#include <dht_nonblocking.h>

#define DHT_SENSOR_TYPE DHT_TYPE_11

static const int DHT_SENSOR_PIN = 37; // pin to which the sensor is connected
DHT_nonblocking dht_sensor(DHT_SENSOR_PIN, DHT_SENSOR_TYPE);

#define HELTEC_POWER_BUTTON   // must be before "#include <heltec_unofficial.h>"
#include <heltec_unofficial.h>

// Define LoRa parameters
#define PAUSE               100  // Pause between transmitted packets in seconds.
#define FREQUENCY           866.3  // Frequency in MHz (for Europe)
#define BANDWIDTH           250.0  // LoRa bandwidth
#define SPREADING_FACTOR    9  // Spreading factor
#define TRANSMIT_POWER      0  // Transmit power in dBm

String txdata;
volatile bool rxFlag = false;
long counter = 0;
uint64_t last_tx = 0;
uint64_t tx_time;
uint64_t minimum_pause;

void setup() {

  heltec_setup();
  both.println("Radio init");
  RADIOLIB_OR_HALT(radio.begin());

  radio.setDio1Action(rx);  // Set the callback function for received packets

  both.printf("Frequency: %.2f MHz\n", FREQUENCY);
  RADIOLIB_OR_HALT(radio.setFrequency(FREQUENCY));
  both.printf("Bandwidth: %.1f kHz\n", BANDWIDTH);
  RADIOLIB_OR_HALT(radio.setBandwidth(BANDWIDTH));
  both.printf("Spreading Factor: %i\n", SPREADING_FACTOR);
  RADIOLIB_OR_HALT(radio.setSpreadingFactor(SPREADING_FACTOR));
  both.printf("TX power: %i dBm\n", TRANSMIT_POWER);
  RADIOLIB_OR_HALT(radio.setOutputPower(TRANSMIT_POWER));

  RADIOLIB_OR_HALT(radio.startReceive(RADIOLIB_SX126X_RX_TIMEOUT_INF));
}

void loop() {
  heltec_loop();

  bool tx_legal = millis() > last_tx + minimum_pause;
  
  // Check if we have valid temperature and humidity readings
  float temperature;
  float humidity;

  if (dht_sensor.measure(&temperature, &humidity)) {
    // Format the message as "T: <value> C, H: <value> %"
    txdata = "T:" + String(temperature, 2) + " C, H:" + String(humidity, 2) + " %";

    // Transmit the data
    both.printf("TX [%s] ", txdata.c_str());
    radio.clearDio1Action();
    heltec_led(50);  // 50% brightness is plenty for this LED
    tx_time = millis();
    RADIOLIB(radio.transmit(txdata.c_str()));  // Send the temperature and humidity string
    tx_time = millis() - tx_time;
    heltec_led(0);

    if (_radiolib_status == RADIOLIB_ERR_NONE) {
      both.printf("OK (%i ms)\n", (int)tx_time);
    } else {
      both.printf("fail (%i)\n", _radiolib_status);
    }

    // Maximum 1% duty cycle
    minimum_pause = tx_time * 100;
    last_tx = millis();
    radio.setDio1Action(rx);
    RADIOLIB_OR_HALT(radio.startReceive(RADIOLIB_SX126X_RX_TIMEOUT_INF));
  
  
    delay(300000); // send sensor readings evey 5 minutes
  }
}

// Callback function for RX, not used in this version but still required
void rx() {
  rxFlag = true;
}




#include <SPI.h>
#include <WiFiNINA.h>
#include <HttpClient.h>

#define SECRET_SSID "alexander_w"
#define SECRET_PASS "FBEsAsDesGes!"


///////please enter your sensitive data in the Secret tab/arduino_secrets.h
char ssid[] = SECRET_SSID;        // your network SSID (name)
char pass[] = SECRET_PASS;    // your network password (use for WPA, or use as key for WEP)
int keyIndex = 0;            // your network key Index number (needed only for WEP)

// Number of milliseconds to wait if no data is available before trying again
const int kNetworkDelay = 1000;

int status = WL_IDLE_STATUS;

WiFiClient client;


// Make an HTTP POST request
void post(const char* server, int port, String path, String args) {
  HttpClient httpClient(client);

  String x = path + String("?") + args;
  Serial.println(server);
  Serial.println(x);
  int result = httpClient.post(server, port, x.c_str());
  httpClient.stop();
}

void get(const char* server, int port, const char* path, char* buf) {
  HttpClient http(client);
  int err = http.get(server, port, path);
  err = http.skipResponseHeaders();

  if (err >= 0) {
    int bodyLen = http.contentLength();
    int i = 0;
    char c;

    while ( (http.connected() || http.available()) ) {
      if (http.available()) {
        c = http.read();
        buf[i++] = c;
      } else {
        // We haven't got any data, so let's pause to allow some to
        // arrive
        delay(kNetworkDelay);
      }
    }

    buf[i] = 0;
  }

  http.stop();
}


void init_network() {
  // check for the WiFi module:
  if (WiFi.status() == WL_NO_MODULE) {
    Serial.println("Communication with WiFi module failed!");
    // don't continue
    while (true);
  }

  String fv = WiFi.firmwareVersion();
  if (fv < WIFI_FIRMWARE_LATEST_VERSION) {
    Serial.println("Please upgrade the firmware");
  }

  // attempt to connect to Wifi network:
  while (status != WL_CONNECTED) {
    Serial.print("Attempting to connect to SSID: ");
    Serial.println(ssid);
    // Connect to WPA/WPA2 network. Change this line if using open or WEP network:
    status = WiFi.begin(ssid, pass);

    // wait 10 seconds for connection:
    delay(10000);
  }
  Serial.println("Connected to wifi");
  printWifiStatus();
}


void printWifiStatus() {
  // print the SSID of the network you're attached to:
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // print your board's IP address:
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);

  // print the received signal strength:
  long rssi = WiFi.RSSI();
  Serial.print("signal strength (RSSI):");
  Serial.print(rssi);
  Serial.println(" dBm");
}

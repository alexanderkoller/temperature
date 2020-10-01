
const char server[] = "192.168.0.31";
int port = 5000;
int measurement_run = 0;


void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW); // turn off builtin LED
  
  delay(1000);
  Serial.begin(9600);
  delay(1000);

  sensors.begin();  // initialize sensors
  adresseAusgeben(); /* Adresse der Devices ausgeben */

  init_network();   // initialize network connection
  
  digitalWrite(LED_BUILTIN, HIGH); // turn off builtin LED


  // get measurement run id
  char buf[500];
  get(server, port, "/init", buf);
  measurement_run = atoi(buf);
  Serial.print("Run ID is: ");
  Serial.println(measurement_run);
}

void loop() {
  Serial.println();
  sensors.requestTemperatures(); // Temp abfragen
  float temp = sensors.getTempCByIndex(0);

  Serial.print(temp);
  Serial.print(" Grad Celsius");

  if( temp > -100 ) { // ignore error values
    String url = String("/post_temperature");
    String args = String("temp=") + String(temp);
    args = args + "&id=" + String(measurement_run);
    post(server, port, url, args);
  }

  delay(1000);
}

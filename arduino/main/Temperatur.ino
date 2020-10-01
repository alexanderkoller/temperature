/* 
TWTemp Version 1.0 vom 14.06.2013 

8038 bytes

Thomas Wenzlaff http://www.wenzlaff.de

Temperature Sensor DS18B20 an Digitalen Port Pin 2 wie folgt verbunden
Links=Masse, 
Mitte=Data, 
Rechts=+5V, 
3300 to 4700 Ohm Widerstand von +5V nach Data.

Es wird erst die Adresse des 1-Wire-Device ausgegeben und dann wird die Temperaturmessung gestartet.

*/

/* Benötigte Bibliotheken importieren */
#include <OneWire.h>
#include <DallasTemperature.h>

#define ONE_WIRE_BUS 21 /* Digitalport Pin 2 definieren */

OneWire ourWire(ONE_WIRE_BUS); /* Ini oneWire instance */

DallasTemperature sensors(&ourWire);/* Dallas Temperature Library für Nutzung der oneWire Library vorbereiten */


void adresseAusgeben(void) {
  byte i;
  byte present = 0;
  byte data[12];
  byte addr[8];

  Serial.print("Suche 1-Wire-Devices...\n\r");// "\n\r" is NewLine
  while(ourWire.search(addr)) {
    Serial.print("\n\r\n\r1-Wire-Device gefunden mit Adresse:\n\r");
    for( i = 0; i < 8; i++) {
      Serial.print("0x");
      if (addr[i] < 16) {
        Serial.print('0');
      }
      Serial.print(addr[i], HEX);
      if (i < 7) {
        Serial.print(", ");
      }
    }
    if ( OneWire::crc8( addr, 7) != addr[7]) {
      Serial.print("CRC is not valid!\n\r");
      return;
    }
  }
  Serial.println();
  ourWire.reset_search();
  return;
}

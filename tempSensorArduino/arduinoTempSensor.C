#include <OneWire.h>
#include <DallasTemperature.h>

#define ONE_WIRE_BUS 2

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);


void setup(void)
{
 // start serial port
 Serial.begin(9600);
 sensors.begin();
}


void loop(void)
{
 // Get temperature readings
 sensors.requestTemperatures();

 Serial.println(sensors.getTempCByIndex(0));
 delay(5000); // 5 second intervals
}

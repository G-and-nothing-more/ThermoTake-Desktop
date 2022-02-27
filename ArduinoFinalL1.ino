#include <OneWire.h>
#include <DallasTemperature.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 20, 4); 

// Data wire is plugged into port 2 on the Arduino
#define ONE_WIRE_BUS 2 //pin for sensor

// Setup a oneWire instance to communicate with any OneWire devices (not just Maxim/Dallas temperature ICs)
OneWire oneWire(ONE_WIRE_BUS);

// Pass our oneWire reference to Dallas Temperature.
DallasTemperature sensors(&oneWire);

//value that determines if LCD backlight is lit
bool light = 0;
/*
   The setup function. We only start the sensors here
*/
void setup(void)
{
  // start serial port
  Serial.begin(9600);
 
  // Start up the library
  sensors.begin();
  lcd.init();
  //lcd.backlight();
}

/*
   Main function, get and show the temperature
*/
void loop(void)
{

  const int buttonPin = 8;
  int buttonState = 0;
  
  // call sensors.requestTemperatures() to issue a global temperature
  // request to all devices on the bus
  //Serial.print("Requesting temperatures...");
  sensors.requestTemperatures(); // Send the command to get temperatures
  //Serial.println("DONE");
  
  // After we got the temperatures, we can print them here.
  // We use the function ByIndex, and as an example get the temperature from the first sensor only.
  float tempC = sensors.getTempCByIndex(0);


  pinMode(buttonPin,INPUT);

  buttonState = digitalRead(buttonPin);

  /*
   * This block checks to see if there is serial data able to be read in from the PC end.
   * If there is data being sent, then flip the light boolean. We do not need to process the serial further since it is the only 
   * incoming data sent over the port.
   */
  if(Serial.available() > 0){
    Serial.read();
     if (light == 0){
      light = 1;
     }
     else if (light == 1){
      light = 0;
     }
    
  }

  /*
   * If the button is pushed or the light boolean is true
   */
  if (buttonState == HIGH || light) {
   //clear the serial
  Serial.read();
  // Check if reading was successful
  lcd.backlight();
  lcd.display();

  //if the thermometer is dissconnected
  if (tempC != DEVICE_DISCONNECTED_C)
  {
    //Serial.print("Temperature for the device 1 (index 0) is: ");
    
    
    lcd.setCursor(0, 0);
    lcd.print("Temperature:");
    lcd.setCursor(0, 1);
    lcd.print(tempC);
    lcd.print((char)223);
    lcd.print("C");
    lcd.print(" | ");
    lcd.print(DallasTemperature::toFahrenheit(tempC));
    lcd.print(" F");
    
  }
  else
  {
    //Serial.println("Error: Could not read temperature data");
     lcd.clear(); 
     lcd.setCursor(0, 0);
     lcd.print("Sensor Error ");
     Serial.println("error");
  }
  }
  else if (buttonState == LOW) {
    lcd.noBacklight();
    lcd.noDisplay();
    }

    // Finally encode the rounded temperature in C and attatch the checksum
    int roundedValue = 100 * tempC;
    double rounded = (double)roundedValue/100;
    int check1 = roundedValue %64;

    //Print the data over the serial port (HC-05)
    Serial.print(rounded);
    Serial.print(":");
    Serial.println(check1);
    delay(100);
}

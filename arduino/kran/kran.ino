/*
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  ‾‾‾‾‾‾‾‾‾‾4-------------8‾‾‾‾‾‾‾‾‾‾
            3             7
            ┆             ┆
            ┆             ┆
            2             6
  __________1-------------5__________
  ==============================
*/

#define sensor1 2
#define sensor2 3
#define sensor3 4
#define sensor4 5
#define sensor5 6
#define sensor6 7
#define sensor7 8
#define sensor8 9

#include <SoftwareSerial.h>
#define onShield  12
#include<stdio.h>
#include<string.h>

SoftwareSerial SimSerial(10, 11); // TX,  RX

uint32_t Timer1, Timer2, Timer3, Timer4, Timer5, Timer6, Timer7, Timer8;
uint32_t TimerPrint, TimerEmpty;
int p90, p180; // один цикл 90 и один цикл 180
int dalaySensors = 2000; //ожидание после срабатывания датчика
int halfTurn180; // оборот в одну сторону на 180 градусов
int p90Temp, p180Temp; // переменные для хранения предыдущих значений
int countGet = 0; // счетчик отправленных запросов
String data, two_las_simvols;
String latitude, longitude;
int Led = 13;//LED pin

String dataGPS, statusGet;
String const ip_addr = "http://18.139.162.128";
String const api = "/api/v1.0/add_get_kran";
String const mechanism_id = "13893";
String const password = "super_pass";
int bad_conect;



void setup()
{
  pinMode(Led, OUTPUT);
  pinMode(sensor1, INPUT_PULLUP);
  pinMode(sensor2, INPUT_PULLUP);
  pinMode(sensor3, INPUT_PULLUP);
  pinMode(sensor4, INPUT_PULLUP);
  pinMode(sensor5, INPUT_PULLUP);
  pinMode(sensor6, INPUT_PULLUP);
  pinMode(sensor7, INPUT_PULLUP);
  pinMode(sensor8, INPUT_PULLUP);
  Serial.begin(9600);
  LED();
  delay(100);
  LED();
  SimSerial.begin(9600);
  SimSerial.setTimeout(1000);
  //  updateSerial();
  turnOnShield();
  turnOnGPS();
  registrationSim();
  ArduinoToSim("AT+GSMBUSY=1", 500); //Reject incoming call
  statusShield();
  statusConect();

}

void loop()
{


  if (digitalRead(sensor1) == 0 && millis() - Timer1 > dalaySensors)
  {
    Timer1 = millis();
    data += "1";
    LED();
  }

  if (digitalRead(sensor2) == 0 && millis() - Timer2 > dalaySensors)
  {
    Timer2 = millis();
    data += "2";
    LED();
  }

  if (digitalRead(sensor3) == 0 && millis() - Timer3 > dalaySensors)
  {
    Timer3 = millis();
    data += "3";
    LED();
  }
  if (digitalRead(sensor4) == 0 && millis() - Timer4 > dalaySensors)
  {
    Timer4 = millis();
    data += "4";
    LED();
  }

  if (digitalRead(sensor5) == 0 && millis() - Timer5 > dalaySensors)
  {
    Timer5 = millis();
    data += "5";
    LED();
  }

  if (digitalRead(sensor6) == 0 && millis() - Timer6 > dalaySensors)
  {
    Timer6 = millis();
    data += "6";
    LED();
  }

  if (digitalRead(sensor7) == 0 && millis() - Timer7 > dalaySensors)
  {
    Timer7 = millis();
    data += "7";
    LED();
  }

  if (digitalRead(sensor8) == 0 && millis() - Timer8 > dalaySensors)
  {
    Timer8 = millis();
    data += "8";
    LED();
  }



  if (millis() - TimerPrint > 1000)
  {
    TimerPrint = millis();
    Serial.println(data + ":" + p90 + "-" + p180 + " >" + bad_conect);

  }

  if (millis() - TimerEmpty > 300000) {
    TimerEmpty = millis();
    GetSend(0, countGet, latitude, longitude);
  }

  if (data.length() >= 4) {
    if (data == "1234" || data == "4321" || data == "5678" || data == "8765") {
      halfTurn180++; // половина цикла поворота
    }

    if (data == "1221" || data == "4334" || data == "5665" || data == "8778") {
      p90++;
    }
    data = "";
    p180 += halfTurn180 / 2; // цикл считается когда кран повернулся на 180 туда и обратно

    if (p90 - p90Temp == 1) { // если новое значение больше старого
      dataGPS = sendData("AT + CGPSINF=2", 2000);
      ParseGPS(dataGPS);
      Serial.println(" отправляем на сервер 90 градусов" +  String(p90) + " " + String(countGet));
      GetSend(1, countGet, latitude, longitude);
      AfterGet();
    }
    if (p180 - p180Temp == 1) {// если новое значение больше старого
      dataGPS = sendData("AT + CGPSINF=2", 2000);
      ParseGPS(dataGPS);
      Serial.println(" отправляем на сервер 180 градусов" +  String(p180) + " " + String(countGet));
      GetSend(2, countGet, latitude, longitude);
      AfterGet();
    }
    p90Temp = p90;
    p180Temp = p180;

  }

  if (data.length() >= 3) { // если оди датчик не сработал то скидываем data в положениях стрела на море или на штабель
    two_las_simvols = data.substring(data.length() - 2, data.length());
    if (two_las_simvols == "21" || two_las_simvols == "34" || two_las_simvols == "65" ||  two_las_simvols == "78") {
      data = "";
    }
  }


}


void LED() {
  digitalWrite(Led, HIGH);
  delay(100);
  digitalWrite(Led, LOW);
}

void AfterGet() {
  statusConectCount();
  countGet++;
  halfTurn180 = 0;
  LED();
  delay(100);
  LED();
  TimerEmpty = millis();
}

void(* resetFunc) (void) = 0;

void statusShield() { // if Shild is turn of then turn on
  String statusSim;
  updateSerial(); // clear Serial
  statusSim = sendData("AT", 500);
  if (statusSim.indexOf("OK") < 0) {
    statusConect();
    resetFunc();
  }
}

void turnOnShield() {
  digitalWrite(onShield, HIGH);
  delay(1000);
  digitalWrite(onShield, LOW);
  delay(2000); // give time to register Sim online
}

void turnOnGPS() {
  ArduinoToSim("AT", 1000);
  ArduinoToSim("AT + CGPSPWR=1", 1000);
  ArduinoToSim("AT + CGPSRST=2", 1000); // 1 HOT; 2 WARM
  ArduinoToSim("AT + CGPSINF=2", 1000);
  ArduinoToSim("AT+CGNSSEQ=RMC", 1000);
  ArduinoToSim("AT + CGPSSTATUS?", 1000);
}

void registrationSim() {
  ArduinoToSim("AT", 1000);// Status Shild
  ArduinoToSim("AT+CSQ", 1000);//Signal quality test, 0-31
  ArduinoToSim("AT+CCID", 1000);// SIM card information
  ArduinoToSim("AT + CIPSHUT", 1000);//Break all connections
  ArduinoToSim("AT+CGATT=1", 1000);// GPRS attach or deatach
  ArduinoToSim("AT + CREG?", 1000);// is module in network
  ArduinoToSim("AT + SAPBR = 3,1, \"CONTYPE\", \"GPRS\"", 1000);
  ArduinoToSim("AT+SAPBR=3,1,\"APN\",\"internet.beeline.ru\"", 1000);  //internet.mts.ru
  ArduinoToSim("AT+SAPBR=1,1", 2000); //Conect gprs
  ArduinoToSim("AT+SAPBR=2,1", 1000); //Status Conect gprs
  ArduinoToSim("AT+HTTPINIT", 1000);
}


void ParseGPS(String str) {
  int v0, v1, v2, v3,  v4, v5;
  v0 = str.indexOf("CGPSINF:");
  v1 = str.indexOf(",", v0 + 1);
  v2 = str.indexOf(",", v1 + 1);
  v3 = str.indexOf(",", v2 + 1);
  v4 = str.indexOf(",", v3 + 1);
  v5 = str.indexOf(",", v4 + 1);
  latitude = str.substring(v2 + 3, v3);
  longitude = str.substring(v4 + 3, v5);
  if (latitude == "00.0000") {
    latitude = "0"; // because server gets it how last data
    longitude = "0";
  }
}


void statusConectCount() { // if bad conect more then 3 then reset
  String statusGPRS;
  updateSerial(); // clear Serial
  statusGPRS = sendData("AT+SAPBR=2,1", 500);
  //  Serial.println("______________");
  //  Serial.println(statusGPRS);
  if (statusGPRS.indexOf("SAPBR: 1,1,") < 0) {
    bad_conect++;
    if (bad_conect > 3) {
      bad_conect = 0;
      ArduinoToSim("AT+CPOWD=1", 200);
      delay(3000);
      turnOnShield();
      turnOnGPS();
      registrationSim();
    }
    else {
      bad_conect = 0;
    }
  }
}

void GetSend(int value, int count, String latitudeD, String longitudeD) {
  //sent data on server
  String get_request;
  get_request = "AT+HTTPPARA=\"URL\", \"" + ip_addr + api + "?mechanism_id=" + mechanism_id + "&password=" + password + "&value=" + String(value) + "&value3=" + String(count) +  "&latitude=" + latitudeD + "&longitude=" + longitudeD + "\"";
  ArduinoToSim("AT+HTTPINIT", 100);  // ???
  ArduinoToSim("AT+HTTPPARA=\"CID\",1", 100);
  ArduinoToSim(get_request, 100);
  ArduinoToSim("AT+HTTPACTION=0", 100);
  ArduinoToSim("AT+HTTPREAD", 100);
  ArduinoToSim("AT+HTTPTERM", 100); // ???
}


String sendData (String command , const int timeout) { // sent data to serial port return ansver
  String response = "";
  SimSerial.println(command);
  long int time = millis();
  int i = 0;
  while ( (time + timeout ) > millis()) {
    while (SimSerial.available()) {
      char c = char(SimSerial.read());
      response += c;
    }
  }
  return response;
}

void ArduinoToSim(String command, const int wait) { //it is more comfortable
  SimSerial.println(command);
  delay(wait);
  updateSerial();
}


void updateSerial()
//message view function
{
  // delay(1000);
  while (Serial.available())
  {
    SimSerial.write(Serial.read());
  }
  while (SimSerial.available())
  {
    Serial.write(SimSerial.read());
  }
}

void statusConect() { // if GPRS not conect then reset
  String statusGPRS;
  updateSerial(); // clear Serial
  statusGPRS = sendData("AT+SAPBR=2,1", 2000);
  //  Serial.println("______________");
  if (statusGPRS.indexOf("SAPBR: 1,1,") < 0) {
    ArduinoToSim("AT+CPOWD=1", 1000);
    delay(3000);
    turnOnShield();
    turnOnGPS();
    registrationSim();
  }
}

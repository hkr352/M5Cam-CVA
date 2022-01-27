#include "esp_camera.h"
#include <WiFi.h>
#include <WiFiUdp.h>

// Select Huge APP

#define CAMERA_MODEL_M5STACK_WIDE

#include "camera_pins.h"

#define AI_CAMERA
#define N_BUFFER 1024

WiFiUDP udp;

const char* ssid = "SSID";
const char* password = "PASSWORD";

//const int
//uint8_t
int port = 50104;
uint8_t remotePortt = 50104;
IPAddress remoteIp(192,168,255,255);
//IPAddress remoteIp(192,168,2,243);
//unsigned long timeNow = 0;
unsigned long timeM = 0;
bool timeFlag = false;
bool remoteFlag = false;

void startCameraServer();

int val = 0;

void setup() {
  Serial.begin(115200);
  Serial.setDebugOutput(true);
  Serial.println();

  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  //init with high specs to pre-allocate larger buffers
  if(psramFound()){
    config.frame_size = FRAMESIZE_UXGA;
    config.jpeg_quality = 10;
    config.fb_count = 2;
  } else {
    config.frame_size = FRAMESIZE_SVGA;
    config.jpeg_quality = 12;
    config.fb_count = 1;
  }

#if defined(AI_CAMERA)
  pinMode(13, INPUT_PULLUP);
  pinMode(14, OUTPUT);
#endif


  // camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    //Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }

  sensor_t * s = esp_camera_sensor_get();
  //initial sensors are flipped vertically and colors are a bit saturated
  if (s->id.PID == OV3660_PID) {
    s->set_vflip(s, 1);//flip it back
    s->set_brightness(s, 1);//up the blightness just a bit
    s->set_saturation(s, -2);//lower the saturation
  }
  //drop down frame size for higher initial frame rate
  s->set_framesize(s, FRAMESIZE_QVGA);

#if defined(CAMERA_MODEL_M5STACK_WIDE)
  s->set_vflip(s, 1);
  s->set_hmirror(s, 1);
#endif

  WiFi.begin(ssid, password);
  char buff[16];
  int stageSelect =0;
  String SSIDD = "";
  String PASSWORD = "";
  while (WiFi.status() != WL_CONNECTED) {
    if(Serial.available() > 0){
        String str = Serial.readStringUntil('\n');
        Serial.println(str);
        switch(stageSelect){
            case 1:
                SSIDD = str;
                stageSelect = 0;
                Serial.println(SSIDD);
                Serial.println("conf");
                break;
            case 2:
                PASSWORD = str;
                stageSelect = 0;
                Serial.println(PASSWORD);
                Serial.println("conf");
                break;
        }

        if( str.equals("SSID") ){
            stageSelect = 1;
            Serial.println("input SSID");
        }
        else if( str.equals("PASS") ){
            stageSelect = 2;
            Serial.println("input PASS");
        }
        else if( str.equals("CON") ){
            Serial.println("input CON");
            Serial.println(SSIDD);
            Serial.println(PASSWORD);
            WiFi.begin(SSIDD.c_str(),PASSWORD.c_str());
        }
        
    }else{
        delay(500);
        Serial.print(".");
    }
    
  }
  //Serial.println("");
  //Serial.println("WiFi connected");

  startCameraServer();

  Serial.print("Camera Ready! Use 'http://");
  Serial.print(WiFi.localIP());
  Serial.println("' to connect");

  udp.begin(port);
}

void loop() {
#if defined(AI_CAMERA)

    char packetBuffer[N_BUFFER];
    int packetSize = udp.parsePacket();
 
    // get packet
    if (packetSize){
        int len = udp.read(packetBuffer, packetSize);
        if (len > 0){
            packetBuffer[len] = '\0'; // end
        }
        Serial.println(packetBuffer);
        //Serial1.printf("Received %d bytes from %s, port %d\n", packetSize, Udp.remoteIP().toString().c_str(), Udp.remotePort());
        Serial.println(udp.remoteIP());
        Serial.println(udp.remotePort());
        remoteIp = udp.remoteIP();
        
        udp.beginPacket(remoteIp, udp.remotePort());
        udp.print(packetBuffer);

        if(!strcmp(packetBuffer, "con"))
        {
            remoteFlag = true;
        }else if(!strcmp(packetBuffer, "dcon")){
            remoteFlag = false;
        }
        udp.endPacket();
    }

    val = digitalRead(13);
    digitalWrite(14, val);
    if (val == 0){
        if (!timeFlag){
            timeM = millis();
            timeFlag = true;
        }
        if ((millis()-timeM) >= 5000 ){
            if(remoteFlag){
                //delay(5000);
                udp.beginPacket(remoteIp, udp.remotePort());
                udp.print("detect");// udp.write("5");
                udp.endPacket();
                digitalWrite(14, HIGH);
                delay(10000);
            }
        }
    }else{
        timeFlag = false;
        timeM = millis();
    }

    
//    if (val == 0){
//        if(remoteFlag){
//            delay(5000);
//            udp.beginPacket(remoteIp, udp.remotePort());
//            udp.print("detect");// udp.write("5");
//            udp.endPacket();
//            digitalWrite(14, HIGH);
//            delay(10000);
//        }else{
//            //udp.beginPacket(remoteIp, remotePortt);
//        }
//    }
#endif
  //delay(500);//delay(10000);
}

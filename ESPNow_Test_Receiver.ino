#include <WiFi.h>
#include <esp_now.h>

struct SOSMessage
{
  char name[30];
  char phone[20];
  char type[20];
  char message[150];
};

// Callback function when data is received
SOSMessage receivedSOS;

void OnDataRecv(const esp_now_recv_info *info, const uint8_t *incomingData, int len)
{
  memcpy(&receivedSOS, incomingData, sizeof(receivedSOS));

  Serial.println();
  Serial.println("SOS_START");
  Serial.println(receivedSOS.name);
  Serial.println(receivedSOS.phone);
  Serial.println(receivedSOS.type);
  Serial.println(receivedSOS.message);
  Serial.println("SOS_END");
}

void setup()
{
    Serial.begin(115200);

    WiFi.mode(WIFI_STA);

    Serial.print("Gateway MAC: ");
    Serial.println(WiFi.macAddress());

    if (esp_now_init() != ESP_OK)
    {
        Serial.println("ESP-NOW Init Failed");
        return;
    }

    esp_now_register_recv_cb(OnDataRecv);

    Serial.println("Gateway Ready...");
}

void loop()
{

}

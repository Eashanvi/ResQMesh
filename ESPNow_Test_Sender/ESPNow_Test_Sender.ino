#include <WiFi.h>
#include <esp_now.h>
#include <string.h>

struct SOSMessage
{
  char name[30];
  char phone[20];
  char type[20];
  char message[150];
};

// Gateway Station MAC
uint8_t gatewayMAC[] = {0xD4, 0xE9, 0xF4, 0x78, 0xE7, 0xD4};

esp_now_peer_info_t peerInfo;

SOSMessage sos;

void setup()
{
  Serial.begin(115200);

  WiFi.mode(WIFI_STA);

  Serial.println("Access Node Started");

  if (esp_now_init() != ESP_OK)
  {
    Serial.println("ESP-NOW Init Failed");
    return;
  }

  memcpy(peerInfo.peer_addr, gatewayMAC, 6);
  peerInfo.channel = 0;
  peerInfo.encrypt = false;

  if (esp_now_add_peer(&peerInfo) != ESP_OK)
  {
    Serial.println("Failed to Add Peer");
    return;
  }

  Serial.println("Peer Added Successfully");
}

void loop()
{
  strcpy(sos.name, "Eashanvi");
  strcpy(sos.phone, "9063955544");
  strcpy(sos.type, "Fire");
  strcpy(sos.message, "Fire in Building A");

  esp_err_t result = esp_now_send(
      gatewayMAC,
      (uint8_t *)&sos,
      sizeof(sos));

  if (result == ESP_OK)
  {
    Serial.println("Message Sent");
  }
  else
  {
    Serial.println("Send Failed");
  }

  delay(3000);
}
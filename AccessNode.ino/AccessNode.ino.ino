#include <WiFi.h>
#include <WebServer.h>
#include <esp_now.h>
#include <string.h>

struct SOSMessage
{
  char name[30];
  char phone[20];
  char type[20];
  char message[150];
};

SOSMessage sos;

uint8_t gatewayMAC[] = {
  0xD4, 0xE9, 0xF4,
  0x78, 0xE7, 0xD4
};

esp_now_peer_info_t peerInfo;

const char* ssid = "ESP32-Test";
const char* password = "12345678";

WebServer server(80);

void handleRoot() {

  String html = R"rawliteral(
<!DOCTYPE html>
<html>

<head>
<meta name="viewport" content="width=device-width, initial-scale=1">

<style>

body{
font-family:Arial;
text-align:center;
margin:20px;
background:#f2f2f2;
}

.container{
background:white;
padding:20px;
border-radius:10px;
max-width:400px;
margin:auto;
}

input,select,textarea{
width:95%;
padding:10px;
margin:8px 0;
}

button{
padding:12px 25px;
background:red;
color:white;
border:none;
border-radius:5px;
font-size:16px;
}

</style>

</head>

<body>

<div class="container">

<h2>Emergency Communication System</h2>

<form action="/submit" method="GET">

<input
type="text"
name="name"
placeholder="Your Name"
required>

<input
type="text"
name="phone"
placeholder="Phone Number"
required>

<select name="type">

<option>Medical</option>

<option>Fire</option>

<option>Accident</option>

<option>Crime</option>

<option>Other</option>

</select>

<textarea
name="message"
rows="4"
placeholder="Describe your emergency"></textarea>

<br>

<button type="submit">
SEND SOS
</button>

</form>

</div>

</body>
</html>
)rawliteral";

  server.send(200, "text/html", html);
}

void handleSubmit() {

  String name = server.arg("name");
  String phone = server.arg("phone");
  String type = server.arg("type");
  String message = server.arg("message");

Serial.println("SOS_START");

Serial.println(name);
Serial.println(phone);
Serial.println(type);
Serial.println(message);

Serial.println("SOS_END");

  // Copy form data into SOS structure
strncpy(sos.name, name.c_str(), sizeof(sos.name) - 1);
sos.name[sizeof(sos.name) - 1] = '\0';

strncpy(sos.phone, phone.c_str(), sizeof(sos.phone) - 1);
sos.phone[sizeof(sos.phone) - 1] = '\0';

strncpy(sos.type, type.c_str(), sizeof(sos.type) - 1);
sos.type[sizeof(sos.type) - 1] = '\0';

strncpy(sos.message, message.c_str(), sizeof(sos.message) - 1);
sos.message[sizeof(sos.message) - 1] = '\0';

// Send to Gateway
esp_err_t result = esp_now_send(
    gatewayMAC,
    (uint8_t *)&sos,
    sizeof(sos));

if (result == ESP_OK)
{
    Serial.println("SOS Sent Successfully");
}
else
{
    Serial.println("Failed to Send SOS");
}

  server.send(
      200,
      "text/html",
      "<h2>SOS Submitted Successfully!</h2>"
      "<p>You may close this page.</p>"
  );
}

void setup() {
  Serial.begin(115200);

  WiFi.mode(WIFI_AP_STA);

  WiFi.softAP(ssid, password);

  delay(500);

  // Initialize ESP-NOW
if (esp_now_init() != ESP_OK)
{
  Serial.println("ESP-NOW Init Failed");
  return;
}

// Configure Gateway as peer
memcpy(peerInfo.peer_addr, gatewayMAC, 6);
peerInfo.channel = WiFi.channel();
Serial.print("WiFi Channel: ");
Serial.println(WiFi.channel());
peerInfo.encrypt = false;

if (esp_now_add_peer(&peerInfo) != ESP_OK)
{
  Serial.println("Failed to Add Gateway Peer");
  return;
}

Serial.println("ESP-NOW Ready");

  Serial.print("Station MAC: ");
  Serial.println(WiFi.STA.macAddress());

  Serial.print("AP MAC: ");
  Serial.println(WiFi.softAPmacAddress());

  Serial.println("AP Started");
  Serial.println(WiFi.softAPIP());

  server.on("/", handleRoot);
  server.on("/submit", handleSubmit);

  server.begin();

  Serial.println("Server Started");
}

void loop() {
  server.handleClient();
}
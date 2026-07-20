#include <WiFi.h>
#include <WebServer.h>



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

  Serial.println("========== SOS RECEIVED ==========");
  Serial.print("Name: ");
  Serial.println(name);

  Serial.print("Phone: ");
  Serial.println(phone);

  Serial.print("Emergency: ");
  Serial.println(type);

  Serial.print("Message: ");
  Serial.println(message);

  Serial.println("=================================");

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

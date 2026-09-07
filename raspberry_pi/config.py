"""
ResQMesh - Raspberry Pi backend configuration
All tunable settings live here so nothing is hard-coded elsewhere.
"""

# ---------- Serial link to the ESP32 ----------
# Leave SERIAL_PORT as None to auto-detect /dev/ttyUSB* or /dev/ttyACM*.
# Set it explicitly (e.g. "/dev/ttyUSB0") if you have more than one device.
SERIAL_PORT = None
BAUD_RATE = 115200
SERIAL_TIMEOUT = 1.0        # seconds
RECONNECT_DELAY = 2.0       # seconds to wait before retrying a lost port

# ---------- Protocol markers (must match the ESP32 firmware exactly) ----------
PACKET_START = "SOS_START"
PACKET_END = "SOS_END"
PACKET_FIELDS = ["name", "phone", "type", "message"]

# ---------- Deterministic priority rules ----------
# This is rule-based classification, NOT machine learning.
# Describe it that way in the presentation and to the jury.
PRIORITY_RULES = {
    "Medical": "HIGH",
    "Fire": "HIGH",
    "Accident": "HIGH",
    "Crime": "HIGH",
    "Other": "MEDIUM",
}
DEFAULT_PRIORITY = "MEDIUM"

# ---------- Dashboard ----------
DASHBOARD_HOST = "0.0.0.0"   # 0.0.0.0 so other devices on the network can view
DASHBOARD_PORT = 5000
REFRESH_MS = 2000            # browser polling interval
MAX_HISTORY = 50             # incidents kept in memory and shown in the table

# ---------- Local persistent storage ----------
# SQLite: a single local file, no server, no network dependency.
# Incidents now survive a dashboard restart or a Pi reboot, while the
# "works with zero internet connectivity" claim remains completely true.
DB_PATH = "resqmesh.db"

# ---------- Logging ----------
LOG_FILE = "logs/resqmesh.log"
ENABLE_FILE_LOG = True

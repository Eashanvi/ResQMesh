"""
ResQMesh - SOS packet parser

Pure logic with no hardware dependency, so it can be unit tested on any
machine without an ESP32 attached. Feed it one line at a time; it returns a
complete record dict when a full SOS_START..SOS_END block has arrived, and
None otherwise.

Expected wire format from the ESP32:

    SOS_START
    <name>
    <phone>
    <type>
    <message>
    SOS_END
"""

from datetime import datetime

try:
    import config
except ImportError:  # allows importing from a parent directory too
    from raspberry_pi import config


class SOSParser:
    """Line-oriented state machine for SOS packets."""

    def __init__(self, priority_rules=None, default_priority=None):
        self.priority_rules = priority_rules or config.PRIORITY_RULES
        self.default_priority = default_priority or config.DEFAULT_PRIORITY
        self._capturing = False
        self._buffer = []
        self._next_id = 1
        self.malformed_count = 0

    def classify(self, emergency_type):
        """Deterministic rule-based priority. Not machine learning."""
        return self.priority_rules.get((emergency_type or "").strip(),
                                       self.default_priority)

    def reset(self):
        self._capturing = False
        self._buffer = []

    def feed(self, line):
        """
        Feed one decoded, stripped line.
        Returns a record dict when a packet completes, else None.
        """
        if line is None:
            return None
        line = line.strip()
        if not line:
            return None

        if line == config.PACKET_START:
            # A new start marker always restarts capture, so a truncated
            # packet can never corrupt the next good one.
            self._capturing = True
            self._buffer = []
            return None

        if line == config.PACKET_END:
            if not self._capturing:
                return None
            record = self._build_record(self._buffer)
            self.reset()
            return record

        if self._capturing:
            self._buffer.append(line)

        return None

    def _build_record(self, buf):
        if len(buf) < len(config.PACKET_FIELDS):
            self.malformed_count += 1
            return None

        name, phone, etype = buf[0], buf[1], buf[2]
        # Anything beyond the fourth line belongs to the message field.
        message = " ".join(buf[3:]).strip()
        etype = etype.strip()

        now = datetime.now()
        record = {
            "id": self._next_id,
            "name": name.strip(),
            "phone": phone.strip(),
            "type": etype,
            "message": message,
            "priority": self.classify(etype),
            "time": now.strftime("%H:%M:%S"),
            "date": now.strftime("%d %b %Y"),
            "timestamp": now.isoformat(timespec="seconds"),
            "status": "ACTIVE",
        }
        self._next_id += 1
        return record

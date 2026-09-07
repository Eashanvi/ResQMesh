"""
ResQMesh - serial receiver

Reads the ESP32 over USB serial in a background thread, parses SOS packets,
stores them in memory, and persists each one to a local SQLite file so
history survives a restart. Reconnects by itself if the ESP32 is unplugged
or reset, so the dashboard never has to be restarted mid-demo.

Can also be run on its own to check the link before starting the dashboard:

    python3 receiver.py
"""

import glob
import os
import threading
import time

import serial

import config
import db
from utils.serial_parser import SOSParser


def find_serial_port():
    """Return the first likely ESP32 serial port, or None."""
    if config.SERIAL_PORT:
        return config.SERIAL_PORT
    ports = sorted(glob.glob("/dev/ttyUSB*")) + sorted(glob.glob("/dev/ttyACM*"))
    return ports[0] if ports else None


class IncidentStore:
    """Thread-safe store of received incidents, newest first."""

    def __init__(self, max_history=None):
        self._lock = threading.Lock()
        self._items = []
        self.max_history = max_history or config.MAX_HISTORY
        self.total_received = 0
        self.last_packet_time = None

    def preload(self, records):
        """Load incidents that were saved before a restart. Called once,
        before the receiver thread starts."""
        with self._lock:
            self._items = list(records)[: self.max_history]
            self.total_received = len(self._items)

    def add(self, record):
        with self._lock:
            self._items.insert(0, record)
            del self._items[self.max_history:]
            self.total_received += 1
            self.last_packet_time = time.time()

    def snapshot(self):
        with self._lock:
            return list(self._items), self.total_received, self.last_packet_time

    def clear(self):
        with self._lock:
            self._items = []
            self.total_received = 0
            self.last_packet_time = None


class SerialReceiver(threading.Thread):
    """Background reader. Survives unplug/replug of the ESP32."""

    daemon = True

    def __init__(self, store, on_record=None, verbose=True, start_id=1):
        super().__init__(daemon=True)
        self.store = store
        self.on_record = on_record
        self.parser = SOSParser()
        self.parser._next_id = start_id  # continue numbering after a restart
        self.port = None
        self.connected = False
        self.verbose = verbose  # print raw non-packet lines too (boot banner etc.)
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def _log(self, text):
        line = "[receiver] {}".format(text)
        print(line, flush=True)
        if config.ENABLE_FILE_LOG:
            try:
                os.makedirs(os.path.dirname(config.LOG_FILE), exist_ok=True)
                with open(config.LOG_FILE, "a", encoding="utf-8") as fh:
                    fh.write("{} {}\n".format(
                        time.strftime("%Y-%m-%d %H:%M:%S"), text))
            except OSError:
                pass  # logging must never crash the receiver

    def run(self):
        while not self._stop.is_set():
            port = find_serial_port()
            if not port:
                self.connected = False
                self.port = None
                time.sleep(config.RECONNECT_DELAY)
                continue

            try:
                ser = serial.Serial(port, config.BAUD_RATE,
                                    timeout=config.SERIAL_TIMEOUT)
                self.port = port
                self.connected = True
                self.parser.reset()
                self._log("connected on {} at {} baud".format(
                    port, config.BAUD_RATE))
                self._log("waiting for data... (press the ESP32's EN/RST "
                          "button now if you want to confirm it is alive)")

                while not self._stop.is_set():
                    raw = ser.readline()
                    if not raw:
                        continue
                    line = raw.decode("utf-8", errors="ignore").strip()
                    if not line:
                        continue

                    record = self.parser.feed(line)
                    if record:
                        self.store.add(record)
                        db.insert_incident(record)
                        self._log("SOS #{} {} [{}] {}".format(
                            record["id"], record["type"],
                            record["priority"], record["name"]))
                        if self.on_record:
                            self.on_record(record)
                    elif self.verbose:
                        # Anything that is not part of a complete packet still
                        # gets shown, e.g. the boot banner and progress lines.
                        # This is what makes the board's activity visible.
                        print("[esp32] " + line, flush=True)

            except (serial.SerialException, OSError) as exc:
                self._log("link lost ({}), retrying".format(exc))
            finally:
                self.connected = False
                try:
                    ser.close()
                except Exception:
                    pass
            time.sleep(config.RECONNECT_DELAY)


if __name__ == "__main__":
    print("ResQMesh serial receiver - standalone link test")
    print("Waiting for SOS packets. Press Ctrl+C to stop.\n")
    db.init_db()
    store = IncidentStore()
    store.preload(db.load_recent())
    rx = SerialReceiver(store, start_id=db.next_id_after_load())
    rx.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nstopped")

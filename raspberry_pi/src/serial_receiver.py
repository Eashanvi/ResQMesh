import json
import serial
import time

SERIAL_PORT = "/dev/ttyUSB0"
BAUD_RATE = 115200

def read_sos(ser):
    packet = []

    while True:
        raw = ser.readline()
        if not raw:
            continue

        line = raw.decode("utf-8", errors="replace").strip()

        if not line:
            continue

        print(f"[RAW] {line}")

        if line == "SOS_START":
            packet = []
            continue

        if line == "SOS_END":
            if len(packet) >= 4:
                sos = {
                    "name": packet[0],
                    "phone": packet[1],
                    "type": packet[2],
                    "message": packet[3],
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                }

                return sos

            packet = []
            continue

        if packet is not None and len(packet) < 4:
            packet.append(line)


def main():
    print(f"Opening serial port: {SERIAL_PORT}")
    print(f"Baud rate: {BAUD_RATE}")

    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
            print("Serial connection established.")
            print("Waiting for SOS packets...\n")

            while True:
                sos = read_sos(ser)

                print("\n=== SOS RECEIVED ===")
                print(json.dumps(sos, indent=2))
                print("====================\n")

    except serial.SerialException as exc:
        print(f"Serial error: {exc}")
    except KeyboardInterrupt:
        print("\nReceiver stopped by user.")


if __name__ == "__main__":
    main()

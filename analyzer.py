import time
from datetime import datetime
import os
import csv
from saleae import automation
import grpc


#TODO: Replace Logic SaleAE serial with your serial. Also replace your channel.
#By default we use the orange channel (Channel 3)
LOGIC_SERIAL_ID  = '604E99E365809AA5'
CHANNEL_ID = 3 

def validate_frame(frame):
    if len(frame) != 9:
        return False, "Invalid length"
    if frame[0] != 0x59 or frame[1] != 0x59:
        return False, "Bad header"
    checksum = sum(frame[0:8]) & 0xFF
    if checksum != frame[8]:
        return False, f"Checksum mismatch: expected {checksum:02X}, got {frame[8]:02X}"
    return True, ""

def parse_csv_ascii(filepath):
    byte_stream = []
    with open(filepath, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data = row['data']
            if data == r'\0':
                byte_stream.append(0x00)
            elif data == r'\n':
                byte_stream.append(0x0A)
            elif data == r'\r':
                byte_stream.append(0x0D)
            elif len(data) == 1:
                byte_stream.append(ord(data))
            else:
                # Handle escaped or unknown characters if needed
                byte_stream.append(int(data, 16))
                pass
    return byte_stream

def parse_and_validate(byte_stream):
    i = 0
    while i <= len(byte_stream) - 9:
        if byte_stream[i] == 0x59 and byte_stream[i+1] == 0x59:
            frame = byte_stream[i:i+9]
            valid, reason = validate_frame(frame)
            if valid:
                dist = frame[2] + (frame[3] << 8)
                strength = frame[4] + (frame[5] << 8)
                temp_raw = frame[6] + (frame[7] << 8)
                temp = (temp_raw / 8.0) - 256
                print(f"[{i}] OK  - Distance: {dist} cm, Strength: {strength}, Temp: {temp:.1f} °C")
            else:
                dist = frame[2] + (frame[3] << 8)
                strength = frame[4] + (frame[5] << 8)
                temp_raw = frame[6] + (frame[7] << 8)
                temp = (temp_raw / 8.0) - 256
                print(f"[{i}] BAD  - Distance: {dist} cm, Strength: {strength}, Temp: {temp:.1f} °C")
                print(f"[{i}] BAD - {reason} - Frame: {[f'0x{b:02X}' for b in frame]}")
            i += 9
        else:
            print("Corrupted Frame" + str(byte_stream[i]))
            i += 1


def parse_bytes(byte_list):
    i = 0
    results = []
    while i <= len(byte_list) - 9:
        if byte_list[i] == 0x59 and byte_list[i+1] == 0x59:
            frame = byte_list[i:i+9]
            valid, reason = validate_frame(frame)
            if valid:
                dist = frame[2] + (frame[3] << 8)
                strength = frame[4] + (frame[5] << 8)
                temp_raw = frame[6] + (frame[7] << 8)
                temp = (temp_raw / 8.0) - 256
                print(f"[{i}] OK  - Distance: {dist} cm, Strength: {strength}, Temp: {temp:.1f} °C")
            else:
                print(f"[{i}] OK  - Distance: {dist} cm, Strength: {strength}, Temp: {temp:.1f} °C")
                print(f"[{i}] BAD - {reason} - Frame: {[f'0x{b:02X}' for b in frame]}")
            result.append((i, frame,valid, reason))
            i += 9
        else:
            i += 1
    results

def extract_bytes_from_csv(csv_path):
    with open(csv_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # skip header
        return [int(row[1], 16) for row in reader if row and row[1].startswith("0x")]

with automation.Manager.connect(port = 10430) as manager:
        device_configuration = automation.LogicDeviceConfiguration(
            enabled_digital_channels=[CHANNEL_ID],
            digital_sample_rate=10_000_000,
            digital_threshold_volts=1.2,
        )

        # Record 5 seconds of data before stopping the capture
        capture_configuration = automation.CaptureConfiguration( capture_mode=automation.TimedCaptureMode(duration_seconds=1.0))

        with manager.start_capture(device_id=LOGIC_SERIAL_ID, device_configuration=device_configuration, capture_configuration=capture_configuration) as capture:
            uart_analyzer = capture.add_analyzer('Async Serial', settings={
                'Input Channel': CHANNEL_ID,
                'Bit Rate (Bits/s)': 115200,
                'Bits per Frame': '8 Bits per Transfer (Standard)',
                'Stop Bits': '1 Stop Bit (Standard)',
                'Parity Bit': 'No Parity Bit (Standard)',
                'Significant Bit': 'Least Significant Bit Sent First (Standard)',
                'Signal inversion': 'Non Inverted (Standard)',
                'Mode' : 'Normal'
            })
            uart_export_config = automation.DataTableExportConfiguration(uart_analyzer, automation.RadixType.HEXADECIMAL)

            while(True):
                try:
                    capture.wait()
                    # Store output in a timestamped directory
                    output_dir = os.path.join(os.getcwd() + "/traces/", f'output-{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}')
                    os.makedirs(output_dir)
                    analyzer_export_filepath = os.path.join(output_dir,  "tfmini_uart.csv")
                    capture.export_data_table( filepath=analyzer_export_filepath, analyzers=[uart_export_config])
                    # Export raw digital data to a CSV file
                    capture.export_raw_data_csv(directory=output_dir, digital_channels=[CHANNEL_ID])
                    # Finally, save the capture to a file
                    capture_filepath = os.path.join(output_dir, 'example_capture.sal')
                    capture.save_capture(filepath=capture_filepath)

                    #Trace is ready, now you can play with it.
                    if os.path.exists(analyzer_export_filepath):
                        data = parse_csv_ascii(analyzer_export_filepath)
                        parse_and_validate(data)
                except grpc.RpcError as e:
                    print(f"gRPC error during capture: {e}")
                except KeyboardInterrupt:
                    print("Capture interrupted by user.")
                    exit(0)
                except Exception as e:
                    print(f"Unexpected error: {e}")

                time.sleep(1)

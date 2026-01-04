import time
from typing import Optional

import pandas as pd
import struct
import socket
import random
import platform

filename = "./group05_http_input.csv"
messages_df = pd.read_csv(filename)


def validate_csv_format(df: pd.DataFrame):
    expected_columns = ["app_protocol", "src_port", "dst_port", "message", "timestamp"]
    for col in expected_columns:
        if col not in df.columns:
            raise ValueError(f"Missing expected column: {col}")


messages_df['message'] = messages_df['message'].fillna('')  # Fill NaN messages with empty strings
validate_csv_format(messages_df)

IS_WINDOWS = (platform.system() == 'Windows')
try:
    from scapy.all import IP as SCAPY_IP, TCP as SCAPY_TCP, Raw as SCAPY_Raw, send as scapy_send, get_if_list

    HAVE_SCAPY = True
except Exception as e:
    HAVE_SCAPY = False
    SCAPY_IMPORT_ERR = e
    print("CRITICAL ERROR: Please install scapy -> pip install scapy")


def checksum(data: bytes) -> int:
    """Calculate Checksum for headers to ensure integrity"""
    if len(data) % 2:
        data += b'\0'
    res = sum(struct.unpack('!%dH' % (len(data) // 2), data))
    while res >> 16:
        res = (res & 0xFFFF) + (res >> 16)
    return ~res & 0xFFFF


def hexdump(data: bytes, width: int = 16):
    """Helper function to display the data"""
    for i in range(0, len(data), width):
        chunk = data[i:i + width]
        hex_bytes = ' '.join(f'{b:02x}' for b in chunk)
        ascii_bytes = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        print(f"{i:04x}  {hex_bytes:<{width * 3}}  {ascii_bytes}")


def build_ip_header(src_ip: str, dst_ip: str, payload_len: int, proto: int = socket.IPPROTO_TCP) -> bytes:
    """Manual construction of the IPv4 Header"""
    version_ihl = (4 << 4) + 5
    tos = 0
    total_length = 20 + payload_len
    identification = random.randint(0, 65535)
    flags_fragment = 0
    ttl = 64
    header_checksum = 0
    src = socket.inet_aton(src_ip)
    dst = socket.inet_aton(dst_ip)

    # Initial pack to calculate Checksum (checksum set to 0)
    ip_header = struct.pack('!BBHHHBBH4s4s',
                            version_ihl, tos, total_length, identification,
                            flags_fragment, ttl, proto, header_checksum,
                            src, dst)
    chksum = checksum(ip_header)

    # Final pack with the correct checksum
    ip_header = struct.pack('!BBHHHBBH4s4s',
                            version_ihl, tos, total_length, identification,
                            flags_fragment, ttl, proto, chksum,
                            src, dst)
    return ip_header


def build_tcp_header(src_ip: str, dst_ip: str, src_port: int, dst_port: int, payload: bytes = b'',
                     seq: Optional[int] = None, ack_seq: int = 0, flags: int = 0x02, window: int = 65535) -> bytes:
    """Manual construction of the TCP Header"""
    if seq is None:
        seq = random.randint(0, 0xFFFFFFFF)
    doff_reserved = (5 << 4)
    checksum_tcp = 0
    urg_ptr = 0
    tcp_header = struct.pack('!HHLLBBHHH',
                             src_port, dst_port, seq, ack_seq,
                             doff_reserved, flags, window,
                             checksum_tcp, urg_ptr)
    placeholder = 0
    protocol = socket.IPPROTO_TCP
    tcp_length = len(tcp_header) + len(payload)
    pseudo_header = struct.pack('!4s4sBBH',
                                socket.inet_aton(src_ip), socket.inet_aton(dst_ip),
                                placeholder, protocol, tcp_length)
    chksum = checksum(pseudo_header + tcp_header + payload)
    tcp_header = struct.pack('!HHLLBBHHH',
                             src_port, dst_port, seq, ack_seq,
                             doff_reserved, flags, window,
                             chksum, urg_ptr)
    return tcp_header


class RawTcpTransport:
    def __init__(self, src_ip: str, dst_ip: str, src_port: int, dst_port: int, iface: Optional[str] = None):
        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.src_port = src_port
        self.dst_port = dst_port
        self.iface = iface
        self.windows_fallback = IS_WINDOWS
        if not self.windows_fallback:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
        else:
            if not HAVE_SCAPY:
                raise RuntimeError(
                    f"Windows detected but Scapy is not available: {SCAPY_IMPORT_ERR}.\n"
                    "Install with: pip install scapy. Ensure Npcap is installed with loopback support."
                )

    def encapsulate(self, data: bytes, flags: int = 0x02) -> bytes:
        tcp = build_tcp_header(self.src_ip, self.dst_ip, self.src_port, self.dst_port, data, flags=flags)
        ip = build_ip_header(self.src_ip, self.dst_ip, len(tcp) + len(data))
        return ip + tcp + data

    def send(self, data: bytes, flags: int = 0x02):
        if not self.windows_fallback:
            pkt = self.encapsulate(data, flags=flags)
            self.sock.sendto(pkt, (self.dst_ip, 0))
        else:
            scapy_pkt = SCAPY_IP(src=self.src_ip, dst=self.dst_ip) / SCAPY_TCP(sport=self.src_port, dport=self.dst_port,
                                                                               flags=flags) / SCAPY_Raw(data)
            chosen_iface = self.iface
            if chosen_iface is None and self.dst_ip in ("127.0.0.1", "::1"):
                chosen_iface = "Npcap Loopback Adapter"
            scapy_send(scapy_pkt, verbose=False, iface=chosen_iface)


# find interface name for Windows
if IS_WINDOWS and HAVE_SCAPY:
    try:
        print('\n'.join(get_if_list()))
    except Exception as e:
        print('Could not list interfaces:', e)

# Preview packet structure
src_ip = '127.0.0.1'
dst_ip = '127.0.0.1'
src_port = random.randint(1024, 65535)
dst_port = 12345
payload = b'Hello Packet (preview)'
pkt_preview = build_ip_header(src_ip, dst_ip, 20 + len(payload)) + build_tcp_header(src_ip, dst_ip, src_port, dst_port,
                                                                                    payload) + payload
hexdump(pkt_preview)

iface = "Npcap Loopback Adapter"
transport = RawTcpTransport(src_ip, dst_ip, src_port, dst_port, iface=iface)


def demo_send(num_packets: int = 3, delay_sec: float = 1.0, flags: int = 0x02):
    for i in range(num_packets):
        payload = f'Hello Packet {i}'.encode()
        transport.send(payload, flags=flags)
        time.sleep(delay_sec)


demo_send(num_packets=3, delay_sec=1.0, flags=0x02)
# demo_send(num_packets=3, flags=0x18)


# Send messages from CSV file
for index, row in messages_df.iterrows():
    # Extract message details from the DataFrame row
    message = row['message']
    message = f"test message {index}" if not message else message
    # Send the message using the RawTcpTransport class
    # (You may need to adjust flags and other parameters as needed)

    if 'dst_port' in row:
        transport.dst_port = int(row['dst_port'])
    if 'src_port' in row:
        transport.src_port = int(row['src_port'])

    transport.send(message.encode(), flags=0x18)  # PSH+ACK
    time.sleep(0.5)

print("Done.")
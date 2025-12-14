# Practical Networking: From Zero to Hero

A hands-on, practical guide to understanding networking from the ground up. This repository focuses on **Layers 2–4** of the OSI model, TCP/UDP protocols, and application data flow through **runnable, interactive demos** rather than pure theory.

## 🎯 Goal

Enable you to:
- **See packets live** as they move through the network
- **Debug TCP/UDP issues** with confidence
- **Understand how data really moves** on the wire
- Build strong practical networking skills through experimentation

## 📚 Learning Path

Follow this path to build your networking knowledge step by step:

### Prerequisites
- Linux environment (Ubuntu/Debian recommended)
- Python 3.7+
- Basic command line knowledge

### Setup

```bash
# Install required dependencies
sudo apt-get update
sudo apt-get install -y python3 python3-pip tcpdump wireshark-common

# Install Python packages
pip3 install scapy netifaces

# Note: Many scripts require root/sudo to capture/send raw packets
```

### 1. Layer 2 - Data Link Layer (Ethernet & ARP)
**Start here if you're new to networking**

- **[`layer2/01_ethernet_basics.py`](layer2/01_ethernet_basics.py)** - Understanding Ethernet frames and MAC addresses
- **[`layer2/02_arp_demo.py`](layer2/02_arp_demo.py)** - See ARP in action (IP to MAC address resolution)
- **[`layer2/03_arp_spoof_demo.py`](layer2/03_arp_spoof_demo.py)** - Understand ARP cache poisoning (educational)

**What you'll learn:**
- MAC addresses and how they work
- Ethernet frame structure
- ARP protocol and its vulnerabilities
- How switches forward frames

### 2. Layer 3 - Network Layer (IP & ICMP)
**Build on Layer 2 knowledge**

- **[`layer3/01_ip_packet_anatomy.py`](layer3/01_ip_packet_anatomy.py)** - Deep dive into IP packet headers
- **[`layer3/02_icmp_ping.py`](layer3/02_icmp_ping.py)** - Build your own ping utility
- **[`layer3/03_traceroute.py`](layer3/03_traceroute.py)** - Implement traceroute to understand routing
- **[`layer3/04_ip_fragmentation.py`](layer3/04_ip_fragmentation.py)** - See how large packets are fragmented

**What you'll learn:**
- IP addressing and subnetting
- Routing fundamentals
- ICMP protocol
- TTL and packet fragmentation

### 3. Layer 4 - Transport Layer (TCP & UDP)
**Core of reliable communication**

- **[`layer4/01_udp_basics.py`](layer4/01_udp_basics.py)** - Simple UDP client/server with packet inspection
- **[`layer4/02_tcp_handshake.py`](layer4/02_tcp_handshake.py)** - Visualize the 3-way handshake
- **[`layer4/03_tcp_connection.py`](layer4/03_tcp_connection.py)** - Complete TCP communication demo
- **[`layer4/04_tcp_states.py`](layer4/04_tcp_states.py)** - Monitor TCP state transitions
- **[`layer4/05_tcp_retransmission.py`](layer4/05_tcp_retransmission.py)** - See TCP reliability in action

**What you'll learn:**
- UDP vs TCP trade-offs
- TCP 3-way handshake and 4-way termination
- TCP sequence and acknowledgment numbers
- Flow control and retransmission
- Port numbers and sockets

### 4. Application Layer Data Flow
**Putting it all together**

- **[`application/01_http_from_scratch.py`](application/01_http_from_scratch.py)** - HTTP request/response at the TCP level
- **[`application/02_dns_query.py`](application/02_dns_query.py)** - Build a DNS query tool
- **[`application/03_packet_capture_analyzer.py`](application/03_packet_capture_analyzer.py)** - Capture and analyze real traffic

**What you'll learn:**
- How applications use TCP/UDP
- Protocol layering in practice
- Reading packet captures
- End-to-end data flow

### 5. Packet Visualization Tools
**Tools to help you see what's happening**

- **[`tools/packet_sniffer.py`](tools/packet_sniffer.py)** - Live packet capture with filtering
- **[`tools/packet_forge.py`](tools/packet_forge.py)** - Craft custom packets
- **[`tools/traffic_analyzer.py`](tools/traffic_analyzer.py)** - Analyze captured traffic patterns

## 🔬 How to Use These Demos

Each script follows this pattern:

1. **Read the header comments** - Understand what the script does
2. **Run the script** - See it in action (usually requires `sudo`)
3. **Modify parameters** - Experiment with different values
4. **Observe the changes** - See how your modifications affect behavior
5. **Read the inline explanations** - Learn as you go

### Example Workflow

```bash
# 1. Read about Ethernet
cat layer2/01_ethernet_basics.py

# 2. Run the demo
sudo python3 layer2/01_ethernet_basics.py

# 3. Open it in an editor and modify values
nano layer2/01_ethernet_basics.py

# 4. Run again and observe differences
sudo python3 layer2/01_ethernet_basics.py
```

## 🛡️ Important Notes

- **Root/sudo required**: Most scripts need elevated privileges to capture/send raw packets
- **Educational purposes**: Some demos show attack techniques (like ARP spoofing) - use only in controlled environments you own
- **Network impact**: Some scripts generate network traffic - be mindful on shared networks
- **Firewall rules**: Your firewall may block some experiments - adjust as needed

## 🤝 Contributing

Found a bug? Have an idea for a new demo? Contributions are welcome!

## 📖 Additional Resources

- [Scapy Documentation](https://scapy.readthedocs.io/)
- [TCP/IP Illustrated by Richard Stevens](https://www.amazon.com/TCP-Illustrated-Vol-Addison-Wesley-Professional/dp/0201633469)
- [Wireshark User Guide](https://www.wireshark.org/docs/wsug_html_chunked/)

## 📝 License

This project is open source and available for educational purposes.

---

**Start your journey**: Begin with `layer2/01_ethernet_basics.py` and work your way up the stack!
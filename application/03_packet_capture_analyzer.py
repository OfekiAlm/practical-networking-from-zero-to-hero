#!/usr/bin/env python3
"""
Application Demo: Packet Capture Analyzer
==========================================

This script analyzes captured packet files.
You'll learn:
- Reading PCAP files
- Analyzing traffic patterns
- Protocol distribution
- Connection analysis

Run with: python3 03_packet_capture_analyzer.py <file.pcap>

EXPERIMENT IDEAS:
1. Analyze different capture files
2. Extract specific protocols
3. Generate traffic statistics
"""

from scapy.all import rdpcap, IP, TCP, UDP, ICMP, ARP, DNS
import sys
from collections import defaultdict, Counter

def print_section(title):
    """Pretty print section headers"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def analyze_pcap(filename):
    """Analyze a PCAP file"""
    print_section(f"Analyzing: {filename}")
    
    try:
        print("\nReading packets...")
        packets = rdpcap(filename)
        print(f"✓ Loaded {len(packets)} packets")
        
        return packets
    except FileNotFoundError:
        print(f"✗ File not found: {filename}")
        return None
    except Exception as e:
        print(f"✗ Error reading file: {e}")
        return None

def basic_statistics(packets):
    """Generate basic statistics"""
    print_section("Basic Statistics")
    
    if not packets:
        return
    
    # Time range
    first_time = packets[0].time
    last_time = packets[-1].time
    duration = last_time - first_time
    
    # Size statistics
    total_bytes = sum(len(p) for p in packets)
    avg_size = total_bytes / len(packets) if packets else 0
    
    print(f"\nCapture Duration: {duration:.2f} seconds")
    print(f"Total Packets: {len(packets)}")
    print(f"Total Bytes: {total_bytes:,} ({total_bytes/1024/1024:.2f} MB)")
    print(f"Average Packet Size: {avg_size:.1f} bytes")
    print(f"Packets per Second: {len(packets)/duration:.1f}" if duration > 0 else "N/A")
    print(f"Throughput: {(total_bytes*8/duration/1000000):.2f} Mbps" if duration > 0 else "N/A")

def protocol_distribution(packets):
    """Analyze protocol distribution"""
    print_section("Protocol Distribution")
    
    if not packets:
        return
    
    protocols = Counter()
    protocol_bytes = defaultdict(int)
    
    for packet in packets:
        if packet.haslayer(TCP):
            protocols['TCP'] += 1
            protocol_bytes['TCP'] += len(packet)
        elif packet.haslayer(UDP):
            protocols['UDP'] += 1
            protocol_bytes['UDP'] += len(packet)
        elif packet.haslayer(ICMP):
            protocols['ICMP'] += 1
            protocol_bytes['ICMP'] += len(packet)
        elif packet.haslayer(ARP):
            protocols['ARP'] += 1
            protocol_bytes['ARP'] += len(packet)
        else:
            protocols['Other'] += 1
            protocol_bytes['Other'] += len(packet)
    
    print(f"\n{'Protocol':<15} {'Packets':<15} {'Percentage':<15} {'Bytes'}")
    print("-" * 70)
    
    for proto in ['TCP', 'UDP', 'ICMP', 'ARP', 'Other']:
        if protocols[proto] > 0:
            pct = (protocols[proto] / len(packets)) * 100
            print(f"{proto:<15} {protocols[proto]:<15} {pct:>6.2f}%        {protocol_bytes[proto]:,}")

def analyze_ip_addresses(packets):
    """Analyze IP address communication"""
    print_section("IP Address Communication")
    
    if not packets:
        return
    
    sources = Counter()
    destinations = Counter()
    pairs = Counter()
    
    for packet in packets:
        if packet.haslayer(IP):
            src = packet[IP].src
            dst = packet[IP].dst
            sources[src] += 1
            destinations[dst] += 1
            pairs[(src, dst)] += 1
    
    print("\nTop 10 Source IPs:")
    print(f"{'IP Address':<20} {'Packets'}")
    print("-" * 35)
    for ip, count in sources.most_common(10):
        print(f"{ip:<20} {count}")
    
    print("\n\nTop 10 Destination IPs:")
    print(f"{'IP Address':<20} {'Packets'}")
    print("-" * 35)
    for ip, count in destinations.most_common(10):
        print(f"{ip:<20} {count}")
    
    print("\n\nTop 10 IP Pairs (Conversations):")
    print(f"{'Source':<20} {'Destination':<20} {'Packets'}")
    print("-" * 65)
    for (src, dst), count in pairs.most_common(10):
        print(f"{src:<20} {dst:<20} {count}")

def analyze_ports(packets):
    """Analyze port usage"""
    print_section("Port Analysis")
    
    if not packets:
        return
    
    tcp_ports = Counter()
    udp_ports = Counter()
    
    for packet in packets:
        if packet.haslayer(TCP):
            tcp_ports[packet[TCP].dport] += 1
            tcp_ports[packet[TCP].sport] += 1
        elif packet.haslayer(UDP):
            udp_ports[packet[UDP].dport] += 1
            udp_ports[packet[UDP].sport] += 1
    
    print("\nTop 10 TCP Ports:")
    print(f"{'Port':<10} {'Packets':<15} {'Common Service'}")
    print("-" * 50)
    port_services = {
        80: 'HTTP', 443: 'HTTPS', 22: 'SSH', 21: 'FTP',
        25: 'SMTP', 53: 'DNS', 110: 'POP3', 143: 'IMAP',
        3306: 'MySQL', 5432: 'PostgreSQL', 6379: 'Redis',
        8080: 'HTTP-Alt', 3389: 'RDP'
    }
    for port, count in tcp_ports.most_common(10):
        service = port_services.get(port, '')
        print(f"{port:<10} {count:<15} {service}")
    
    print("\n\nTop 10 UDP Ports:")
    print(f"{'Port':<10} {'Packets':<15} {'Common Service'}")
    print("-" * 50)
    udp_services = {
        53: 'DNS', 67: 'DHCP-Server', 68: 'DHCP-Client',
        123: 'NTP', 161: 'SNMP', 514: 'Syslog', 5353: 'mDNS'
    }
    for port, count in udp_ports.most_common(10):
        service = udp_services.get(port, '')
        print(f"{port:<10} {count:<15} {service}")

def analyze_tcp_flags(packets):
    """Analyze TCP flags"""
    print_section("TCP Flag Analysis")
    
    if not packets:
        return
    
    flag_counts = Counter()
    
    for packet in packets:
        if packet.haslayer(TCP):
            flags = packet[TCP].flags
            flag_str = str(flags)
            flag_counts[flag_str] += 1
    
    print(f"\n{'Flags':<10} {'Count':<15} {'Description'}")
    print("-" * 55)
    
    flag_desc = {
        'S': 'SYN (Connection request)',
        'SA': 'SYN-ACK (Connection response)',
        'A': 'ACK (Acknowledgment)',
        'PA': 'PSH-ACK (Data push)',
        'F': 'FIN (Close connection)',
        'FA': 'FIN-ACK (Close + ack)',
        'R': 'RST (Reset connection)',
        'RA': 'RST-ACK (Reset + ack)',
    }
    
    for flags, count in flag_counts.most_common():
        desc = flag_desc.get(flags, '')
        print(f"{flags:<10} {count:<15} {desc}")

def analyze_dns(packets):
    """Analyze DNS queries"""
    print_section("DNS Analysis")
    
    if not packets:
        return
    
    queries = []
    responses = []
    
    for packet in packets:
        if packet.haslayer(DNS):
            dns = packet[DNS]
            if dns.qr == 0:  # Query
                if dns.qd:
                    queries.append(dns.qd.qname.decode())
            else:  # Response
                responses.append(dns)
    
    print(f"\nTotal DNS Queries: {len(queries)}")
    print(f"Total DNS Responses: {len(responses)}")
    
    if queries:
        print("\nTop 10 Queried Domains:")
        query_counter = Counter(queries)
        print(f"{'Domain':<40} {'Count'}")
        print("-" * 55)
        for domain, count in query_counter.most_common(10):
            print(f"{domain:<40} {count}")

def analyze_http(packets):
    """Analyze HTTP traffic"""
    print_section("HTTP Analysis")
    
    if not packets:
        return
    
    http_packets = 0
    methods = Counter()
    
    for packet in packets:
        if packet.haslayer(TCP) and packet.haslayer('Raw'):
            try:
                payload = bytes(packet['Raw'].load)
                payload_str = payload.decode('utf-8', errors='ignore')
                
                # Check for HTTP methods
                for method in ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS']:
                    if payload_str.startswith(method):
                        http_packets += 1
                        methods[method] += 1
                        break
            except:
                pass
    
    print(f"\nHTTP Packets: {http_packets}")
    
    if methods:
        print("\nHTTP Methods:")
        print(f"{'Method':<15} {'Count'}")
        print("-" * 30)
        for method, count in methods.most_common():
            print(f"{method:<15} {count}")

def generate_summary(packets):
    """Generate overall summary"""
    print_section("Summary")
    
    if not packets:
        return
    
    tcp_count = sum(1 for p in packets if p.haslayer(TCP))
    udp_count = sum(1 for p in packets if p.haslayer(UDP))
    icmp_count = sum(1 for p in packets if p.haslayer(ICMP))
    
    unique_ips = set()
    for p in packets:
        if p.haslayer(IP):
            unique_ips.add(p[IP].src)
            unique_ips.add(p[IP].dst)
    
    print(f"""
Capture Summary:
- Total Packets: {len(packets)}
- TCP Packets: {tcp_count} ({tcp_count/len(packets)*100:.1f}%)
- UDP Packets: {udp_count} ({udp_count/len(packets)*100:.1f}%)
- ICMP Packets: {icmp_count} ({icmp_count/len(packets)*100:.1f}%)
- Unique IP Addresses: {len(unique_ips)}
    """)

def create_sample_capture():
    """Instructions for creating a sample capture"""
    print_section("Creating Sample Captures")
    print("""
To create packet captures for analysis:

1. Using tcpdump:
   sudo tcpdump -i any -w capture.pcap -c 1000
   (Capture 1000 packets to capture.pcap)

2. Capture specific traffic:
   sudo tcpdump -i any -w http.pcap port 80
   (Capture HTTP traffic)

3. Capture for duration:
   sudo tcpdump -i any -w timed.pcap -G 60 -W 1
   (Capture for 60 seconds)

4. While browsing:
   sudo tcpdump -i any -w browsing.pcap &
   (Start capture)
   firefox http://example.com
   (Browse some sites)
   sudo killall tcpdump
   (Stop capture)

Then analyze:
   python3 03_packet_capture_analyzer.py capture.pcap
    """)

def main():
    """Main function"""
    print("\n" + "="*60)
    print("  PACKET CAPTURE ANALYZER")
    print("="*60)
    
    if len(sys.argv) < 2:
        print("\nUsage: python3 03_packet_capture_analyzer.py <file.pcap>")
        create_sample_capture()
        return
    
    filename = sys.argv[1]
    packets = analyze_pcap(filename)
    
    if packets:
        basic_statistics(packets)
        protocol_distribution(packets)
        analyze_ip_addresses(packets)
        analyze_ports(packets)
        analyze_tcp_flags(packets)
        analyze_dns(packets)
        analyze_http(packets)
        generate_summary(packets)
        
        print_section("Next Steps")
        print("""
Additional analysis ideas:
1. Open in Wireshark for visual analysis
2. Filter specific conversations
3. Export objects (files transferred)
4. Analyze timing and latency
5. Look for anomalies or attacks
        """)
    
    print("\n✅ Analysis complete!\n")

if __name__ == "__main__":
    main()

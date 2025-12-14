#!/usr/bin/env python3
"""
Traffic Analyzer Tool
=====================

Real-time traffic analysis and statistics.
You'll learn:
- Live traffic monitoring
- Protocol statistics
- Bandwidth analysis

Run with: sudo python3 traffic_analyzer.py

EXPERIMENT IDEAS:
1. Monitor different interfaces
2. Analyze peak traffic times
3. Identify bandwidth hogs
"""

from scapy.all import sniff, IP, TCP, UDP
import time
import threading
from collections import defaultdict
import sys

class TrafficAnalyzer:
    """Real-time traffic analyzer"""
    
    def __init__(self, interface=None):
        self.interface = interface
        self.start_time = time.time()
        self.packet_count = 0
        self.byte_count = 0
        self.protocol_count = defaultdict(int)
        self.protocol_bytes = defaultdict(int)
        self.ip_traffic = defaultdict(int)
        self.port_traffic = defaultdict(int)
        self.running = True
        
    def packet_handler(self, packet):
        """Handle each captured packet"""
        self.packet_count += 1
        self.byte_count += len(packet)
        
        # Protocol analysis
        if packet.haslayer(TCP):
            self.protocol_count['TCP'] += 1
            self.protocol_bytes['TCP'] += len(packet)
            
            # Port tracking
            if packet[TCP].dport:
                self.port_traffic[packet[TCP].dport] += 1
            if packet[TCP].sport:
                self.port_traffic[packet[TCP].sport] += 1
                
        elif packet.haslayer(UDP):
            self.protocol_count['UDP'] += 1
            self.protocol_bytes['UDP'] += len(packet)
            
            # Port tracking
            if packet[UDP].dport:
                self.port_traffic[packet[UDP].dport] += 1
            if packet[UDP].sport:
                self.port_traffic[packet[UDP].sport] += 1
        else:
            self.protocol_count['Other'] += 1
            self.protocol_bytes['Other'] += len(packet)
        
        # IP tracking
        if packet.haslayer(IP):
            self.ip_traffic[packet[IP].src] += 1
            self.ip_traffic[packet[IP].dst] += 1
    
    def get_stats(self):
        """Get current statistics"""
        elapsed = time.time() - self.start_time
        pps = self.packet_count / elapsed if elapsed > 0 else 0
        bps = (self.byte_count * 8) / elapsed if elapsed > 0 else 0
        
        return {
            'elapsed': elapsed,
            'packets': self.packet_count,
            'bytes': self.byte_count,
            'pps': pps,
            'bps': bps,
            'mbps': bps / 1000000,
        }
    
    def display_stats(self):
        """Display statistics"""
        while self.running:
            time.sleep(2)
            self.print_stats()
    
    def print_stats(self):
        """Print current statistics"""
        # Clear screen (ANSI escape codes)
        print("\033[2J\033[H")
        
        stats = self.get_stats()
        
        print("="*70)
        print("  REAL-TIME TRAFFIC ANALYZER")
        print("="*70)
        
        print(f"\nElapsed Time: {stats['elapsed']:.1f} seconds")
        print(f"Total Packets: {stats['packets']:,}")
        print(f"Total Bytes: {stats['bytes']:,} ({stats['bytes']/1024/1024:.2f} MB)")
        print(f"Packets/sec: {stats['pps']:.1f}")
        print(f"Throughput: {stats['mbps']:.2f} Mbps")
        
        # Protocol distribution
        print("\n" + "-"*70)
        print("Protocol Distribution:")
        print("-"*70)
        print(f"{'Protocol':<15} {'Packets':<15} {'%':<10} {'Bytes'}")
        print("-"*70)
        
        for proto in ['TCP', 'UDP', 'Other']:
            if self.protocol_count[proto] > 0:
                pct = (self.protocol_count[proto] / self.packet_count) * 100
                print(f"{proto:<15} {self.protocol_count[proto]:<15} "
                      f"{pct:>5.1f}%     {self.protocol_bytes[proto]:,}")
        
        # Top IPs
        print("\n" + "-"*70)
        print("Top 5 IP Addresses:")
        print("-"*70)
        print(f"{'IP Address':<20} {'Packets'}")
        print("-"*70)
        
        for ip, count in sorted(self.ip_traffic.items(), 
                               key=lambda x: x[1], reverse=True)[:5]:
            print(f"{ip:<20} {count}")
        
        # Top Ports
        print("\n" + "-"*70)
        print("Top 5 Ports:")
        print("-"*70)
        print(f"{'Port':<10} {'Packets':<15} {'Service'}")
        print("-"*70)
        
        port_services = {
            80: 'HTTP', 443: 'HTTPS', 22: 'SSH', 53: 'DNS',
            21: 'FTP', 25: 'SMTP', 110: 'POP3', 143: 'IMAP',
        }
        
        for port, count in sorted(self.port_traffic.items(), 
                                 key=lambda x: x[1], reverse=True)[:5]:
            service = port_services.get(port, '')
            print(f"{port:<10} {count:<15} {service}")
        
        print("\n" + "="*70)
        print("Press Ctrl+C to stop")
        print("="*70)
    
    def start(self):
        """Start traffic analysis"""
        print("Starting traffic analyzer...")
        print(f"Interface: {self.interface or 'default'}")
        print("Capturing packets...\n")
        
        # Start display thread
        display_thread = threading.Thread(target=self.display_stats)
        display_thread.daemon = True
        display_thread.start()
        
        try:
            sniff(iface=self.interface, prn=self.packet_handler, store=False)
        except KeyboardInterrupt:
            print("\n\nStopping analyzer...")
            self.running = False
            time.sleep(1)
            self.print_final_report()
    
    def print_final_report(self):
        """Print final report"""
        print("\n" + "="*70)
        print("  FINAL REPORT")
        print("="*70)
        
        stats = self.get_stats()
        
        print(f"\nTotal Duration: {stats['elapsed']:.1f} seconds")
        print(f"Total Packets: {stats['packets']:,}")
        print(f"Total Data: {stats['bytes']:,} bytes ({stats['bytes']/1024/1024:.2f} MB)")
        print(f"Average PPS: {stats['pps']:.1f}")
        print(f"Average Throughput: {stats['mbps']:.2f} Mbps")
        
        print("\nProtocol Summary:")
        for proto in ['TCP', 'UDP', 'Other']:
            if self.protocol_count[proto] > 0:
                pct = (self.protocol_count[proto] / self.packet_count) * 100
                print(f"  {proto}: {self.protocol_count[proto]:,} packets ({pct:.1f}%)")
        
        print(f"\nUnique IPs: {len(self.ip_traffic)}")
        print(f"Unique Ports: {len(self.port_traffic)}")

def print_section(title):
    """Pretty print section headers"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def show_help():
    """Show help information"""
    print_section("Traffic Analyzer Help")
    print("""
This tool provides real-time network traffic analysis.

Usage:
    sudo python3 traffic_analyzer.py [interface]

Examples:
    sudo python3 traffic_analyzer.py           # Default interface
    sudo python3 traffic_analyzer.py eth0      # Specific interface
    sudo python3 traffic_analyzer.py wlan0     # WiFi interface

Features:
✓ Real-time packet statistics
✓ Protocol distribution (TCP/UDP)
✓ Top talkers (IP addresses)
✓ Top ports (services)
✓ Bandwidth monitoring
✓ Live updates every 2 seconds

Metrics Displayed:
- Packets per second (PPS)
- Bits per second (bps/Mbps)
- Protocol breakdown
- Most active IPs
- Most used ports

Tips:
- Run on quiet network first to understand baseline
- Monitor during specific activities (browsing, streaming)
- Compare different interfaces
- Use with packet_sniffer.py for detailed analysis

Press Ctrl+C to stop and see final report.
    """)

def main():
    """Main function"""
    
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
        show_help()
        return
    
    interface = sys.argv[1] if len(sys.argv) > 1 else None
    
    print("\n" + "="*70)
    print("  TRAFFIC ANALYZER")
    print("="*70)
    print("\nReal-time network traffic monitoring and analysis")
    
    try:
        analyzer = TrafficAnalyzer(interface)
        analyzer.start()
    except PermissionError:
        print("\n⚠️  Traffic analysis requires root privileges")
        print("Run with: sudo python3 traffic_analyzer.py")
    except KeyboardInterrupt:
        print("\n\nExiting...")

if __name__ == "__main__":
    main()

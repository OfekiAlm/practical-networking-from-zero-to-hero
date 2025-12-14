#!/usr/bin/env python3
"""
Application Demo: DNS Query from Scratch
=========================================

This script implements DNS queries manually.
You'll learn:
- How DNS works at packet level
- DNS message format
- Building DNS queries with Scapy

Run with: python3 02_dns_query.py [hostname]

EXPERIMENT IDEAS:
1. Query different record types (A, AAAA, MX, NS)
2. Use different DNS servers
3. Compare with system resolver
"""

from scapy.all import IP, UDP, DNS, DNSQR, DNSRR, sr1
import sys

def print_section(title):
    """Pretty print section headers"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def explain_dns():
    """Explain DNS fundamentals"""
    print_section("DNS (Domain Name System)")
    print("""
DNS Purpose:
- Translate hostnames to IP addresses
- example.com → 93.184.216.34
- Distributed, hierarchical database

DNS Hierarchy:
  Root (.)
    ↓
  Top-Level Domain (.com, .org, .net)
    ↓
  Second-Level Domain (example.com)
    ↓
  Subdomain (www.example.com)

DNS Query Process:
1. Application needs IP for "www.example.com"
2. Check local cache
3. Query DNS resolver (usually ISP or 8.8.8.8)
4. Resolver queries root servers
5. Root refers to .com servers
6. .com refers to example.com servers
7. example.com returns IP address
8. Resolver caches and returns to client

DNS Uses UDP (typically):
- Port 53
- Fast, lightweight
- Query fits in one packet
- Falls back to TCP for large responses

DNS Message Format:
  +------------------+
  |     Header       |  12 bytes
  +------------------+
  |    Question      |  Variable (what we're asking)
  +------------------+
  |     Answer       |  Variable (response)
  +------------------+
  |    Authority     |  Variable (authoritative servers)
  +------------------+
  |   Additional     |  Variable (extra info)
  +------------------+
    """)

def show_dns_record_types():
    """Show common DNS record types"""
    print_section("DNS Record Types")
    
    records = [
        ("A", "IPv4 address", "example.com → 93.184.216.34"),
        ("AAAA", "IPv6 address", "example.com → 2606:2800:220:1:..."),
        ("CNAME", "Canonical name (alias)", "www → example.com"),
        ("MX", "Mail exchange", "example.com → mail.example.com"),
        ("NS", "Name server", "example.com → ns1.example.com"),
        ("TXT", "Text records", "SPF, DKIM, verification"),
        ("PTR", "Reverse lookup", "1.2.3.4 → host.example.com"),
        ("SOA", "Start of authority", "Zone information"),
        ("SRV", "Service", "Service location"),
    ]
    
    print(f"\n{'Type':<8} {'Description':<25} {'Example'}")
    print("-" * 70)
    for rtype, desc, example in records:
        print(f"{rtype:<8} {desc:<25} {example}")

def build_dns_query(domain, qtype="A"):
    """Build a DNS query packet"""
    print_section(f"Building DNS Query for {domain} ({qtype})")
    
    # Create DNS query
    dns_query = IP(dst="8.8.8.8")/UDP(dport=53)/DNS(rd=1, qd=DNSQR(qname=domain, qtype=qtype))
    
    print("\nComplete DNS Query Packet:")
    print(dns_query.show(dump=True))
    
    print("\n\nPacket Breakdown:")
    print("IP Layer:")
    print(f"  Destination: {dns_query[IP].dst} (Google DNS)")
    
    print("\nUDP Layer:")
    print(f"  Destination Port: {dns_query[UDP].dport} (53 = DNS)")
    print(f"  Source Port: {dns_query[UDP].sport} (random)")
    
    print("\nDNS Layer:")
    dns = dns_query[DNS]
    print(f"  Transaction ID: {dns.id}")
    print(f"  Flags: {hex(dns.flags)}")
    print(f"    - QR: 0 (Query)")
    print(f"    - RD: {dns.rd} (Recursion Desired)")
    print(f"  Question Count: {dns.qdcount}")
    
    print("\nDNS Question:")
    print(f"  Name: {dns.qd.qname.decode()}")
    print(f"  Type: {qtype}")
    print(f"  Class: IN (Internet)")
    
    return dns_query

def send_dns_query(domain, qtype="A", dns_server="8.8.8.8"):
    """Send DNS query and parse response"""
    print_section(f"Querying {domain} ({qtype}) via {dns_server}")
    
    # Build query
    query = IP(dst=dns_server)/UDP(dport=53)/DNS(rd=1, qd=DNSQR(qname=domain, qtype=qtype))
    
    print(f"\n→ Sending query to {dns_server}...")
    
    # Send and receive
    response = sr1(query, verbose=0, timeout=5)
    
    if response is None:
        print("✗ No response (timeout)")
        return
    
    if not response.haslayer(DNS):
        print("✗ Response is not DNS")
        return
    
    # Parse response
    dns_resp = response[DNS]
    
    print(f"✓ Received response!")
    print(f"\nDNS Response:")
    print(f"  Transaction ID: {dns_resp.id}")
    print(f"  Flags: {hex(dns_resp.flags)}")
    print(f"    - QR: 1 (Response)")
    print(f"    - AA: {dns_resp.aa} (Authoritative Answer)")
    print(f"    - RD: {dns_resp.rd} (Recursion Desired)")
    print(f"    - RA: {dns_resp.ra} (Recursion Available)")
    print(f"  Answer Count: {dns_resp.ancount}")
    print(f"  Authority Count: {dns_resp.nscount}")
    print(f"  Additional Count: {dns_resp.arcount}")
    
    # Parse answers
    if dns_resp.ancount > 0:
        print(f"\nAnswers:")
        for i in range(dns_resp.ancount):
            if dns_resp.an[i]:
                rr = dns_resp.an[i]
                print(f"  {i+1}. {rr.rrname.decode()}")
                print(f"     Type: {rr.type} ({rr.sprintf('%type%')})")
                print(f"     TTL: {rr.ttl} seconds")
                print(f"     Data: {rr.rdata}")
    else:
        print(f"\n✗ No answers (domain may not exist)")
    
    return response

def compare_query_types(domain):
    """Query different record types"""
    print_section(f"Querying Different Record Types for {domain}")
    
    types = ["A", "AAAA", "MX", "NS", "TXT"]
    
    for qtype in types:
        query = IP(dst="8.8.8.8")/UDP(dport=53)/DNS(rd=1, qd=DNSQR(qname=domain, qtype=qtype))
        response = sr1(query, verbose=0, timeout=3)
        
        print(f"\n{qtype} Record:")
        if response and response.haslayer(DNS):
            dns_resp = response[DNS]
            if dns_resp.ancount > 0:
                for i in range(dns_resp.ancount):
                    if dns_resp.an[i]:
                        rr = dns_resp.an[i]
                        print(f"  {rr.rdata}")
            else:
                print(f"  No {qtype} record found")
        else:
            print(f"  No response")

def demonstrate_dns_caching():
    """Explain DNS caching"""
    print_section("DNS Caching")
    print("""
DNS uses multi-level caching for performance:

1. Browser Cache:
   - Caches recent lookups
   - Very short TTL (seconds)

2. OS Cache:
   - System resolver cache
   - Check with: systemd-resolve --statistics (Linux)

3. Resolver Cache:
   - ISP or public DNS server
   - Caches based on TTL

4. Authoritative Server:
   - Source of truth
   - No caching

TTL (Time To Live):
- Tells caches how long to store record
- Set by domain owner
- Typical values:
  • 300s (5 min): Dynamic services
  • 3600s (1 hour): Common default
  • 86400s (24 hours): Stable records

Check your DNS cache (Linux):
  systemd-resolve --flush-caches   (clear)
  systemd-resolve --statistics     (view stats)
    """)

def main():
    """Main demonstration function"""
    print("\n" + "="*60)
    print("  APPLICATION LAYER: DNS QUERY DEMO")
    print("="*60)
    print("\nThis demo builds DNS queries from scratch.")
    print("Learn how domain name resolution really works!")
    
    # Get domain from args or use default
    domain = sys.argv[1] if len(sys.argv) > 1 else "example.com"
    
    # Part 1: Explain DNS
    explain_dns()
    
    # Part 2: Record types
    show_dns_record_types()
    
    # Part 3: Build query
    build_dns_query(domain)
    
    # Part 4: Caching
    demonstrate_dns_caching()
    
    # Part 5: Send real query
    print("\n" + "="*60)
    print("Sending Real DNS Queries")
    print("="*60)
    
    try:
        # Query A record
        send_dns_query(domain, "A")
        
        # Query multiple types
        compare_query_types(domain)
        
    except Exception as e:
        print(f"\n⚠️  Error: {e}")
        print("Note: Some networks may block DNS queries to external servers")
    
    print_section("Experiments to Try")
    print("""
1. Capture DNS traffic:
   sudo tcpdump -i any udp port 53 -vv

2. Query different servers:
   - 8.8.8.8 (Google)
   - 1.1.1.1 (Cloudflare)
   - Your router's IP

3. Use dig/nslookup:
   dig example.com
   dig example.com MX
   dig @8.8.8.8 example.com

4. Watch in Wireshark:
   - Filter: dns
   - Expand DNS section
   - See query/response pairs

5. Reverse DNS lookup:
   dig -x 8.8.8.8
   (PTR record)

6. Trace DNS resolution:
   dig +trace example.com
   (Shows full resolution path)

7. Check your DNS resolver:
   cat /etc/resolv.conf
   systemd-resolve --status

8. Performance test:
   - Query same domain multiple times
   - First query: slower (no cache)
   - Subsequent: faster (cached)
    """)
    
    print("\n✅ Demo complete! Continue to 03_packet_capture_analyzer.py\n")

if __name__ == "__main__":
    main()

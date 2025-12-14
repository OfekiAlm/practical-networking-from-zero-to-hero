#!/usr/bin/env python3
"""
Application Demo: HTTP from Scratch
====================================

This script demonstrates HTTP at the TCP level.
You'll learn:
- How HTTP works over TCP
- HTTP request/response format
- Building HTTP manually

Run with: python3 01_http_from_scratch.py

EXPERIMENT IDEAS:
1. Make requests to different servers
2. Modify HTTP headers
3. Compare with browser behavior
"""

import socket
import ssl

def print_section(title):
    """Pretty print section headers"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def explain_http_layers():
    """Explain how HTTP sits on TCP"""
    print_section("HTTP Layering")
    print("""
HTTP is an Application Layer (Layer 7) protocol that runs on TCP:

Layer Stack:
  ┌─────────────────────────┐
  │   Application (HTTP)    │  Layer 7: GET /index.html HTTP/1.1
  ├─────────────────────────┤
  │   Transport (TCP)       │  Layer 4: Port 80, reliable delivery
  ├─────────────────────────┤
  │   Network (IP)          │  Layer 3: Routing to destination
  ├─────────────────────────┤
  │   Data Link (Ethernet)  │  Layer 2: Local delivery
  └─────────────────────────┘

HTTP Request Format:
  REQUEST-LINE CRLF
  HEADERS CRLF
  CRLF
  BODY (optional)

Example:
  GET /index.html HTTP/1.1
  Host: example.com
  User-Agent: MyClient/1.0
  Connection: close
  
  (blank line)

HTTP Response Format:
  STATUS-LINE CRLF
  HEADERS CRLF
  CRLF
  BODY

Example:
  HTTP/1.1 200 OK
  Content-Type: text/html
  Content-Length: 1234
  
  <html>...</html>
    """)

def build_http_request(host, path="/", method="GET"):
    """Build HTTP request manually"""
    print_section(f"Building HTTP {method} Request")
    
    # HTTP request format
    request = f"{method} {path} HTTP/1.1\r\n"
    request += f"Host: {host}\r\n"
    request += "User-Agent: PracticalNetworking/1.0\r\n"
    request += "Accept: */*\r\n"
    request += "Connection: close\r\n"
    request += "\r\n"  # Empty line ends headers
    
    print(f"\nHTTP Request to {host}{path}:")
    print("-" * 60)
    print(request)
    print("-" * 60)
    
    print("\nRequest Breakdown:")
    lines = request.split('\r\n')
    print(f"Request Line: {lines[0]}")
    print(f"  Method: {method}")
    print(f"  Path: {path}")
    print(f"  Version: HTTP/1.1")
    print("\nHeaders:")
    for line in lines[1:-2]:  # Skip request line and last empty lines
        if line:
            print(f"  {line}")
    
    return request.encode()

def send_http_request(host, port=80, path="/", use_ssl=False):
    """Send HTTP request over raw TCP"""
    print_section(f"Sending HTTP Request to {host}:{port}")
    
    try:
        # Step 1: Create TCP socket
        print("\n1. Creating TCP socket...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        
        # Step 2: TCP connect
        print(f"2. Connecting to {host}:{port}...")
        sock.connect((host, port))
        print("   ✓ TCP connection established (3-way handshake complete)")
        
        # Step 3: Wrap with SSL if needed
        if use_ssl:
            print("3. Establishing SSL/TLS...")
            context = ssl.create_default_context()
            sock = context.wrap_socket(sock, server_hostname=host)
            print("   ✓ TLS handshake complete")
        
        # Step 4: Send HTTP request
        print(f"4. Sending HTTP request...")
        request = build_http_request(host, path)
        sock.sendall(request)
        print("   ✓ Request sent")
        
        # Step 5: Receive response
        print("5. Receiving HTTP response...")
        response = b""
        while True:
            try:
                data = sock.recv(4096)
                if not data:
                    break
                response += data
            except socket.timeout:
                break
        
        print(f"   ✓ Received {len(response)} bytes")
        
        # Step 6: Close connection
        sock.close()
        print("6. TCP connection closed (FIN handshake)")
        
        return response
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return None

def parse_http_response(response):
    """Parse and display HTTP response"""
    print_section("Parsing HTTP Response")
    
    if not response:
        print("No response to parse")
        return
    
    try:
        # Decode response
        response_str = response.decode('utf-8', errors='ignore')
        
        # Split headers and body
        parts = response_str.split('\r\n\r\n', 1)
        header_section = parts[0]
        body = parts[1] if len(parts) > 1 else ""
        
        # Parse status line and headers
        lines = header_section.split('\r\n')
        status_line = lines[0]
        headers = {}
        
        for line in lines[1:]:
            if ':' in line:
                key, value = line.split(':', 1)
                headers[key.strip()] = value.strip()
        
        # Display results
        print("\nStatus Line:")
        print(f"  {status_line}")
        parts = status_line.split(' ', 2)
        if len(parts) >= 3:
            print(f"  Version: {parts[0]}")
            print(f"  Status Code: {parts[1]}")
            print(f"  Reason: {parts[2]}")
        
        print("\nResponse Headers:")
        for key, value in headers.items():
            print(f"  {key}: {value}")
        
        print(f"\nBody Length: {len(body)} bytes")
        if body:
            print(f"\nBody Preview (first 200 chars):")
            print("-" * 60)
            print(body[:200])
            if len(body) > 200:
                print("...")
            print("-" * 60)
        
    except Exception as e:
        print(f"Error parsing response: {e}")

def compare_http_versions():
    """Compare HTTP versions"""
    print_section("HTTP Versions")
    print("""
HTTP/1.0 (1996):
- New TCP connection per request
- No persistent connections
- Simple but inefficient

HTTP/1.1 (1997):
- Persistent connections (Connection: keep-alive)
- Pipelining (multiple requests without waiting)
- Chunked transfer encoding
- Host header required (virtual hosting)

HTTP/2 (2015):
- Binary protocol (not text)
- Multiplexing (multiple requests on one connection)
- Server push
- Header compression (HPACK)

HTTP/3 (2022):
- Uses QUIC instead of TCP
- Built on UDP
- Improved performance
- Better handling of packet loss
    """)

def demonstrate_http_methods():
    """Show different HTTP methods"""
    print_section("HTTP Methods")
    
    methods = [
        ("GET", "Retrieve resource (most common)"),
        ("POST", "Submit data to server"),
        ("PUT", "Update/replace resource"),
        ("DELETE", "Remove resource"),
        ("HEAD", "Like GET but only headers (no body)"),
        ("OPTIONS", "Query supported methods"),
        ("PATCH", "Partial modification"),
    ]
    
    print(f"\n{'Method':<10} {'Description'}")
    print("-" * 60)
    for method, desc in methods:
        print(f"{method:<10} {desc}")
    
    print("\n💡 GET and POST are most commonly used")

def main():
    """Main demonstration function"""
    print("\n" + "="*60)
    print("  APPLICATION LAYER: HTTP FROM SCRATCH")
    print("="*60)
    print("\nThis demo shows HTTP working over TCP.")
    print("See how web browsers really work under the hood!")
    
    # Part 1: Explain layers
    explain_http_layers()
    
    # Part 2: HTTP methods
    demonstrate_http_methods()
    
    # Part 3: HTTP versions
    compare_http_versions()
    
    # Part 4: Build request
    build_http_request("example.com", "/")
    
    # Part 5: Send real request
    print("\n" + "="*60)
    print("Making Real HTTP Request")
    print("="*60)
    
    response = send_http_request("example.com", 80, "/")
    
    if response:
        parse_http_response(response)
    
    print_section("Experiments to Try")
    print("""
1. Capture HTTP with tcpdump:
   sudo tcpdump -i any -A 'tcp port 80' -nn

2. Manual HTTP with netcat:
   printf "GET / HTTP/1.1\\r\\nHost: example.com\\r\\n\\r\\n" | nc example.com 80

3. Compare with browser:
   - Open browser dev tools (F12)
   - Go to Network tab
   - Visit http://example.com
   - Compare headers

4. Try different methods:
   - Modify script to use POST
   - Add custom headers
   - Send body data

5. Monitor in Wireshark:
   - Filter: http
   - Follow TCP stream
   - See complete HTTP transaction

6. Test HTTPS:
   - Modify script to use port 443 with SSL
   - Observe TLS handshake in Wireshark

7. Implement other methods:
   - HEAD request
   - POST with form data
   - Custom User-Agent
    """)
    
    print("\n✅ Demo complete! Continue to 02_dns_query.py\n")

if __name__ == "__main__":
    main()

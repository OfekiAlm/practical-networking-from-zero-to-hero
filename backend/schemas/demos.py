"""Parameter schemas for specific demos."""
import re
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class TCPHandshakeParams(BaseModel):
    """Parameters for TCP 3-way handshake demo."""
    
    target_ip: str = Field(
        ...,
        description="Target IP address (IPv4)",
        examples=["8.8.8.8", "142.250.185.46"]
    )
    target_port: int = Field(
        ...,
        description="Target TCP port number",
        ge=1,
        le=65535,
        examples=[80, 443, 22]
    )
    timeout: int = Field(
        default=5,
        description="Timeout in seconds",
        ge=1,
        le=30
    )
    source_port: Optional[int] = Field(
        None,
        description="Source port (random if not specified)",
        ge=1024,
        le=65535
    )
    
    @field_validator("target_ip")
    @classmethod
    def validate_ip(cls, v: str) -> str:
        """Validate IPv4 address format."""
        pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
        if not re.match(pattern, v):
            raise ValueError("Invalid IPv4 address format")
        
        # Validate each octet
        octets = v.split(".")
        for octet in octets:
            if int(octet) > 255:
                raise ValueError(f"Invalid octet value: {octet}")
        
        # Block private/special ranges for security (optional, can be relaxed)
        first_octet = int(octets[0])
        if first_octet in [0, 127, 224, 240]:
            raise ValueError(f"IP address range not allowed: {v}")
        
        return v


class ARPDemoParams(BaseModel):
    """Parameters for ARP demo."""
    
    target_ip: str = Field(
        ...,
        description="Target IP address to resolve",
        examples=["192.168.1.1"]
    )
    interface: Optional[str] = Field(
        None,
        description="Network interface to use (default interface if not specified)"
    )
    timeout: int = Field(
        default=2,
        description="Timeout in seconds",
        ge=1,
        le=10
    )
    
    @field_validator("target_ip")
    @classmethod
    def validate_ip(cls, v: str) -> str:
        """Validate IPv4 address format."""
        pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
        if not re.match(pattern, v):
            raise ValueError("Invalid IPv4 address format")
        
        octets = v.split(".")
        for octet in octets:
            if int(octet) > 255:
                raise ValueError(f"Invalid octet value: {octet}")
        
        return v


class ICMPPingParams(BaseModel):
    """Parameters for ICMP ping demo."""
    
    target_ip: str = Field(
        ...,
        description="Target IP address to ping",
        examples=["8.8.8.8"]
    )
    count: int = Field(
        default=4,
        description="Number of ping packets to send",
        ge=1,
        le=10
    )
    timeout: int = Field(
        default=2,
        description="Timeout per ping in seconds",
        ge=1,
        le=10
    )
    packet_size: int = Field(
        default=56,
        description="Packet payload size in bytes",
        ge=0,
        le=1472
    )
    ttl: int = Field(
        default=64,
        description="Time to live",
        ge=1,
        le=255
    )
    
    @field_validator("target_ip")
    @classmethod
    def validate_ip(cls, v: str) -> str:
        """Validate IPv4 address format."""
        pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
        if not re.match(pattern, v):
            raise ValueError("Invalid IPv4 address format")
        
        octets = v.split(".")
        for octet in octets:
            if int(octet) > 255:
                raise ValueError(f"Invalid octet value: {octet}")
        
        return v

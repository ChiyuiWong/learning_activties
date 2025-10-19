#!/usr/bin/env python3
"""
Simple test to check server status
"""
import requests
import socket

def test_port_5000():
    """Test if port 5000 is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 5000))
        sock.close()
        if result == 0:
            print("Port 5000 is open")
            return True
        else:
            print("Port 5000 is closed")
            return False
    except Exception as e:
        print(f"Error testing port 5000: {e}")
        return False

def test_http_request():
    """Test HTTP request to server"""
    try:
        response = requests.get("http://localhost:5000/", timeout=5)
        print(f"HTTP request successful: {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print("HTTP connection failed")
        return False
    except Exception as e:
        print(f"HTTP request error: {e}")
        return False

if __name__ == "__main__":
    print("Testing server status...")
    
    if test_port_5000():
        print("Port 5000 is accessible")
        if test_http_request():
            print("Server is responding to HTTP requests")
        else:
            print("Server is not responding to HTTP requests")
    else:
        print("Port 5000 is not accessible")
        print("Please check if your server is running")

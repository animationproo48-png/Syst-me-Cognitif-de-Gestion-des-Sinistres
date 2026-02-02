#!/usr/bin/env python
"""
API Testing Script - Verify Insurance CRM Backend
Run from workspace: python test_api.py
"""
import requests
import json
import time
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("\n[TEST] Health Check")
    try:
        resp = requests.get(f"{BASE_URL}/health")
        print(f"  Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"  Response: {resp.json()}")
            print("  [OK] Health check passed")
            return True
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False

def test_get_client():
    """Test get client by matricule"""
    print("\n[TEST] Get Client by Matricule")
    try:
        resp = requests.get(f"{BASE_URL}/api/v1/clients/AB-4521-22")
        print(f"  Status: {resp.status_code}")
        if resp.status_code == 200:
            client = resp.json()
            print(f"  Client: {client['nom']} {client['prenom']}")
            print(f"  Email: {client['email']}")
            print("  [OK] Client retrieval passed")
            return True
        else:
            print(f"  Error: {resp.text}")
            return False
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False

def test_create_client():
    """Test create new client"""
    print("\n[TEST] Create New Client")
    try:
        new_client = {
            "matricule": "TEST-1234-26",
            "nom": "Test",
            "prenom": "User",
            "email": "test.user@email.com",
            "telephone": "06 11 22 33 44",
            "civilite": "Mr"
        }
        resp = requests.post(f"{BASE_URL}/api/v1/clients", json=new_client)
        print(f"  Status: {resp.status_code}")
        if resp.status_code == 200:
            created = resp.json()
            print(f"  Created: {created['nom']} {created['prenom']}")
            print("  [OK] Client creation passed")
            return True
        else:
            print(f"  Error: {resp.text}")
            return False
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False

def test_authenticate():
    """Test conversation authenticate endpoint"""
    print("\n[TEST] Authenticate Endpoint")
    try:
        auth_data = {"matricule": "AB-4521-22"}
        resp = requests.post(f"{BASE_URL}/api/v1/conversation/authenticate", json=auth_data)
        print(f"  Status: {resp.status_code}")
        if resp.status_code == 200:
            result = resp.json()
            print(f"  Valide: {result.get('valide')}")
            if result.get('client'):
                print(f"  Client: {result['client']['nom']} {result['client']['prenom']}")
            print("  [OK] Authentication passed")
            return True
        else:
            print(f"  Error: {resp.text}")
            return False
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("[*] INSURANCE CRM API TESTING")
    print("="*60)
    
    # Give server time to fully start
    time.sleep(2)
    
    tests = [
        test_health,
        test_get_client,
        test_create_client,
        test_authenticate,
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"[ERROR] Test failed: {e}")
            results.append(False)
    
    print("\n" + "="*60)
    print(f"[*] RESULTS: {sum(results)}/{len(results)} tests passed")
    print("="*60)
    
    if all(results):
        print("\n[OK] All tests passed! Backend is ready.")
        return 0
    else:
        print("\n[!] Some tests failed. Check output above.")
        return 1

if __name__ == "__main__":
    exit(main())

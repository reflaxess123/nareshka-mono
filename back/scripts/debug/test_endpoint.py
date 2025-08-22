#!/usr/bin/env python3

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_companies_top():
    print("Testing /api/v2/interviews/companies/top endpoint")
    response = client.get("/api/v2/interviews/companies/top")
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data)} companies")
        for company in data[:3]:  # Show first 3
            print(f"  {company}")

if __name__ == "__main__":
    test_companies_top()
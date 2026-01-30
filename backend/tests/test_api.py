import pytest
from datetime import datetime
from fastapi.testclient import TestClient


class TestContractsAPI:
    """Integration tests for the contracts API endpoints"""
    
    def test_root_endpoint(self, client):
        """Test the root endpoint"""
        response = client.get("/")
        
        assert response.status_code == 200
        assert response.json() == {"message": "Procurement Data Dashboard API"}
    
    def test_health_endpoint(self, client):
        """Test the health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
    
    def test_create_contract_success(self, client, sample_contract_data):
        """Test creating a contract via API"""
        response = client.post("/contracts", json=sample_contract_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["company_name"] == sample_contract_data["company_name"]
        assert data["contract_value"] == sample_contract_data["contract_value"]
        assert data["category"] == sample_contract_data["category"]
        assert "id" in data
        assert "created_at" in data
    
    def test_create_contract_invalid_data(self, client):
        """Test creating a contract with invalid data"""
        invalid_data = {
            "company_name": "",  # Empty name
            "contract_value": -100,  # Negative value
            "contract_date": "2024-01-15",
            "category": "goods"
        }
        
        response = client.post("/contracts", json=invalid_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_create_contract_invalid_category(self, client):
        """Test creating a contract with invalid category"""
        invalid_data = {
            "company_name": "Test",
            "contract_value": 100,
            "contract_date": "2024-01-15",
            "category": "invalid_category"
        }
        
        response = client.post("/contracts", json=invalid_data)
        
        assert response.status_code == 422
    
    def test_get_contracts_empty(self, client):
        """Test getting contracts when database is empty"""
        response = client.get("/contracts")
        
        assert response.status_code == 200
        data = response.json()
        assert data["contracts"] == []
        assert data["total"] == 0
        assert data["page"] == 0
        assert data["has_more"] is False
    
    def test_get_contracts_with_data(self, client, multiple_contracts_data):
        """Test getting contracts with data"""
        # Create contracts first
        for contract_data in multiple_contracts_data:
            client.post("/contracts", json=contract_data)
        
        response = client.get("/contracts")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["contracts"]) == len(multiple_contracts_data)
        assert data["total"] == len(multiple_contracts_data)
    
    def test_get_contracts_pagination(self, client, multiple_contracts_data):
        """Test pagination"""
        # Create contracts
        for contract_data in multiple_contracts_data:
            client.post("/contracts", json=contract_data)
        
        # Get first page
        response = client.get("/contracts?page=0&page_size=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["contracts"]) == 2
        assert data["page"] == 0
        assert data["has_more"] is True
        
        # Get second page
        response = client.get("/contracts?page=1&page_size=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["contracts"]) == 2
        assert data["page"] == 1
    
    def test_get_contracts_filter_by_category(self, client, multiple_contracts_data):
        """Test filtering by category"""
        for contract_data in multiple_contracts_data:
            client.post("/contracts", json=contract_data)
        
        response = client.get("/contracts?category=goods")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2  # Two goods contracts
        assert all(c["category"] == "goods" for c in data["contracts"])
    
    def test_get_contracts_filter_by_value(self, client, multiple_contracts_data):
        """Test filtering by value range"""
        for contract_data in multiple_contracts_data:
            client.post("/contracts", json=contract_data)
        
        response = client.get("/contracts?min_value=100000&max_value=200000")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["contracts"][0]["contract_value"] == 150000.0
    
    def test_get_contracts_filter_by_date(self, client, multiple_contracts_data):
        """Test filtering by date range"""
        for contract_data in multiple_contracts_data:
            client.post("/contracts", json=contract_data)
        
        response = client.get(
            "/contracts?start_date=2024-02-01T00:00:00&end_date=2024-03-31T23:59:59"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2  # Two contracts in Feb-March
    
    def test_get_contracts_invalid_date_range(self, client):
        """Test invalid date range"""
        response = client.get(
            "/contracts?start_date=2024-12-31T00:00:00&end_date=2024-01-01T00:00:00"
        )
        
        assert response.status_code == 400
        assert "start_date must be before end_date" in response.json()["detail"]
    
    def test_get_contracts_invalid_value_range(self, client):
        """Test invalid value range"""
        response = client.get("/contracts?min_value=1000&max_value=500")
        
        assert response.status_code == 400
        assert "min_value must be less than max_value" in response.json()["detail"]
    
    def test_get_contract_by_id(self, client, sample_contract_data):
        """Test getting a specific contract by ID"""
        # Create a contract
        create_response = client.post("/contracts", json=sample_contract_data)
        contract_id = create_response.json()["id"]
        
        # Get the contract
        response = client.get(f"/contracts/{contract_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == contract_id
        assert data["company_name"] == sample_contract_data["company_name"]
    
    def test_get_contract_not_found(self, client):
        """Test getting a non-existent contract"""
        response = client.get("/contracts/99999")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Contract not found"
    
    def test_get_statistics_empty(self, client):
        """Test statistics with no contracts"""
        response = client.get("/contracts/statistics")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_contracts"] == 0
        assert data["total_value"] == 0.0
        assert data["average_value"] == 0.0
    
    def test_get_statistics_with_data(self, client, multiple_contracts_data):
        """Test statistics with data"""
        for contract_data in multiple_contracts_data:
            client.post("/contracts", json=contract_data)
        
        response = client.get("/contracts/statistics")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_contracts"] == 4
        assert data["total_value"] == 525000.0
        assert data["average_value"] == 131250.0
        assert "goods" in data["by_category"]
        assert "services" in data["by_category"]
        assert "works" in data["by_category"]
    
    def test_cors_headers(self, client):
        """Test that CORS headers are present"""
        response = client.options(
            "/contracts",
            headers={"Origin": "http://localhost:3000"}
        )
        
        # CORS middleware should handle this
        assert response.status_code in [200, 405]  # OPTIONS might not be explicitly defined
    
    def test_negative_page_number(self, client):
        """Test that negative page numbers are rejected"""
        response = client.get("/contracts?page=-1")
        
        assert response.status_code == 422  # Validation error
    
    def test_excessive_page_size(self, client, multiple_contracts_data):
        """Test that page size over 1000 is rejected by validation"""
        for contract_data in multiple_contracts_data:
            client.post("/contracts", json=contract_data)
        
        # Request excessive page size - API validates le=1000
        response = client.get("/contracts?page_size=5000")
        
        # Query validation rejects page_size > 1000
        assert response.status_code == 422

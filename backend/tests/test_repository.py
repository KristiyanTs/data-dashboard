import pytest
from datetime import datetime
from app.repositories.contract_repository import ContractRepository
from app.database import Contract as DBContract, ContractCategoryEnum


class TestContractRepository:
    """Unit tests for ContractRepository"""
    
    def test_create_contract(self, db_session, sample_contract_data):
        """Test creating a new contract"""
        repository = ContractRepository(db_session)
        
        contract = repository.create(sample_contract_data)
        
        assert contract.id is not None
        assert contract.company_name == sample_contract_data["company_name"]
        assert contract.contract_value == sample_contract_data["contract_value"]
        assert contract.category == ContractCategoryEnum.GOODS
        assert contract.description == sample_contract_data["description"]
        assert contract.created_at is not None
    
    def test_get_by_id(self, db_session, sample_contract_data):
        """Test retrieving a contract by ID"""
        repository = ContractRepository(db_session)
        
        created = repository.create(sample_contract_data)
        retrieved = repository.get_by_id(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.company_name == created.company_name
    
    def test_get_by_id_not_found(self, db_session):
        """Test retrieving a non-existent contract"""
        repository = ContractRepository(db_session)
        
        result = repository.get_by_id(99999)
        
        assert result is None
    
    def test_get_all_no_filters(self, db_session, multiple_contracts_data):
        """Test getting all contracts without filters"""
        repository = ContractRepository(db_session)
        
        # Create multiple contracts
        for data in multiple_contracts_data:
            repository.create(data)
        
        contracts, total = repository.get_all()
        
        assert total == len(multiple_contracts_data)
        assert len(contracts) == len(multiple_contracts_data)
    
    def test_get_all_with_pagination(self, db_session, multiple_contracts_data):
        """Test pagination"""
        repository = ContractRepository(db_session)
        
        for data in multiple_contracts_data:
            repository.create(data)
        
        # Get first page
        contracts, total = repository.get_all(skip=0, limit=2)
        assert len(contracts) == 2
        assert total == len(multiple_contracts_data)
        
        # Get second page
        contracts, total = repository.get_all(skip=2, limit=2)
        assert len(contracts) == 2
        assert total == len(multiple_contracts_data)
    
    def test_get_all_filter_by_category(self, db_session, multiple_contracts_data):
        """Test filtering by category"""
        repository = ContractRepository(db_session)
        
        for data in multiple_contracts_data:
            repository.create(data)
        
        contracts, total = repository.get_all(category="goods")
        
        assert total == 2  # Two goods contracts
        assert all(c.category == ContractCategoryEnum.GOODS for c in contracts)
    
    def test_get_all_filter_by_value_range(self, db_session, multiple_contracts_data):
        """Test filtering by value range"""
        repository = ContractRepository(db_session)
        
        for data in multiple_contracts_data:
            repository.create(data)
        
        contracts, total = repository.get_all(min_value=100000, max_value=200000)
        
        assert total == 1  # Only one contract in this range (150000)
        assert contracts[0].contract_value == 150000.0
    
    def test_get_all_filter_by_date_range(self, db_session, multiple_contracts_data):
        """Test filtering by date range"""
        repository = ContractRepository(db_session)
        
        for data in multiple_contracts_data:
            repository.create(data)
        
        start_date = datetime(2024, 2, 1)
        end_date = datetime(2024, 3, 31)
        
        contracts, total = repository.get_all(start_date=start_date, end_date=end_date)
        
        assert total == 2  # Two contracts in Feb-March
        for contract in contracts:
            assert start_date <= contract.contract_date <= end_date
    
    def test_get_all_combined_filters(self, db_session, multiple_contracts_data):
        """Test combining multiple filters"""
        repository = ContractRepository(db_session)
        
        for data in multiple_contracts_data:
            repository.create(data)
        
        contracts, total = repository.get_all(
            category="goods",
            min_value=40000,
            max_value=60000
        )
        
        assert total == 1  # Only Company A matches
        assert contracts[0].company_name == "Company A"
    
    def test_get_statistics_empty_db(self, db_session):
        """Test statistics with no contracts"""
        repository = ContractRepository(db_session)
        
        stats = repository.get_statistics()
        
        assert stats['total_contracts'] == 0
        assert stats['total_value'] == 0.0
        assert stats['average_value'] == 0.0
        assert stats['by_category'] == {}
    
    def test_get_statistics_with_data(self, db_session, multiple_contracts_data):
        """Test statistics calculation"""
        repository = ContractRepository(db_session)
        
        for data in multiple_contracts_data:
            repository.create(data)
        
        stats = repository.get_statistics()
        
        assert stats['total_contracts'] == 4
        assert stats['total_value'] == 525000.0  # Sum of all contracts
        assert stats['average_value'] == 131250.0  # Average
        
        # Check category breakdown
        assert 'goods' in stats['by_category']
        assert stats['by_category']['goods']['count'] == 2.0
        assert stats['by_category']['goods']['total_value'] == 125000.0
        
        assert 'services' in stats['by_category']
        assert stats['by_category']['services']['count'] == 1.0
        
        assert 'works' in stats['by_category']
        assert stats['by_category']['works']['count'] == 1.0

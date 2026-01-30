import pytest
from datetime import datetime
from unittest.mock import Mock
from app.services.contract_service import ContractService
from app.repositories.contract_repository import ContractRepository
from app.models import ContractCreate
from app.database import Contract as DBContract, ContractCategoryEnum


class TestContractService:
    """Unit tests for ContractService"""
    
    @pytest.fixture
    def mock_repository(self):
        """Create a mock repository"""
        return Mock(spec=ContractRepository)
    
    @pytest.fixture
    def service(self, mock_repository):
        """Create a service with mocked repository"""
        return ContractService(mock_repository)
    
    def test_get_contracts_success(self, service, mock_repository):
        """Test getting contracts successfully"""
        # Mock data
        mock_contracts = [
            DBContract(
                id=1,
                company_name="Test Co",
                contract_value=100000,
                contract_date=datetime(2024, 1, 15),
                category=ContractCategoryEnum.GOODS,
                description="Test",
                created_at=datetime.now()
            )
        ]
        mock_repository.get_all.return_value = (mock_contracts, 1)
        
        result = service.get_contracts(page=0, page_size=10)
        
        assert result.total == 1
        assert len(result.contracts) == 1
        assert result.page == 0
        assert result.page_size == 10
        assert result.has_more is False
        mock_repository.get_all.assert_called_once()
    
    def test_get_contracts_with_pagination(self, service, mock_repository):
        """Test pagination logic"""
        mock_contracts = [
            DBContract(
                id=i,
                company_name="Test",
                contract_value=1000,
                contract_date=datetime(2024, 1, 1),
                category=ContractCategoryEnum.GOODS,
                created_at=datetime.now()
            )
            for i in range(1, 11)
        ]
        mock_repository.get_all.return_value = (mock_contracts, 25)
        
        result = service.get_contracts(page=1, page_size=10)
        
        assert result.total == 25
        assert result.page == 1
        assert result.has_more is True  # 10 + 10 = 20 < 25
    
    def test_get_contracts_limits_page_size(self, service, mock_repository):
        """Test that page size is limited to 1000"""
        mock_repository.get_all.return_value = ([], 0)
        
        service.get_contracts(page=0, page_size=5000)
        
        # Check that repository was called with limited page size
        call_args = mock_repository.get_all.call_args
        assert call_args.kwargs['limit'] == 1000
    
    def test_get_contracts_validates_date_range(self, service, mock_repository):
        """Test date range validation"""
        start_date = datetime(2024, 12, 31)
        end_date = datetime(2024, 1, 1)
        
        with pytest.raises(ValueError, match="start_date must be before end_date"):
            service.get_contracts(start_date=start_date, end_date=end_date)
    
    def test_get_contracts_validates_value_range(self, service, mock_repository):
        """Test value range validation"""
        with pytest.raises(ValueError, match="min_value must be less than max_value"):
            service.get_contracts(min_value=1000, max_value=500)
    
    def test_get_contracts_applies_filters(self, service, mock_repository):
        """Test that filters are passed to repository"""
        mock_repository.get_all.return_value = ([], 0)
        
        service.get_contracts(
            page=0,
            page_size=50,
            category="goods",
            min_value=1000,
            max_value=5000,
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31)
        )
        
        call_args = mock_repository.get_all.call_args
        assert call_args.kwargs['category'] == "goods"
        assert call_args.kwargs['min_value'] == 1000
        assert call_args.kwargs['max_value'] == 5000
        assert call_args.kwargs['start_date'] == datetime(2024, 1, 1)
        assert call_args.kwargs['end_date'] == datetime(2024, 12, 31)
    
    def test_get_contract_found(self, service, mock_repository):
        """Test getting a single contract that exists"""
        mock_contract = DBContract(
            id=1,
            company_name="Test Co",
            contract_value=100000,
            contract_date=datetime(2024, 1, 15),
            category=ContractCategoryEnum.GOODS,
            created_at=datetime.now()
        )
        mock_repository.get_by_id.return_value = mock_contract
        
        result = service.get_contract(1)
        
        assert result is not None
        assert result.id == 1
        assert result.company_name == "Test Co"
        mock_repository.get_by_id.assert_called_once_with(1)
    
    def test_get_contract_not_found(self, service, mock_repository):
        """Test getting a contract that doesn't exist"""
        mock_repository.get_by_id.return_value = None
        
        result = service.get_contract(999)
        
        assert result is None
        mock_repository.get_by_id.assert_called_once_with(999)
    
    def test_create_contract_success(self, service, mock_repository):
        """Test creating a contract"""
        contract_data = ContractCreate(
            company_name="New Company",
            contract_value=50000,
            contract_date=datetime(2024, 1, 15),
            category="goods",
            description="New contract"
        )
        
        mock_db_contract = DBContract(
            id=1,
            company_name=contract_data.company_name,
            contract_value=contract_data.contract_value,
            contract_date=contract_data.contract_date,
            category=ContractCategoryEnum.GOODS,
            description=contract_data.description,
            created_at=datetime.now()
        )
        mock_repository.create.return_value = mock_db_contract
        
        result = service.create_contract(contract_data)
        
        assert result.id == 1
        assert result.company_name == "New Company"
        mock_repository.create.assert_called_once()
    
    def test_create_contract_high_value(self, service, mock_repository):
        """Test creating a high-value contract (>$10M)"""
        contract_data = ContractCreate(
            company_name="Big Company",
            contract_value=15_000_000,
            contract_date=datetime(2024, 1, 15),
            category="works"
        )
        
        mock_db_contract = DBContract(
            id=1,
            company_name=contract_data.company_name,
            contract_value=contract_data.contract_value,
            contract_date=contract_data.contract_date,
            category=ContractCategoryEnum.WORKS,
            created_at=datetime.now()
        )
        mock_repository.create.return_value = mock_db_contract
        
        # Should still create successfully (business rule just notes it)
        result = service.create_contract(contract_data)
        
        assert result.contract_value == 15_000_000
        mock_repository.create.assert_called_once()
    
    def test_create_contract_future_date(self, service, mock_repository):
        """Test creating a contract with future date"""
        future_date = datetime(2030, 1, 1)
        contract_data = ContractCreate(
            company_name="Future Company",
            contract_value=50000,
            contract_date=future_date,
            category="services"
        )
        
        mock_db_contract = DBContract(
            id=1,
            company_name=contract_data.company_name,
            contract_value=contract_data.contract_value,
            contract_date=contract_data.contract_date,
            category=ContractCategoryEnum.SERVICES,
            created_at=datetime.now()
        )
        mock_repository.create.return_value = mock_db_contract
        
        # Should still create successfully (business rule just notes it)
        result = service.create_contract(contract_data)
        
        assert result.contract_date == future_date
        mock_repository.create.assert_called_once()
    
    def test_get_statistics(self, service, mock_repository):
        """Test getting statistics"""
        mock_stats = {
            'total_contracts': 10,
            'total_value': 1000000.0,
            'average_value': 100000.0,
            'by_category': {
                'goods': {'count': 5.0, 'total_value': 500000.0},
                'services': {'count': 5.0, 'total_value': 500000.0}
            }
        }
        mock_repository.get_statistics.return_value = mock_stats
        
        result = service.get_statistics()
        
        assert result.total_contracts == 10
        assert result.total_value == 1000000.0
        assert result.average_value == 100000.0
        assert 'goods' in result.by_category
        mock_repository.get_statistics.assert_called_once()

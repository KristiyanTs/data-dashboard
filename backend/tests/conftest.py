import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app


# Use in-memory SQLite database for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with overridden database dependency"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_contract_data():
    """Sample contract data for testing"""
    return {
        "company_name": "Test Company",
        "contract_value": 100000.0,
        "contract_date": "2024-01-15",
        "category": "goods",
        "description": "Test contract description"
    }


@pytest.fixture
def multiple_contracts_data():
    """Multiple contracts for testing pagination and filtering"""
    return [
        {
            "company_name": "Company A",
            "contract_value": 50000.0,
            "contract_date": "2024-01-10",
            "category": "goods",
            "description": "Goods contract"
        },
        {
            "company_name": "Company B",
            "contract_value": 150000.0,
            "contract_date": "2024-02-15",
            "category": "services",
            "description": "Services contract"
        },
        {
            "company_name": "Company C",
            "contract_value": 250000.0,
            "contract_date": "2024-03-20",
            "category": "works",
            "description": "Works contract"
        },
        {
            "company_name": "Company D",
            "contract_value": 75000.0,
            "contract_date": "2024-01-25",
            "category": "goods",
            "description": "Another goods contract"
        },
    ]

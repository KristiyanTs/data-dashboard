"""
Tests for the scraper functionality
"""
import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime
from app.services.smart_scraper_service import SmartScraperService
from app.services.scraper_orchestrator import ScraperOrchestrator


@pytest.mark.asyncio
async def test_smart_scraper_ted_eu():
    """Test TED EU scraper returns contracts"""
    scraper = SmartScraperService()
    
    contracts = await scraper.scrape_ted_eu(limit=5)
    
    assert len(contracts) > 0
    assert len(contracts) <= 5
    
    # Check contract structure
    contract = contracts[0]
    assert "company_name" in contract
    assert "contract_value" in contract
    assert "contract_date" in contract
    assert "category" in contract
    assert "source" in contract
    assert contract["source"] == "TED_EU"
    
    await scraper.close()


@pytest.mark.asyncio
async def test_smart_scraper_sam_gov():
    """Test SAM.gov scraper returns contracts"""
    scraper = SmartScraperService()
    
    contracts = await scraper.scrape_sam_gov(limit=5)
    
    assert len(contracts) > 0
    assert len(contracts) <= 5
    
    # Check contract structure
    contract = contracts[0]
    assert "company_name" in contract
    assert "contract_value" in contract
    assert contract["source"] == "SAM_GOV"
    assert contract["country"] == "USA"
    
    await scraper.close()


@pytest.mark.asyncio
async def test_smart_scraper_uk():
    """Test UK Contracts Finder scraper returns contracts"""
    scraper = SmartScraperService()
    
    contracts = await scraper.scrape_uk_contracts_finder(limit=5)
    
    assert len(contracts) > 0
    assert len(contracts) <= 5
    
    # Check contract structure
    contract = contracts[0]
    assert contract["source"] == "UK_CONTRACTS_FINDER"
    assert contract["country"] == "GBR"
    
    await scraper.close()


def test_cpv_code_mapping():
    """Test CPV code to category mapping"""
    scraper = SmartScraperService()
    
    # Construction codes
    assert scraper._map_cpv_to_category("45000000") == "works"
    
    # Goods codes
    assert scraper._map_cpv_to_category("30000000") == "goods"
    assert scraper._map_cpv_to_category("31000000") == "goods"
    
    # Services codes (default)
    assert scraper._map_cpv_to_category("72000000") == "services"
    assert scraper._map_cpv_to_category("") == "services"


def test_naics_code_mapping():
    """Test NAICS code to category mapping"""
    scraper = SmartScraperService()
    
    # Construction
    assert scraper._map_naics_to_category("23") == "works"
    assert scraper._map_naics_to_category("236000") == "works"
    
    # Manufacturing/Goods
    assert scraper._map_naics_to_category("31") == "goods"
    assert scraper._map_naics_to_category("32") == "goods"
    assert scraper._map_naics_to_category("33") == "goods"
    assert scraper._map_naics_to_category("42") == "goods"
    
    # Services (default)
    assert scraper._map_naics_to_category("54") == "services"
    assert scraper._map_naics_to_category("") == "services"


@pytest.mark.asyncio
async def test_orchestrator_get_sources(db_session):
    """Test orchestrator returns configured sources"""
    orchestrator = ScraperOrchestrator(db_session)
    
    sources = orchestrator.get_sources()
    
    assert len(sources) >= 3
    assert any(s.name.startswith("TED") for s in sources)
    assert any(s.name.startswith("SAM") for s in sources)
    assert any(s.name.startswith("UK") for s in sources)
    
    await orchestrator.close()


@pytest.mark.asyncio
async def test_orchestrator_scrape_single_source(db_session):
    """Test orchestrator can scrape a single source"""
    orchestrator = ScraperOrchestrator(db_session)
    
    result = await orchestrator.scrape_single_source("ted_eu", limit=3)
    
    assert result.source == "ted_eu"
    assert result.contracts_found >= 0
    assert result.contracts_saved >= 0
    assert result.duration_seconds >= 0
    
    await orchestrator.close()


@pytest.mark.asyncio
async def test_orchestrator_duplicate_detection(db_session):
    """Test that duplicates are detected and skipped"""
    orchestrator = ScraperOrchestrator(db_session)
    
    # First scrape
    result1 = await orchestrator.scrape_single_source("ted_eu", limit=3)
    first_saved = result1.contracts_saved
    
    # Second scrape (should find duplicates)
    result2 = await orchestrator.scrape_single_source("ted_eu", limit=3)
    
    # All contracts should be duplicates on second run
    assert result2.duplicates_skipped == result2.contracts_found
    assert result2.contracts_saved == 0
    
    await orchestrator.close()

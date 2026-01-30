"""
Scraper Orchestrator - Intelligent coordination of multiple scraping sources
"""
import asyncio
from typing import List, Dict
from datetime import datetime
import logging
from sqlalchemy.orm import Session

from .smart_scraper_service import SmartScraperService
from ..repositories.contract_repository import ContractRepository
from ..models import ScraperResult, ScraperStatus, ScraperSource, ContractPreview

logger = logging.getLogger(__name__)


class ScraperOrchestrator:
    """
    Intelligent scraper that coordinates multiple data sources
    This is what makes the system SMARTER than traditional scrapers
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.smart_scraper = SmartScraperService()
        self.repository = ContractRepository(db)
        
        # Source configuration with best extraction method
        self.sources = {
            "ted_eu": ScraperSource(
                name="TED (EU Tenders Electronic Daily)",
                method="api",
                priority=1,
                url="https://ted.europa.eu",
                enabled=True
            ),
            "sam_gov": ScraperSource(
                name="SAM.gov (US Federal Procurement)",
                method="api",
                priority=1,
                url="https://sam.gov",
                enabled=True
            ),
            "uk_contracts_finder": ScraperSource(
                name="UK Contracts Finder",
                method="api",
                priority=2,
                url="https://www.contractsfinder.service.gov.uk",
                enabled=True
            ),
        }
    
    async def scrape_all_sources(self, limit_per_source: int = 50) -> ScraperStatus:
        """
        Scrape all enabled sources in parallel
        Returns comprehensive status with results from each source
        """
        started_at = datetime.now()
        
        # Get enabled sources
        enabled_sources = {
            name: config 
            for name, config in self.sources.items() 
            if config.enabled
        }
        
        logger.info(f"Starting scrape of {len(enabled_sources)} sources")
        
        # Create tasks for parallel execution
        tasks = []
        for source_name in enabled_sources.keys():
            tasks.append(self._scrape_source(source_name, limit_per_source))
        
        # Run all scrapers in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        scraper_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Scraper failed: {result}")
            else:
                scraper_results.append(result)
        
        completed_at = datetime.now()
        duration = (completed_at - started_at).total_seconds()
        
        status = ScraperStatus(
            status="completed",
            started_at=started_at,
            completed_at=completed_at,
            total_sources=len(enabled_sources),
            completed_sources=len(scraper_results),
            results=scraper_results
        )
        
        logger.info(f"Scraping completed in {duration:.2f}s. "
                   f"Total contracts: {sum(r.contracts_saved for r in scraper_results)}")
        
        return status
    
    async def _scrape_source(self, source_name: str, limit: int) -> ScraperResult:
        """
        Scrape a single source and save contracts to database
        """
        start_time = datetime.now()
        errors = []
        contracts_found = 0
        contracts_saved = 0
        duplicates_skipped = 0
        contract_previews = []
        
        try:
            # Call appropriate scraper based on source
            if source_name == "ted_eu":
                raw_contracts = await self.smart_scraper.scrape_ted_eu(limit=limit)
            elif source_name == "sam_gov":
                raw_contracts = await self.smart_scraper.scrape_sam_gov(limit=limit)
            elif source_name == "uk_contracts_finder":
                raw_contracts = await self.smart_scraper.scrape_uk_contracts_finder(limit=limit)
            else:
                raise ValueError(f"Unknown source: {source_name}")
            
            contracts_found = len(raw_contracts)
            logger.info(f"{source_name}: Found {contracts_found} contracts")
            
            # Save contracts to database
            for contract_data in raw_contracts:
                try:
                    # Check if contract already exists (by external_id)
                    existing = self._find_existing_contract(
                        contract_data.get("external_id"),
                        contract_data.get("source")
                    )
                    
                    if existing:
                        duplicates_skipped += 1
                        logger.debug(f"Skipping duplicate: {contract_data.get('external_id')}")
                        
                        # Add preview for duplicate
                        contract_date_str = contract_data.get("contract_date")
                        if isinstance(contract_date_str, datetime):
                            contract_date_str = contract_date_str.isoformat()
                        
                        contract_previews.append(ContractPreview(
                            company_name=contract_data.get("company_name", "Unknown"),
                            contract_value=contract_data.get("contract_value", 0),
                            contract_date=contract_date_str,
                            category=contract_data.get("category"),
                            description=contract_data.get("description"),
                            source=contract_data.get("source"),
                            external_id=contract_data.get("external_id"),
                            country=contract_data.get("country"),
                            is_duplicate=True,
                            duplicate_reason=f"Already exists in database (ID: {contract_data.get('external_id')})"
                        ))
                        continue
                    
                    # Parse and validate contract date
                    if isinstance(contract_data.get("contract_date"), str):
                        contract_data["contract_date"] = datetime.fromisoformat(
                            contract_data["contract_date"].replace("Z", "+00:00")
                        )
                    
                    # Save to database
                    self.repository.create(contract_data)
                    contracts_saved += 1
                    
                    # Add preview for saved contract
                    contract_date_str = contract_data.get("contract_date")
                    if isinstance(contract_date_str, datetime):
                        contract_date_str = contract_date_str.isoformat()
                    
                    contract_previews.append(ContractPreview(
                        company_name=contract_data.get("company_name", "Unknown"),
                        contract_value=contract_data.get("contract_value", 0),
                        contract_date=contract_date_str,
                        category=contract_data.get("category"),
                        description=contract_data.get("description"),
                        source=contract_data.get("source"),
                        external_id=contract_data.get("external_id"),
                        country=contract_data.get("country"),
                        is_duplicate=False
                    ))
                    
                except Exception as e:
                    error_msg = f"Error saving contract: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
            
            # Commit all changes
            self.db.commit()
            
        except Exception as e:
            error_msg = f"Error scraping {source_name}: {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg)
            self.db.rollback()
        
        duration = (datetime.now() - start_time).total_seconds()
        
        return ScraperResult(
            source=source_name,
            contracts_found=contracts_found,
            contracts_saved=contracts_saved,
            duplicates_skipped=duplicates_skipped,
            errors=errors,
            duration_seconds=duration,
            contract_previews=contract_previews
        )
    
    def _find_existing_contract(self, external_id: str, source: str) -> bool:
        """
        Check if a contract with this external_id and source already exists
        """
        if not external_id or not source:
            return False
        
        from ..database import Contract
        existing = self.db.query(Contract).filter(
            Contract.external_id == external_id,
            Contract.source == source
        ).first()
        
        return existing is not None
    
    def get_sources(self) -> List[ScraperSource]:
        """Get all configured sources"""
        return list(self.sources.values())
    
    async def scrape_single_source(self, source_name: str, limit: int = 50) -> ScraperResult:
        """
        Scrape a single source (useful for testing/debugging)
        """
        if source_name not in self.sources:
            raise ValueError(f"Unknown source: {source_name}")
        
        return await self._scrape_source(source_name, limit)
    
    async def close(self):
        """Clean up resources"""
        await self.smart_scraper.close()

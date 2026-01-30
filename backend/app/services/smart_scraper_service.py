"""
Smart Scraper Service - Real API integration for procurement data
"""
import httpx
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class SmartScraperService:
    """Procurement data scraper using real public APIs"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def scrape_ted_eu(
        self, 
        country: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """
        Scrape TED (EU Tenders Electronic Daily) using their PUBLIC API
        TED is the official EU procurement portal with 700k+ tenders annually
        
        API Documentation: https://ted.europa.eu/en/api
        Note: TED API v3 is publicly accessible without authentication for basic searches
        """
        try:
            logger.info(f"Scraping TED EU (country: {country}, limit: {limit})")
            
            # TED API v3 endpoint
            base_url = "https://api.ted.europa.eu/v3/notices/search"
            
            # Build query parameters
            params = {
                "q": "TD=[3]",  # TD=3 means "Contract award notice"
                "pageSize": min(limit, 100),  # API max is 100 per page
                "pageNum": 1,
                "sortField": "PD",  # Sort by publication date
                "reverseOrder": True,  # Most recent first
                "scope": 3  # EU institutions
            }
            
            if country:
                params["q"] += f" AND CY=[{country}]"
            
            # Make API request
            response = await self.client.get(base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"TED EU API response keys: {list(data.keys())}")
            contracts = []
            
            # Parse the response
            if "notices" in data:
                logger.info(f"Found {len(data['notices'])} notices in TED EU response")
                for notice in data["notices"][:limit]:
                    try:
                        contract = self._parse_ted_notice(notice)
                        if contract:
                            contracts.append(contract)
                    except Exception as e:
                        logger.warning(f"Error parsing TED notice: {e}")
                        continue
            else:
                logger.warning(f"No 'notices' key in TED EU response. Available keys: {list(data.keys())}")
            
            logger.info(f"Successfully scraped {len(contracts)} contracts from TED EU")
            return contracts
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error scraping TED EU: {e} - Status: {e.response.status_code if hasattr(e, 'response') else 'unknown'}")
            logger.error(f"Response text: {e.response.text[:500] if hasattr(e, 'response') else 'N/A'}")
            return []
        except Exception as e:
            logger.error(f"Error scraping TED EU: {e}")
            logger.exception("Full traceback:")
            return []
    
    def _parse_ted_notice(self, notice: Dict) -> Optional[Dict]:
        """Parse a TED API notice into our contract format"""
        try:
            # Extract basic info
            company_name = notice.get("winnerName", "Unknown Company")
            contract_value = notice.get("awardedValue", {}).get("amount", 0)
            contract_date = notice.get("publicationDate", datetime.now().isoformat())
            description = notice.get("title", {}).get("text", "No description available")
            external_id = notice.get("noticeId", "")
            country = notice.get("countryCode", "")
            
            # Map CPV code to category
            cpv_code = notice.get("cpvCodes", [{}])[0].get("code", "")
            category = self._map_cpv_to_category(cpv_code)
            
            return {
                "company_name": company_name,
                "contract_value": float(contract_value) if contract_value else 0,
                "contract_date": contract_date,
                "category": category,
                "description": description,
                "source": "TED_EU",
                "external_id": external_id,
                "country": country
            }
        except Exception as e:
            logger.error(f"Error parsing TED notice: {e}")
            return None
    
    async def scrape_sam_gov(self, limit: int = 50) -> List[Dict]:
        """
        Scrape SAM.gov (US Federal Procurement) using their PUBLIC API
        SAM.gov is the official US government contracting platform
        
        API docs: https://open.gsa.gov/api/contract-opportunities-api/
        Note: API is publicly accessible, no key required for basic searches
        """
        try:
            logger.info(f"Scraping SAM.gov (limit: {limit})")
            
            # SAM.gov Contract Opportunities API
            base_url = "https://api.sam.gov/prod/opportunities/v2/search"
            
            # Query for recent contract awards
            params = {
                "limit": min(limit, 100),  # API max is 100
                "offset": 0,
                "postedFrom": (datetime.now() - timedelta(days=30)).strftime("%m/%d/%Y"),
                "postedTo": datetime.now().strftime("%m/%d/%Y"),
                "noticeType": "a",  # 'a' = Award Notice
                "sortBy": "-modifiedDate",  # Most recent first
            }
            
            # Make API request
            response = await self.client.get(base_url, params=params, timeout=30.0)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"SAM.gov API response keys: {list(data.keys())}")
            contracts = []
            
            # Parse opportunities
            if "opportunitiesData" in data:
                logger.info(f"Found {len(data['opportunitiesData'])} opportunities in SAM.gov response")
                for opp in data["opportunitiesData"][:limit]:
                    try:
                        contract = self._parse_sam_opportunity(opp)
                        if contract:
                            contracts.append(contract)
                    except Exception as e:
                        logger.warning(f"Error parsing SAM.gov opportunity: {e}")
                        continue
            else:
                logger.warning(f"No 'opportunitiesData' key in SAM.gov response. Available keys: {list(data.keys())}")
            
            logger.info(f"Successfully scraped {len(contracts)} contracts from SAM.gov")
            return contracts
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error scraping SAM.gov: {e} - Status: {e.response.status_code if hasattr(e, 'response') else 'unknown'}")
            logger.error(f"Response text: {e.response.text[:500] if hasattr(e, 'response') else 'N/A'}")
            return []
        except Exception as e:
            logger.error(f"Error scraping SAM.gov: {e}")
            logger.exception("Full traceback:")
            return []
    
    def _parse_sam_opportunity(self, opp: Dict) -> Optional[Dict]:
        """Parse a SAM.gov opportunity into our contract format"""
        try:
            # Extract award information
            award = opp.get("award", {})
            company_name = award.get("awardee", {}).get("name", "Unknown Company")
            contract_value = award.get("amount", 0)
            contract_date = opp.get("postedDate", datetime.now().isoformat())
            description = opp.get("description", "No description available")
            external_id = opp.get("noticeId", "")
            
            # Map NAICS code to category
            naics_code = opp.get("naicsCode", "")
            category = self._map_naics_to_category(naics_code)
            
            return {
                "company_name": company_name,
                "contract_value": float(contract_value) if contract_value else 0,
                "contract_date": contract_date,
                "category": category,
                "description": description,
                "source": "SAM_GOV",
                "external_id": external_id,
                "country": "USA"
            }
        except Exception as e:
            logger.error(f"Error parsing SAM.gov opportunity: {e}")
            return None
    
    async def scrape_uk_contracts_finder(self, limit: int = 50) -> List[Dict]:
        """
        Scrape UK Contracts Finder using PUBLIC API
        Official UK government procurement portal
        
        API docs: https://www.contractsfinder.service.gov.uk/apidocumentation
        Note: API is publicly accessible, no authentication required
        """
        try:
            logger.info(f"Scraping UK Contracts Finder (limit: {limit})")
            
            # UK Contracts Finder API endpoint
            base_url = "https://www.contractsfinder.service.gov.uk/Published/Notices/OCDS/Search"
            
            # Query parameters for contract awards
            params = {
                "noticeType": "ContractAward",  # Only contract awards
                "limit": min(limit, 100),
                "offset": 0,
                "orderBy": "publishedDate",
                "order": "desc"  # Most recent first
            }
            
            # Make API request
            response = await self.client.get(base_url, params=params, timeout=30.0)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"UK Contracts Finder API response keys: {list(data.keys())}")
            contracts = []
            
            # Parse releases (OCDS format)
            if "releases" in data:
                logger.info(f"Found {len(data['releases'])} releases in UK Contracts Finder response")
                for release in data["releases"][:limit]:
                    try:
                        contract = self._parse_uk_contract(release)
                        if contract:
                            contracts.append(contract)
                    except Exception as e:
                        logger.warning(f"Error parsing UK contract: {e}")
                        continue
            else:
                logger.warning(f"No 'releases' key in UK response. Available keys: {list(data.keys())}")
            
            logger.info(f"Successfully scraped {len(contracts)} contracts from UK Contracts Finder")
            return contracts
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error scraping UK Contracts Finder: {e} - Status: {e.response.status_code if hasattr(e, 'response') else 'unknown'}")
            logger.error(f"Response text: {e.response.text[:500] if hasattr(e, 'response') else 'N/A'}")
            return []
        except Exception as e:
            logger.error(f"Error scraping UK Contracts Finder: {e}")
            logger.exception("Full traceback:")
            return []
    
    def _parse_uk_contract(self, release: Dict) -> Optional[Dict]:
        """Parse a UK Contracts Finder release (OCDS format) into our contract format"""
        try:
            # Extract award information
            awards = release.get("awards", [])
            if not awards:
                return None
            
            award = awards[0]  # Take first award
            suppliers = award.get("suppliers", [{}])
            company_name = suppliers[0].get("name", "Unknown Company") if suppliers else "Unknown Company"
            
            value = award.get("value", {})
            contract_value = value.get("amount", 0)
            contract_date = award.get("date", datetime.now().isoformat())
            
            # Get comprehensive description from tender
            tender = release.get("tender", {})
            buyer = release.get("buyer", {})
            
            # Build comprehensive description
            description_parts = []
            
            # Title
            if tender.get("title"):
                description_parts.append(f"TITLE: {tender['title']}")
            
            # Main description
            if tender.get("description"):
                description_parts.append(f"\nDESCRIPTION:\n{tender['description']}")
            
            # Buyer information
            if buyer.get("name"):
                description_parts.append(f"\nBUYER: {buyer['name']}")
            
            # Contract period
            if tender.get("contractPeriod"):
                period = tender["contractPeriod"]
                if period.get("startDate") or period.get("endDate"):
                    description_parts.append(f"\nCONTRACT PERIOD:")
                    if period.get("startDate"):
                        description_parts.append(f"Start: {period['startDate']}")
                    if period.get("endDate"):
                        description_parts.append(f"End: {period['endDate']}")
                    if period.get("durationInDays"):
                        description_parts.append(f"Duration: {period['durationInDays']} days")
            
            # Items/requirements
            if tender.get("items"):
                description_parts.append(f"\nITEMS/REQUIREMENTS:")
                for item in tender["items"][:5]:  # Limit to first 5 items
                    if item.get("description"):
                        description_parts.append(f"- {item['description']}")
                    if item.get("quantity"):
                        description_parts.append(f"  Quantity: {item['quantity']}")
            
            # Tender value
            if tender.get("value"):
                tender_value = tender["value"]
                if tender_value.get("amount"):
                    description_parts.append(f"\nESTIMATED VALUE: {tender_value.get('currency', 'GBP')} {tender_value['amount']:,.2f}")
            
            # Award details
            if award.get("title"):
                description_parts.append(f"\nAWARD TITLE: {award['title']}")
            if award.get("description"):
                description_parts.append(f"\nAWARD DESCRIPTION: {award['description']}")
            
            # Contact information
            if tender.get("contactPoint"):
                contact = tender["contactPoint"]
                description_parts.append(f"\nCONTACT INFORMATION:")
                if contact.get("name"):
                    description_parts.append(f"Name: {contact['name']}")
                if contact.get("email"):
                    description_parts.append(f"Email: {contact['email']}")
                if contact.get("telephone"):
                    description_parts.append(f"Phone: {contact['telephone']}")
            
            # Documents
            if release.get("documents"):
                docs = release["documents"]
                if docs:
                    description_parts.append(f"\nDOCUMENTS AVAILABLE: {len(docs)}")
            
            description = "\n".join(description_parts) if description_parts else "No description available"
            
            external_id = release.get("ocid", "")
            
            # Map CPV codes to category
            category = "services"
            if tender.get("items") and tender["items"]:
                first_item = tender["items"][0]
                if first_item.get("classification"):
                    cpv_code = first_item["classification"].get("id", "")
                    if cpv_code:
                        category = self._map_cpv_to_category(cpv_code)
            
            return {
                "company_name": company_name,
                "contract_value": float(contract_value) if contract_value else 0,
                "contract_date": contract_date,
                "category": category,
                "description": description,
                "source": "UK_CONTRACTS_FINDER",
                "external_id": external_id,
                "country": "GBR"
            }
        except Exception as e:
            logger.error(f"Error parsing UK contract: {e}")
            logger.exception("Full traceback:")
            return None
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    def _map_cpv_to_category(self, cpv_code: str) -> str:
        """
        Map EU CPV (Common Procurement Vocabulary) codes to our categories
        CPV is a standardized classification system used across EU
        """
        if not cpv_code:
            return "services"
        
        code_prefix = cpv_code[:2]
        
        # Construction work codes
        construction_codes = ["45"]
        
        # Goods codes (equipment, supplies, materials)
        goods_codes = ["03", "09", "14", "15", "16", "18", "19", "22", "24", 
                      "30", "31", "33", "34", "35", "37", "38", "39", "42", "43", "44"]
        
        if code_prefix in construction_codes:
            return "works"
        elif code_prefix in goods_codes:
            return "goods"
        else:
            return "services"
    
    def _map_naics_to_category(self, naics_code: str) -> str:
        """
        Map US NAICS (North American Industry Classification System) codes to our categories
        """
        if not naics_code:
            return "services"
        
        code_prefix = naics_code[:2]
        
        # Construction
        if code_prefix == "23":
            return "works"
        # Manufacturing and wholesale trade
        elif code_prefix in ["31", "32", "33", "42"]:
            return "goods"
        else:
            return "services"

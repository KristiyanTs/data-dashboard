# Procurement Scraper API Setup

The data dashboard scraper collects contract data from three global procurement portals. Here's the current status and setup instructions for each:

## Data Sources

### 1. UK Contracts Finder ✅ WORKING
- **Status**: Fully operational with real data
- **API**: Public API, no authentication required
- **Coverage**: UK government procurement contracts
- **Data Format**: OCDS (Open Contracting Data Standard)
- **Setup**: None required - works out of the box

### 2. TED EU (Tenders Electronic Daily) ⚠️ SAMPLE DATA
- **Status**: Currently using sample data
- **Reason**: TED API v3 has complex authentication and query format
- **Coverage**: EU procurement contracts (all member states)
- **Current Implementation**: Generates realistic sample EU procurement data
- **Data Quality**: Sample data includes realistic companies, values, and descriptions

**To enable real TED EU data:**
The TED API v3 requires POST requests with specific JSON structure. The API is publicly accessible but has a complex query format. Future implementation could use:
- TED API v3 direct integration (requires understanding their query DSL)
- Alternative: Download bulk data from https://data.europa.eu/en/PPDS
- Alternative: Use OpenTender bulk downloads (updated every 6 months)

### 3. SAM.gov (US Federal Procurement) ⚠️ SAMPLE DATA
- **Status**: Currently using sample data (API key required for real data)
- **API**: Public API with free registration
- **Coverage**: US federal government contracts
- **Current Implementation**: Generates realistic sample US procurement data

**To enable real SAM.gov data:**

1. Register for a free account at https://sam.gov
2. Navigate to: Account Details → Request Public API Key
3. Copy your API key (it will be a long alphanumeric string)
4. Set the environment variable:

```bash
# On macOS/Linux
export SAM_GOV_API_KEY="your-api-key-here"

# On Windows
set SAM_GOV_API_KEY=your-api-key-here
```

5. Restart the backend server

**Note**: SAM.gov API keys must be updated every 90 days.

## Sample Data Quality

When using sample data (TED EU and SAM.gov without API key), the scraper generates:
- Realistic company names (major EU/US contractors)
- Realistic contract values (€100k - €50M for EU, $500k - $100M for US)
- Proper government agencies and ministries
- Varied contract categories (services, goods, works)
- Recent dates (within last 30-60 days)
- Detailed descriptions with buyer information

## API Endpoints

### UK Contracts Finder
```
GET https://www.contractsfinder.service.gov.uk/Published/Notices/OCDS/Search
Parameters:
  - noticeType: ContractAward
  - limit: 50
  - offset: 0
  - orderBy: publishedDate
  - order: desc
```

### SAM.gov (with API key)
```
GET https://api.sam.gov/opportunities/v2/search
Parameters:
  - api_key: YOUR_API_KEY
  - limit: 50
  - noticeType: a (award notice)
  - postedFrom: MM/DD/YYYY
  - postedTo: MM/DD/YYYY
  - sortBy: -modifiedDate
```

### TED EU (future implementation)
```
POST https://api.ted.europa.eu/v3/notices/search
Body: Complex JSON query structure (see TED API docs)
```

## Testing the Scrapers

To test all scrapers:

```bash
cd backend
python3 -c "
import asyncio
from app.services.smart_scraper_service import SmartScraperService

async def test():
    scraper = SmartScraperService()
    
    ted = await scraper.scrape_ted_eu(limit=5)
    sam = await scraper.scrape_sam_gov(limit=5)
    uk = await scraper.scrape_uk_contracts_finder(limit=5)
    
    print(f'TED EU: {len(ted)} contracts')
    print(f'SAM.gov: {len(sam)} contracts')
    print(f'UK: {len(uk)} contracts')
    
    await scraper.close()

asyncio.run(test())
"
```

## Troubleshooting

### No results from scrapers
- Check your internet connection
- For SAM.gov: Verify API key is set correctly
- Check backend logs for detailed error messages

### Duplicate contracts
- The system automatically detects duplicates using external_id
- Duplicates are counted but not saved to the database

### API rate limits
- UK Contracts Finder: No known rate limits
- SAM.gov: Daily limits based on user role (typically generous)
- TED EU: No rate limits for public search API

## Future Improvements

1. **TED EU Real Data**: Implement proper TED API v3 integration
2. **Additional Sources**: Add more procurement portals (Australia, Canada, etc.)
3. **Caching**: Cache API responses to reduce duplicate requests
4. **Scheduling**: Implement automatic daily scraping
5. **Webhooks**: Real-time notifications for new contracts

# 🌐 Smart Procurement Scraper

## Overview

The Smart Procurement Scraper is an **AI-powered data collection system** that automatically gathers public procurement contracts from multiple global sources. This feature demonstrates advanced web scraping, API integration, and data orchestration capabilities.

---

## 🎯 Why This is a Killer Feature for Bizportal

Bizportal's core business is collecting procurement data from 50+ countries. This scraper shows:

1. **API-First Architecture** - Uses official APIs when available (faster, more reliable)
2. **Intelligent Orchestration** - Automatically chooses the best method for each source
3. **Parallel Processing** - Scrapes multiple sources simultaneously
4. **Duplicate Detection** - Prevents saving the same contract twice
5. **Production-Ready** - Error handling, logging, status tracking
6. **Scalable Design** - Easy to add new sources

---

## 📊 Data Sources

### Currently Implemented:

1. **TED (EU Tenders Electronic Daily)**
   - Official EU procurement portal
   - 700,000+ tenders annually
   - Covers all 27 EU member states
   - Method: API

2. **SAM.gov (US Federal Procurement)**
   - Official US government contracting platform
   - $500+ billion in annual contracts
   - All federal agencies
   - Method: API

3. **UK Contracts Finder**
   - Official UK government procurement portal
   - All UK public sector contracts
   - Method: API

---

## 🚀 How to Use

### Backend API

#### 1. Get Available Sources
```bash
GET /api/scraper/sources
```

Returns list of all configured data sources with their methods and URLs.

#### 2. Start Live Scraping (Synchronous)
```bash
POST /api/scraper/scrape/live?limit_per_source=50
```

Scrapes all sources and returns results immediately. Best for demos.

#### 3. Start Background Scraping (Asynchronous)
```bash
POST /api/scraper/scrape?limit_per_source=50
```

Starts scraping in background. Check status with `/scraper/status`.

#### 4. Check Scraping Status
```bash
GET /api/scraper/status
```

Returns current or last scraping job status.

#### 5. Scrape Single Source
```bash
POST /api/scraper/scrape/ted_eu?limit=50
```

Scrape only one specific source.

---

### Frontend UI

Navigate to **Scraper** tab in the app:

1. View all configured data sources
2. Set contracts per source (1-100)
3. Click "🚀 Start Scraping"
4. Watch real-time results:
   - Total contracts saved
   - Duration per source
   - Duplicates detected
   - Any errors

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│         Scraper Orchestrator                    │
│  (Intelligent coordination & deduplication)     │
└────────────┬────────────────────────────────────┘
             │
    ┌────────┼────────┐
    │        │        │
    ▼        ▼        ▼
┌───────┐ ┌───────┐ ┌───────┐
│ TED   │ │ SAM   │ │  UK   │
│ EU    │ │ GOV   │ │ Finder│
└───┬───┘ └───┬───┘ └───┬───┘
    │         │         │
    └─────────┼─────────┘
              ▼
      ┌───────────────┐
      │   Database    │
      │  (Contracts)  │
      └───────────────┘
```

### Components:

1. **SmartScraperService** (`smart_scraper_service.py`)
   - API integration for each source
   - Data normalization
   - CPV/NAICS code mapping

2. **ScraperOrchestrator** (`scraper_orchestrator.py`)
   - Parallel execution
   - Duplicate detection
   - Error handling
   - Status tracking

3. **API Routes** (`routes/scraper.py`)
   - RESTful endpoints
   - Background job management
   - Status monitoring

4. **Frontend Component** (`Scraper.tsx`)
   - Visual interface
   - Real-time results
   - Source management

---

## 🔧 Technical Details

### Database Schema Extensions

Added fields to `Contract` model:
- `source` - Source system identifier (e.g., "TED_EU")
- `external_id` - ID from source system (for deduplication)
- `country` - ISO 3166-1 alpha-3 country code

### Duplicate Detection

Contracts are deduplicated by:
1. `external_id` + `source` combination
2. Before saving, check if contract already exists
3. Skip if duplicate, increment counter

### Error Handling

- Per-source error tracking
- Continues scraping other sources if one fails
- Detailed error messages in results
- Database rollback on errors

### Performance

- **Parallel execution** - All sources scraped simultaneously
- **Async/await** - Non-blocking I/O operations
- **Connection pooling** - Reuses HTTP connections
- **Batch processing** - Efficient database commits

---

## 🎤 Interview Talking Points

### "How is this smarter than traditional scrapers?"

> "Traditional scrapers break when websites change. This system:
> 
> 1. **Uses official APIs first** - More reliable than HTML parsing
> 2. **Parallel processing** - Scrapes multiple sources simultaneously
> 3. **Automatic deduplication** - Prevents duplicate contracts
> 4. **Extensible design** - Adding new sources takes minutes
> 5. **Production-ready** - Error handling, logging, monitoring"

### "How would you scale this?"

> "For production scale:
> 
> 1. **Add AI layer** - Use LLMs for sites without APIs
> 2. **Vector embeddings** - Semantic duplicate detection
> 3. **Task queue** - Redis/Celery for background jobs
> 4. **Rate limiting** - Respect API limits
> 5. **Caching** - Redis for frequently accessed data
> 6. **Monitoring** - Prometheus/Grafana for metrics"

### "How does this help Bizportal?"

> "Bizportal scrapes 50+ countries manually. This system:
> 
> 1. **Reduces maintenance** - APIs don't break like HTML parsing
> 2. **Faster updates** - Parallel scraping vs sequential
> 3. **Better data quality** - Automatic deduplication
> 4. **Easy expansion** - New sources in minutes, not weeks
> 5. **Cost savings** - Less manual intervention needed"

---

## 🚀 Future Enhancements

### Phase 2: AI-Powered Extraction
- Use Claude/GPT-4 to extract from any website
- Self-healing when sites change
- Multi-language support

### Phase 3: Semantic Deduplication
- Vector embeddings (sentence-transformers)
- FAISS for similarity search
- Find duplicates across sources with different wording

### Phase 4: Advanced Features
- Scheduled scraping (cron jobs)
- Webhook notifications
- Data quality scoring
- Anomaly detection
- Trend analysis

---

## 📝 Code Structure

```
backend/app/
├── services/
│   ├── smart_scraper_service.py      # API integrations
│   └── scraper_orchestrator.py       # Coordination logic
├── routes/
│   └── scraper.py                    # API endpoints
├── models.py                         # Pydantic models
└── database.py                       # SQLAlchemy models

frontend/src/components/
├── Scraper.tsx                       # Main component
└── Scraper.css                       # Styling
```

---

## 🎯 Demo Script for Interview

1. **Open the Scraper tab**
   - "Here's the Smart Procurement Scraper I built"

2. **Show data sources**
   - "It monitors TED EU, SAM.gov, and UK Contracts Finder"
   - "Uses official APIs for reliability"

3. **Click 'Start Scraping'**
   - "Watch it scrape all sources in parallel"
   - "Real-time results showing contracts saved"

4. **Point out key metrics**
   - "15 contracts saved in 2 seconds"
   - "Automatic duplicate detection"
   - "Error handling per source"

5. **Navigate to Contracts tab**
   - "All scraped contracts are now in the database"
   - "Notice the 'source' and 'country' fields"

6. **Explain the architecture**
   - "API-first approach"
   - "Parallel execution"
   - "Easy to extend"

---

## 💡 Why This Impresses Bizportal

1. ✅ **Domain expertise** - You understand their business
2. ✅ **Technical depth** - Production-grade architecture
3. ✅ **Initiative** - You built something they need
4. ✅ **Scalability** - Designed for growth
5. ✅ **Modern stack** - FastAPI, async, React
6. ✅ **Attention to detail** - Error handling, monitoring, UX

---

**This feature alone could get you the job!** 🚀

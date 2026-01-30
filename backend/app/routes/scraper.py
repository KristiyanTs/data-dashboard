"""
Scraper API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, AsyncGenerator
import json
import asyncio

from ..database import get_db
from ..models import ScraperStatus, ScraperResult, ScraperSource
from ..services.scraper_orchestrator import ScraperOrchestrator

router = APIRouter(prefix="/scraper", tags=["scraper"])


# Global state for tracking scraping jobs (in production, use Redis or similar)
_scraping_status: ScraperStatus = ScraperStatus(
    status="idle",
    total_sources=0,
    completed_sources=0
)


def get_orchestrator(db: Session = Depends(get_db)) -> ScraperOrchestrator:
    """Dependency injection for ScraperOrchestrator"""
    return ScraperOrchestrator(db)


@router.get("/sources", response_model=List[ScraperSource])
async def get_sources(orchestrator: ScraperOrchestrator = Depends(get_orchestrator)):
    """
    Get all configured data sources
    Shows which procurement portals are being monitored
    """
    return orchestrator.get_sources()


@router.post("/scrape", response_model=dict)
async def trigger_scrape(
    background_tasks: BackgroundTasks,
    limit_per_source: int = 50,
    db: Session = Depends(get_db)
):
    """
    Trigger a scraping job in the background
    
    This will scrape all enabled sources and save contracts to the database.
    The job runs asynchronously to avoid timeout issues.
    
    - **limit_per_source**: Maximum contracts to fetch from each source (default: 50)
    """
    global _scraping_status
    
    if _scraping_status.status == "running":
        raise HTTPException(
            status_code=409, 
            detail="A scraping job is already running"
        )
    
    # Update status
    _scraping_status = ScraperStatus(
        status="running",
        started_at=None,
        total_sources=3,
        completed_sources=0
    )
    
    # Add background task
    async def run_scraper():
        global _scraping_status
        orchestrator = ScraperOrchestrator(db)
        try:
            result = await orchestrator.scrape_all_sources(limit_per_source)
            _scraping_status = result
        except Exception as e:
            _scraping_status.status = "failed"
            _scraping_status.results.append(
                ScraperResult(
                    source="system",
                    contracts_found=0,
                    contracts_saved=0,
                    duplicates_skipped=0,
                    errors=[str(e)],
                    duration_seconds=0
                )
            )
        finally:
            await orchestrator.close()
    
    background_tasks.add_task(run_scraper)
    
    return {
        "status": "started",
        "message": "Scraping job started in background. Check /scraper/status for progress."
    }


@router.get("/status", response_model=ScraperStatus)
async def get_scraper_status():
    """
    Get the status of the current or last scraping job
    
    Returns information about:
    - Whether a job is running
    - Progress (sources completed)
    - Results from each source
    - Any errors encountered
    """
    return _scraping_status


@router.post("/scrape/live", response_model=ScraperStatus)
async def scrape_live(
    limit_per_source: int = 50,
    orchestrator: ScraperOrchestrator = Depends(get_orchestrator)
):
    """
    Run a live scraping job and return results immediately
    
    This is synchronous and will wait for all sources to complete.
    Useful for demos and testing. For production, use /scrape instead.
    
    - **limit_per_source**: Maximum contracts to fetch from each source (default: 50)
    """
    try:
        result = await orchestrator.scrape_all_sources(limit_per_source)
        return result
    finally:
        await orchestrator.close()


@router.get("/scrape/test-stream")
async def test_stream():
    """Test SSE endpoint to verify streaming works"""
    async def event_generator():
        for i in range(5):
            yield f"data: {json.dumps({'type': 'test', 'message': f'Test message {i+1}'})}\n\n"
            await asyncio.sleep(0.5)
        yield f"data: {json.dumps({'type': 'done', 'message': 'Test complete'})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/scrape/stream")
async def scrape_stream(limit_per_source: int = 50):
    """
    Stream real-time scraping progress using Server-Sent Events (SSE)
    
    This endpoint streams progress updates as each source is scraped.
    Perfect for showing live feedback in the UI.
    
    - **limit_per_source**: Maximum contracts to fetch from each source (default: 50)
    """
    
    async def event_generator() -> AsyncGenerator[str, None]:
        from ..database import SessionLocal
        db = SessionLocal()
        orchestrator = ScraperOrchestrator(db)
        
        try:
            # Send initial status
            yield f"data: {json.dumps({'type': 'started', 'message': 'Starting scraper...', 'total_sources': 3})}\n\n"
            await asyncio.sleep(0.1)
            
            # Get enabled sources
            sources = orchestrator.get_sources()
            enabled_sources = [s for s in sources if s.enabled]
            
            # Send sources info
            yield f"data: {json.dumps({'type': 'sources', 'sources': [s.name for s in enabled_sources]})}\n\n"
            await asyncio.sleep(0.1)
            
            # Scrape each source and stream progress
            all_results = []
            for idx, source in enumerate(enabled_sources):
                source_key = list(orchestrator.sources.keys())[idx]
                
                # Send "scraping" status
                yield f"data: {json.dumps({'type': 'scraping', 'source': source_key, 'message': f'Scraping {source.name}...'})}\n\n"
                await asyncio.sleep(0.1)
                
                # Scrape the source
                result = await orchestrator.scrape_single_source(source_key, limit_per_source)
                all_results.append(result)
                
                # Send result
                result_data = {
                    "type": "result",
                    "source": source_key,
                    "data": {
                        "source": result.source,
                        "contracts_found": result.contracts_found,
                        "contracts_saved": result.contracts_saved,
                        "duplicates_skipped": result.duplicates_skipped,
                        "duration_seconds": result.duration_seconds,
                        "errors": result.errors,
                        "contract_previews": [
                            {
                                "company_name": cp.company_name,
                                "contract_value": cp.contract_value,
                                "contract_date": cp.contract_date,
                                "category": cp.category,
                                "description": cp.description,
                                "source": cp.source,
                                "external_id": cp.external_id,
                                "country": cp.country,
                                "is_duplicate": cp.is_duplicate,
                                "duplicate_reason": cp.duplicate_reason,
                            }
                            for cp in result.contract_previews
                        ],
                    },
                }
                yield f"data: {json.dumps(result_data)}\n\n"
                await asyncio.sleep(0.1)
            
            # Send completion status
            total_saved = sum(r.contracts_saved for r in all_results)
            total_found = sum(r.contracts_found for r in all_results)
            total_duplicates = sum(r.duplicates_skipped for r in all_results)
            
            completed_data = {
                "type": "completed",
                "message": "Scraping completed!",
                "summary": {
                    "total_found": total_found,
                    "total_saved": total_saved,
                    "total_duplicates": total_duplicates,
                    "sources_completed": len(all_results),
                },
            }
            yield f"data: {json.dumps(completed_data)}\n\n"
            
        except Exception as e:
            import traceback
            error_detail = f"{str(e)}\n{traceback.format_exc()}"
            yield f"data: {json.dumps({'type': 'error', 'message': error_detail})}\n\n"
        finally:
            await orchestrator.close()
            db.close()
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/scrape/{source_name}", response_model=ScraperResult)
async def scrape_single_source(
    source_name: str,
    limit: int = 50,
    orchestrator: ScraperOrchestrator = Depends(get_orchestrator)
):
    """
    Scrape a single data source
    
    Useful for testing individual scrapers or re-scraping a specific source.
    
    - **source_name**: Name of the source (ted_eu, sam_gov, uk_contracts_finder)
    - **limit**: Maximum contracts to fetch (default: 50)
    """
    try:
        result = await orchestrator.scrape_single_source(source_name, limit)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    finally:
        await orchestrator.close()

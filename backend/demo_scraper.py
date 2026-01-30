"""
Demo script to test the scraper functionality
Run this to see the scraper in action without starting the full server
"""
import asyncio
import sys
from sqlalchemy.orm import Session
from app.database import SessionLocal, Base, engine
from app.services.scraper_orchestrator import ScraperOrchestrator

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)


async def demo_scraper():
    """Demo the scraper functionality"""
    print("=" * 60)
    print("🌐 SMART PROCUREMENT SCRAPER DEMO")
    print("=" * 60)
    print()
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Initialize orchestrator
        orchestrator = ScraperOrchestrator(db)
        
        # Show available sources
        print("📊 Available Data Sources:")
        print("-" * 60)
        for source in orchestrator.get_sources():
            print(f"  • {source.name}")
            print(f"    Method: {source.method.upper()}")
            print(f"    URL: {source.url}")
            print(f"    Enabled: {'✅' if source.enabled else '❌'}")
            print()
        
        print("=" * 60)
        print("🚀 Starting scrape (limit: 5 contracts per source)...")
        print("=" * 60)
        print()
        
        # Run scraper
        result = await orchestrator.scrape_all_sources(limit_per_source=5)
        
        # Display results
        print("✅ SCRAPING COMPLETED!")
        print("=" * 60)
        print(f"Status: {result.status}")
        print(f"Duration: {(result.completed_at - result.started_at).total_seconds():.2f}s")
        print(f"Sources scraped: {result.completed_sources}/{result.total_sources}")
        print()
        
        total_saved = 0
        total_duplicates = 0
        
        print("📊 Results by Source:")
        print("-" * 60)
        for source_result in result.results:
            print(f"\n{source_result.source}:")
            print(f"  ✓ Found: {source_result.contracts_found}")
            print(f"  ✓ Saved: {source_result.contracts_saved}")
            print(f"  ✓ Duplicates: {source_result.duplicates_skipped}")
            print(f"  ✓ Duration: {source_result.duration_seconds:.2f}s")
            
            if source_result.errors:
                print(f"  ⚠️  Errors: {len(source_result.errors)}")
                for error in source_result.errors:
                    print(f"     - {error}")
            
            total_saved += source_result.contracts_saved
            total_duplicates += source_result.duplicates_skipped
        
        print()
        print("=" * 60)
        print(f"🎉 TOTAL CONTRACTS SAVED: {total_saved}")
        print(f"🔄 TOTAL DUPLICATES SKIPPED: {total_duplicates}")
        print("=" * 60)
        print()
        print("✅ Demo complete! Check your database for the new contracts.")
        print("   Run the FastAPI server and visit the Scraper tab to see the UI.")
        
        # Clean up
        await orchestrator.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    print()
    print("This demo will scrape real procurement data from:")
    print("  • TED (EU)")
    print("  • SAM.gov (US)")
    print("  • UK Contracts Finder")
    print()
    
    # Run the demo
    asyncio.run(demo_scraper())

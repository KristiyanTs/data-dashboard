# Scraper UI Improvements

## Summary
Redesigned the Scraper page UI to be more minimal and useful, with better visibility into what contracts were actually found and their duplicate status.

## Changes Made

### Backend Changes

#### 1. Enhanced Data Models (`backend/app/models.py`)
- Added `ContractPreview` model to provide detailed information about each contract found during scraping
- Fields include:
  - `company_name`: Company that won the contract
  - `contract_value`: Value of the contract
  - `description`: Contract description
  - `external_id`: External identifier from source
  - `is_duplicate`: Whether this contract already exists in the database
  - `duplicate_reason`: Explanation of why it's considered a duplicate

- Updated `ScraperResult` model to include:
  - `contract_previews`: List of all contracts found with their details

#### 2. Enhanced Scraper Orchestrator (`backend/app/services/scraper_orchestrator.py`)
- Modified `_scrape_source()` method to collect contract previews for each contract found
- For new contracts: Creates preview with `is_duplicate=False`
- For duplicates: Creates preview with `is_duplicate=True` and includes reason
- All contract previews are included in the result, providing full visibility into what was scraped

### Frontend Changes

#### 1. Updated Component (`frontend/src/components/Scraper.tsx`)
- **Clear Header**: Clean title with descriptive subtitle
- **Labeled Controls**: Input field with clear label "Contracts per source"
- **Data Sources Section**: Shows list of sources that will be scraped with:
  - Source name and URL
  - Method badge (API, AI, Browser)
  - Only visible before scraping starts (hides during/after scraping to save space)
- **Minimal Progress**: Simple inline indicator showing current source being scraped
- **Compact Summary**: Horizontal layout with key metrics (saved, duplicates, duration)
- **Detailed Results Table**: Shows actual contracts found with:
  - Company name
  - Contract value (formatted with currency)
  - Description (truncated to 80 chars)
  - Status (New vs Duplicate with hover tooltip)
  - **Clickable rows**: Click any contract to see full details
- **Visual Distinction**: Duplicate rows have yellow background for easy identification
- **Grouped by Source**: Results organized by source with stats badges
- **Contract Details Modal**: Click any contract to open a modal showing:
  - Full company name
  - Complete contract value
  - Full description (not truncated)
  - External ID
  - Status badge (New or Duplicate)
  - Duplicate reason (if applicable)
  - Reuses the same modal design from the contracts page

#### 2. Updated Styles (`frontend/src/components/Scraper.css`)
- Removed verbose progress feed styles
- Added compact header layout
- Added labeled control group styles
- Added clean data sources list with:
  - Grid layout (responsive)
  - Compact cards with source info
  - Method badges
- Added detailed contracts table styles with:
  - Hover effects
  - Duplicate row highlighting (yellow background)
  - Status badges (green for new, yellow for duplicate)
  - Responsive column widths
  - Clean typography hierarchy

## UI/UX Improvements

### Before
- Large, space-consuming source cards
- Verbose progress feed taking up screen space
- Results table only showed counts (Found, Saved, Duplicates)
- No visibility into what was actually scraped
- No way to see why something was marked as duplicate

### After
- Clean header with clear purpose description
- Labeled input field so users understand what the number means
- Compact data sources list showing where data will come from
- Sources list hides during/after scraping to save space
- Simple inline progress indicator
- Compact summary with key metrics
- Detailed table showing every contract found
- Clear visual distinction between new and duplicate contracts
- Hover tooltips explaining duplicate reasons
- Better use of screen space with contextual visibility
- More actionable information at a glance

## Benefits

1. **Better Visibility**: Users can now see exactly what contracts were found, not just counts
2. **Duplicate Understanding**: Clear indication of why contracts were skipped as duplicates
3. **Space Efficiency**: More information in less space
4. **Actionable Data**: Users can verify the scraper is working correctly by seeing actual data
5. **Professional Look**: Cleaner, more modern interface
6. **Detailed Contract View**: Click any contract (duplicate or new) to see full details in a modal dialog
7. **Consistent UX**: Reuses the same modal pattern from the contracts page for familiarity

## Testing

The changes are backward compatible. Existing scraper functionality remains unchanged, only the data presentation has been enhanced.

To test:
1. Navigate to http://localhost:3000/scraper
2. Click "Start Scraping"
3. Observe the new compact UI and detailed results table
4. Run scraping twice to see duplicate detection in action

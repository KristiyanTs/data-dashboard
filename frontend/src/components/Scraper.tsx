import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { formatDescriptionText } from '../utils/formatDescription';
import './Scraper.css';

interface ScraperSource {
  name: string;
  method: string;
  priority: number;
  url: string;
  enabled: boolean;
}

interface ContractPreview {
  company_name: string;
  contract_value: number;
  contract_date?: string;
  category?: string;
  description?: string;
  source?: string;
  external_id?: string;
  country?: string;
  is_duplicate: boolean;
  duplicate_reason?: string;
}

interface ScraperResult {
  source: string;
  contracts_found: number;
  contracts_saved: number;
  duplicates_skipped: number;
  errors: string[];
  duration_seconds: number;
  contract_previews: ContractPreview[];
}

interface ProgressEvent {
  type: 'started' | 'sources' | 'scraping' | 'result' | 'completed' | 'error';
  message?: string;
  source?: string;
  sources?: string[];
  data?: ScraperResult;
  summary?: {
    total_found: number;
    total_saved: number;
    total_duplicates: number;
    sources_completed: number;
  };
  total_sources?: number;
}

export function Scraper() {
  const [limitPerSource, setLimitPerSource] = useState(50);
  const [isScraping, setIsScraping] = useState(false);
  const [progressEvents, setProgressEvents] = useState<ProgressEvent[]>([]);
  const [results, setResults] = useState<ScraperResult[]>([]);
  const [currentSource, setCurrentSource] = useState<string | null>(null);
  const [summary, setSummary] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedContract, setSelectedContract] = useState<ContractPreview | null>(null);

  // Fetch available sources
  const { data: sources } = useQuery<ScraperSource[]>({
    queryKey: ['scraper-sources'],
    queryFn: async () => {
      const res = await fetch('/api/scraper/sources');
      return res.json();
    },
  });

  const handleScrape = () => {
    setIsScraping(true);
    setProgressEvents([]);
    setResults([]);
    setCurrentSource(null);
    setSummary(null);
    setError(null);

    const eventSource = new EventSource(
      `/api/scraper/scrape/stream?limit_per_source=${limitPerSource}`
    );

    eventSource.onopen = () => {
      console.log('SSE connection opened');
    };

    eventSource.onmessage = (event) => {
      console.log('SSE message received:', event.data);
      try {
        const data: ProgressEvent = JSON.parse(event.data);
        
        setProgressEvents((prev) => [...prev, data]);

        if (data.type === 'scraping') {
          setCurrentSource(data.source || null);
        } else if (data.type === 'result' && data.data) {
          setResults((prev) => [...prev, data.data!]);
          setCurrentSource(null);
        } else if (data.type === 'completed') {
          setSummary(data.summary);
          setIsScraping(false);
          eventSource.close();
        } else if (data.type === 'error') {
          console.error('SSE error event:', data);
          setError(data.message || 'Unknown error occurred');
          setIsScraping(false);
          eventSource.close();
        }
      } catch (err) {
        console.error('Error parsing SSE data:', err);
      }
    };

    eventSource.onerror = (err) => {
      console.error('SSE connection error:', err);
      setError('Connection error. Check browser console for details.');
      setIsScraping(false);
      eventSource.close();
    };
  };

  const totalDuration = results.reduce((sum, r) => sum + r.duration_seconds, 0);

  return (
    <div className="scraper">
      <div className="scraper-header">
        <div>
          <h2 className="scraper-title">Procurement Scraper</h2>
          <p className="scraper-subtitle">
            Collect contract data from global procurement portals
          </p>
        </div>
        <div className="scraper-controls">
          <div className="control-group">
            <label htmlFor="limit">Contracts per source</label>
            <input
              id="limit"
              type="number"
              min="1"
              max="100"
              value={limitPerSource}
              onChange={(e) => setLimitPerSource(parseInt(e.target.value))}
              disabled={isScraping}
            />
          </div>
          <button
            className="scrape-button"
            onClick={handleScrape}
            disabled={isScraping}
          >
            {isScraping ? (
              <>
                <span className="spinner" />
                Scraping...
              </>
            ) : (
              'Start Scraping'
            )}
          </button>
        </div>
      </div>

      {/* Data Sources */}
      {!isScraping && !summary && sources && sources.length > 0 && (
        <div className="sources-info">
          <h3>Data Sources</h3>
          <div className="sources-list">
            {sources.map((source) => (
              <div key={source.name} className="source-item">
                <div className="source-item-header">
                  <span className="source-item-name">{source.name}</span>
                  <span className={`source-badge ${source.method}`}>
                    {source.method.toUpperCase()}
                  </span>
                </div>
                <div className="source-item-url">{source.url}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Real-time Progress */}
      {isScraping && currentSource && (
        <div className="progress-indicator">
          <span className="pulse-dot" />
          Scraping {currentSource}...
        </div>
      )}

      {/* Results */}
      {summary && results.length > 0 && (
        <div className="scraper-results">
          <div className="results-summary-compact">
            <div className="summary-item">
              <span className="summary-value">{summary.total_saved}</span>
              <span className="summary-label">saved</span>
            </div>
            <div className="summary-item">
              <span className="summary-value">{summary.total_duplicates}</span>
              <span className="summary-label">duplicates</span>
            </div>
            <div className="summary-item">
              <span className="summary-value">{totalDuration.toFixed(1)}s</span>
              <span className="summary-label">duration</span>
            </div>
          </div>

          {results.map((result) => (
            <div key={result.source} className="source-result">
              <div className="source-result-header">
                <h3>{result.source}</h3>
                <div className="source-stats">
                  <span className="stat-badge saved">{result.contracts_saved} saved</span>
                  <span className="stat-badge duplicate">{result.duplicates_skipped} duplicates</span>
                  <span className="stat-badge duration">{result.duration_seconds.toFixed(1)}s</span>
                </div>
              </div>

              {result.contract_previews && result.contract_previews.length > 0 && (
                <div className="contracts-preview">
                  <table className="contracts-table">
                    <thead>
                      <tr>
                        <th>Company</th>
                        <th>Value</th>
                        <th>Description</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.contract_previews.map((contract, idx) => (
                        <tr 
                          key={idx} 
                          className={`clickable-row ${contract.is_duplicate ? 'duplicate-row' : ''}`}
                          onClick={() => setSelectedContract(contract)}
                        >
                          <td className="company-cell">{contract.company_name}</td>
                          <td className="value-cell">
                            ${contract.contract_value.toLocaleString()}
                          </td>
                          <td className="description-cell">
                            {contract.description ? (
                              contract.description.length > 80 
                                ? contract.description.substring(0, 80) + '...'
                                : contract.description
                            ) : (
                              <span className="no-description">No description</span>
                            )}
                          </td>
                          <td className="status-cell">
                            {contract.is_duplicate ? (
                              <span className="status-duplicate" title={contract.duplicate_reason}>
                                Duplicate
                              </span>
                            ) : (
                              <span className="status-new">New</span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {result.errors.length > 0 && (
                <div className="source-errors">
                  {result.errors.map((error, idx) => (
                    <div key={idx} className="error-message">
                      {error}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="error-banner">
          {error}
        </div>
      )}

      {/* Contract Details Modal */}
      {selectedContract && (
        <div className="modal-overlay" onClick={() => setSelectedContract(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Contract Details</h3>
              <button 
                className="modal-close" 
                onClick={() => setSelectedContract(null)}
                aria-label="Close"
              >
                ×
              </button>
            </div>
            
            <div className="modal-body">
              <div className="detail-section">
                <div className="detail-row">
                  <span className="detail-label">Company Name</span>
                  <span className="detail-value">{selectedContract.company_name}</span>
                </div>
                
                <div className="detail-row">
                  <span className="detail-label">Contract Value</span>
                  <span className="detail-value detail-value-highlight">
                    ${selectedContract.contract_value.toLocaleString()}
                  </span>
                </div>
                
                {selectedContract.contract_date && (
                  <div className="detail-row">
                    <span className="detail-label">Contract Date</span>
                    <span className="detail-value">
                      {new Date(selectedContract.contract_date).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                      })}
                    </span>
                  </div>
                )}
                
                {selectedContract.category && (
                  <div className="detail-row">
                    <span className="detail-label">Category</span>
                    <span className="detail-value">
                      <span className={`category-badge ${selectedContract.category}`}>
                        {selectedContract.category}
                      </span>
                    </span>
                  </div>
                )}
                
                {selectedContract.description && (
                  <div className="detail-row detail-row-full">
                    <span className="detail-label">Description</span>
                    <div className="detail-value description-formatted">
                      {formatDescriptionText(selectedContract.description)}
                    </div>
                  </div>
                )}
                
                {selectedContract.source && (
                  <div className="detail-row">
                    <span className="detail-label">Source</span>
                    <span className="detail-value detail-value-source">
                      {selectedContract.source}
                    </span>
                  </div>
                )}
                
                {selectedContract.external_id && (
                  <div className="detail-row">
                    <span className="detail-label">External ID</span>
                    <span className="detail-value detail-value-code">
                      {selectedContract.external_id}
                    </span>
                  </div>
                )}
                
                {selectedContract.country && (
                  <div className="detail-row">
                    <span className="detail-label">Country</span>
                    <span className="detail-value">{selectedContract.country}</span>
                  </div>
                )}
                
                <div className="detail-row">
                  <span className="detail-label">Status</span>
                  <span className="detail-value">
                    {selectedContract.is_duplicate ? (
                      <span className="status-duplicate-badge">
                        Duplicate
                      </span>
                    ) : (
                      <span className="status-new-badge">
                        New Contract
                      </span>
                    )}
                  </span>
                </div>
                
                {selectedContract.is_duplicate && selectedContract.duplicate_reason && (
                  <div className="detail-row detail-row-full">
                    <span className="detail-label">Duplicate Reason</span>
                    <span className="detail-value detail-value-muted">
                      {selectedContract.duplicate_reason}
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

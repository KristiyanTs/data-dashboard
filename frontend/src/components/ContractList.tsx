import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchContracts } from '../services/api';
import { Contract, ContractCategory } from '../types/contract';
import { formatDescriptionText } from '../utils/formatDescription';
import './ContractList.css';

const FILTER_DEBOUNCE_MS = 400;

export function ContractList() {
  const [page, setPage] = useState(0);
  const [selectedContract, setSelectedContract] = useState<Contract | null>(null);
  const [filters, setFilters] = useState<{
    category?: string;
    min_value?: number;
    max_value?: number;
  }>({});
  const [debouncedFilters, setDebouncedFilters] = useState<typeof filters>({});

  // Category updates immediately; min/max are debounced
  useEffect(() => {
    setDebouncedFilters(prev => ({ ...prev, category: filters.category }));

    const t = setTimeout(() => {
      setDebouncedFilters(prev => ({
        ...prev,
        min_value: filters.min_value,
        max_value: filters.max_value,
      }));
    }, FILTER_DEBOUNCE_MS);
    return () => clearTimeout(t);
  }, [filters]);

  const { data, isLoading, error } = useQuery({
    queryKey: ['contracts', page, debouncedFilters],
    queryFn: () => fetchContracts(page, 50, debouncedFilters),
  });

  const handleFilterChange = (key: string, value: string | number | undefined) => {
    setFilters(prev => ({
      ...prev,
      [key]: value || undefined,
    }));
    setPage(0); // Reset to first page when filters change
  };

  return (
    <div className="contract-list">
      <h2 className="contract-list-title">Contracts</h2>

      <div className="filters">
        <div className="filter-group">
          <label>Category:</label>
          <select 
            value={filters.category || ''} 
            onChange={(e) => handleFilterChange('category', e.target.value)}
          >
            <option value="">All</option>
            <option value={ContractCategory.GOODS}>Goods</option>
            <option value={ContractCategory.SERVICES}>Services</option>
            <option value={ContractCategory.WORKS}>Works</option>
          </select>
        </div>
        
        <div className="filter-group">
          <label>Min Value:</label>
          <input 
            type="number" 
            placeholder="Min" 
            value={filters.min_value || ''} 
            onChange={(e) => handleFilterChange('min_value', e.target.value ? parseFloat(e.target.value) : undefined)}
          />
        </div>
        
        <div className="filter-group">
          <label>Max Value:</label>
          <input 
            type="number" 
            placeholder="Max" 
            value={filters.max_value || ''} 
            onChange={(e) => handleFilterChange('max_value', e.target.value ? parseFloat(e.target.value) : undefined)}
          />
        </div>
      </div>

      {error ? (
        <div className="error">Error loading contracts</div>
      ) : isLoading || !data ? (
        <div className="loading">
          <span className="loading-spinner" aria-hidden />
          Loading contracts…
        </div>
      ) : (
        <>
          <div className="results-info">
            {data.total} contract{data.total !== 1 ? 's' : ''} · Page {page + 1}
          </div>

          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Company</th>
                  <th>Value</th>
                  <th>Date</th>
                  <th>Category</th>
                  <th>Description</th>
                </tr>
              </thead>
              <tbody>
                {data.contracts.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="no-data">No contracts found</td>
                  </tr>
                ) : (
                  data.contracts.map((contract) => (
                    <tr 
                      key={contract.id} 
                      className="clickable-row"
                      onClick={() => setSelectedContract(contract)}
                    >
                      <td>{contract.id}</td>
                      <td>{contract.company_name}</td>
                      <td>${contract.contract_value.toLocaleString()}</td>
                      <td>{new Date(contract.contract_date).toLocaleDateString()}</td>
                      <td>
                        <span className={`category-badge ${contract.category}`}>
                          {contract.category}
                        </span>
                      </td>
                      <td className="description-cell" title={contract.description || undefined}>
                        {contract.description || '-'}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          <div className="pagination">
            <button
              type="button"
              onClick={() => setPage(p => Math.max(0, p - 1))}
              disabled={page === 0}
            >
              Previous
            </button>
            <span>Page {page + 1}</span>
            <button
              type="button"
              onClick={() => setPage(p => p + 1)}
              disabled={!data.has_more}
            >
              Next
            </button>
          </div>
        </>
      )}

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
                  <span className="detail-label">ID</span>
                  <span className="detail-value">{selectedContract.id}</span>
                </div>
                
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
                
                <div className="detail-row">
                  <span className="detail-label">Category</span>
                  <span className="detail-value">
                    <span className={`category-badge ${selectedContract.category}`}>
                      {selectedContract.category}
                    </span>
                  </span>
                </div>
                
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
                  <span className="detail-label">Created At</span>
                  <span className="detail-value detail-value-muted">
                    {new Date(selectedContract.created_at).toLocaleString('en-US', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

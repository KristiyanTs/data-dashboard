import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchContracts } from '../services/api';
import { ContractCategory } from '../types/contract';
import './ContractList.css';

const FILTER_DEBOUNCE_MS = 400;

export function ContractList() {
  const [page, setPage] = useState(0);
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
                    <tr key={contract.id}>
                      <td>{contract.id}</td>
                      <td>{contract.company_name}</td>
                      <td>${contract.contract_value.toLocaleString()}</td>
                      <td>{new Date(contract.contract_date).toLocaleDateString()}</td>
                      <td>
                        <span className={`category-badge ${contract.category}`}>
                          {contract.category}
                        </span>
                      </td>
                      <td>{contract.description || '-'}</td>
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
    </div>
  );
}

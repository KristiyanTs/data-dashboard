import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { createContract } from '../services/api';
import { ContractCategory, ContractCreate } from '../types/contract';
import './ContractForm.css';

export function ContractForm() {
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState<ContractCreate>({
    company_name: '',
    contract_value: 0,
    contract_date: new Date().toISOString().split('T')[0],
    category: ContractCategory.GOODS,
    description: '',
  });

  const mutation = useMutation({
    mutationFn: createContract,
    onSuccess: () => {
      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey: ['contracts'] });
      queryClient.invalidateQueries({ queryKey: ['statistics'] });
      
      // Reset form
      setFormData({
        company_name: '',
        contract_value: 0,
        contract_date: new Date().toISOString().split('T')[0],
        category: ContractCategory.GOODS,
        description: '',
      });
      
      toast.success('Contract created successfully!');
    },
    onError: (error: any) => {
      toast.error(`Error creating contract: ${error.response?.data?.detail || error.message}`);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Basic validation
    if (!formData.company_name.trim()) {
      toast.error('Company name is required');
      return;
    }
    
    if (formData.contract_value <= 0) {
      toast.error('Contract value must be greater than 0');
      return;
    }
    
    mutation.mutate(formData);
  };

  const handleChange = (field: keyof ContractCreate, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  return (
    <div className="contract-form">
      <h2 className="contract-form-title">New contract</h2>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="company_name">Company Name *</label>
          <input
            id="company_name"
            type="text"
            value={formData.company_name}
            onChange={(e) => handleChange('company_name', e.target.value)}
            placeholder="Enter company name"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="contract_value">Contract Value ($) *</label>
          <input
            id="contract_value"
            type="number"
            step="0.01"
            min="0.01"
            value={formData.contract_value || ''}
            onChange={(e) => handleChange('contract_value', parseFloat(e.target.value))}
            placeholder="0.00"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="contract_date">Contract Date *</label>
          <input
            id="contract_date"
            type="date"
            value={formData.contract_date}
            onChange={(e) => handleChange('contract_date', e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="category">Category *</label>
          <select
            id="category"
            value={formData.category}
            onChange={(e) => handleChange('category', e.target.value as ContractCategory)}
            required
          >
            <option value={ContractCategory.GOODS}>Goods</option>
            <option value={ContractCategory.SERVICES}>Services</option>
            <option value={ContractCategory.WORKS}>Works</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="description">Description (Optional)</label>
          <textarea
            id="description"
            value={formData.description}
            onChange={(e) => handleChange('description', e.target.value)}
            placeholder="Enter contract description"
            rows={4}
          />
        </div>

        <button type="submit" disabled={mutation.isPending}>
          {mutation.isPending && <span className="submit-spinner" aria-hidden />}
          {mutation.isPending ? 'Creating…' : 'Create contract'}
        </button>
      </form>
    </div>
  );
}

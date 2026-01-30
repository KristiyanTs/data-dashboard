import axios from 'axios';
import { Contract, ContractCreate, ContractList, Statistics } from '../types/contract';

// In development, use /api prefix which gets proxied to backend (see setupProxy.js)
// In production, use the backend URL directly
const API_BASE_URL = process.env.NODE_ENV === 'development' ? '/api' : 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const fetchContracts = async (
  page: number = 0,
  pageSize: number = 100,
  filters?: {
    category?: string;
    min_value?: number;
    max_value?: number;
    start_date?: string;
    end_date?: string;
  }
): Promise<ContractList> => {
  const params = new URLSearchParams({
    page: page.toString(),
    page_size: pageSize.toString(),
  });

  if (filters) {
    if (filters.category) params.append('category', filters.category);
    if (filters.min_value) params.append('min_value', filters.min_value.toString());
    if (filters.max_value) params.append('max_value', filters.max_value.toString());
    if (filters.start_date) params.append('start_date', filters.start_date);
    if (filters.end_date) params.append('end_date', filters.end_date);
  }

  const response = await api.get<ContractList>(`/contracts?${params}`);
  return response.data;
};

export const fetchContract = async (id: number): Promise<Contract> => {
  const response = await api.get<Contract>(`/contracts/${id}`);
  return response.data;
};

export const createContract = async (contract: ContractCreate): Promise<Contract> => {
  const response = await api.post<Contract>('/contracts', contract);
  return response.data;
};

export const fetchStatistics = async (): Promise<Statistics> => {
  const response = await api.get<Statistics>('/contracts/statistics');
  return response.data;
};

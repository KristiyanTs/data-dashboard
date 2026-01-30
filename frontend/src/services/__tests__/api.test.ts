/**
 * API service tests - mock axios so no real HTTP requests are made.
 * Factory creates mocks and exposes them via _getMocks() for test setup.
 */
jest.mock('axios', () => {
  const mockGet = jest.fn();
  const mockPost = jest.fn();
  return {
    __esModule: true,
    default: {
      create: () => ({ get: mockGet, post: mockPost }),
      _getMocks: () => ({ get: mockGet, post: mockPost }),
    },
  };
});

import axios from 'axios';
import { fetchContracts, fetchContract, createContract, fetchStatistics } from '../api';

const { get: mockGet, post: mockPost } = (axios as any)._getMocks();
import { ContractCategory } from '../../types/contract';

describe('API Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('fetchContracts', () => {
    it('should fetch contracts successfully', async () => {
      const mockData = {
        contracts: [
          {
            id: 1,
            company_name: 'Test Company',
            contract_value: 100000,
            contract_date: '2024-01-15',
            category: 'goods',
            description: 'Test',
            created_at: '2024-01-15T10:00:00Z',
          },
        ],
        total: 1,
        page: 0,
        page_size: 100,
        has_more: false,
      };

      mockGet.mockResolvedValue({ data: mockData });

      const result = await fetchContracts();

      expect(result).toEqual(mockData);
      expect(result.contracts).toHaveLength(1);
      expect(result.total).toBe(1);
      expect(mockGet).toHaveBeenCalledWith(expect.stringContaining('/contracts'));
    });

    it('should apply filters correctly', async () => {
      const mockData = {
        contracts: [],
        total: 0,
        page: 0,
        page_size: 50,
        has_more: false,
      };

      mockGet.mockResolvedValue({ data: mockData });

      await fetchContracts(0, 50, {
        category: 'goods',
        min_value: 1000,
        max_value: 5000,
      });

      const callUrl = mockGet.mock.calls[0][0];
      expect(callUrl).toContain('category=goods');
      expect(callUrl).toContain('min_value=1000');
      expect(callUrl).toContain('max_value=5000');
    });

    it('should handle pagination parameters', async () => {
      const mockData = {
        contracts: [],
        total: 100,
        page: 2,
        page_size: 25,
        has_more: true,
      };

      mockGet.mockResolvedValue({ data: mockData });

      await fetchContracts(2, 25);

      expect(mockGet).toHaveBeenCalledWith(expect.stringContaining('page=2'));
      expect(mockGet).toHaveBeenCalledWith(expect.stringContaining('page_size=25'));
    });

    it('should handle API errors', async () => {
      mockGet.mockRejectedValue(new Error('Request failed'));

      await expect(fetchContracts()).rejects.toThrow();
    });
  });

  describe('fetchContract', () => {
    it('should fetch a single contract by ID', async () => {
      const mockContract = {
        id: 1,
        company_name: 'Test Company',
        contract_value: 100000,
        contract_date: '2024-01-15',
        category: 'goods',
        description: 'Test',
        created_at: '2024-01-15T10:00:00Z',
      };

      mockGet.mockResolvedValue({ data: mockContract });

      const result = await fetchContract(1);

      expect(result).toEqual(mockContract);
      expect(result.id).toBe(1);
      expect(mockGet).toHaveBeenCalledWith('/contracts/1');
    });

    it('should handle 404 errors', async () => {
      mockGet.mockRejectedValue(new Error('Request failed with status code 404'));

      await expect(fetchContract(999)).rejects.toThrow();
    });
  });

  describe('createContract', () => {
    it('should create a contract successfully', async () => {
      const newContract = {
        company_name: 'New Company',
        contract_value: 50000,
        contract_date: '2024-01-20',
        category: ContractCategory.SERVICES,
        description: 'New contract',
      };

      const mockResponse = {
        ...newContract,
        id: 1,
        created_at: '2024-01-20T10:00:00Z',
      };

      mockPost.mockResolvedValue({ data: mockResponse });

      const result = await createContract(newContract);

      expect(result).toEqual(mockResponse);
      expect(result.id).toBe(1);
      expect(mockPost).toHaveBeenCalledWith('/contracts', newContract);
    });

    it('should handle validation errors', async () => {
      const invalidContract = {
        company_name: '',
        contract_value: -100,
        contract_date: '2024-01-20',
        category: ContractCategory.GOODS,
      };

      mockPost.mockRejectedValue(new Error('Request failed with status code 422'));

      await expect(createContract(invalidContract)).rejects.toThrow();
    });
  });

  describe('fetchStatistics', () => {
    it('should fetch statistics successfully', async () => {
      const mockStats = {
        total_contracts: 10,
        total_value: 1000000,
        average_value: 100000,
        by_category: {
          goods: { count: 5, total_value: 500000 },
          services: { count: 3, total_value: 300000 },
          works: { count: 2, total_value: 200000 },
        },
      };

      mockGet.mockResolvedValue({ data: mockStats });

      const result = await fetchStatistics();

      expect(result).toEqual(mockStats);
      expect(result.total_contracts).toBe(10);
      expect(result.by_category).toHaveProperty('goods');
      expect(mockGet).toHaveBeenCalledWith('/contracts/statistics');
    });

    it('should handle empty statistics', async () => {
      const emptyStats = {
        total_contracts: 0,
        total_value: 0,
        average_value: 0,
        by_category: {},
      };

      mockGet.mockResolvedValue({ data: emptyStats });

      const result = await fetchStatistics();

      expect(result.total_contracts).toBe(0);
      expect(result.by_category).toEqual({});
    });
  });
});

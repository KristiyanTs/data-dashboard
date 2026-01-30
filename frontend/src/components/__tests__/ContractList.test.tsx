import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ContractList } from '../ContractList';
import * as api from '../../services/api';

// Mock the API
jest.mock('../../services/api');

const mockFetchContracts = api.fetchContracts as jest.MockedFunction<typeof api.fetchContracts>;

const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

const renderWithClient = (component: React.ReactElement) => {
  const queryClient = createTestQueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      {component}
    </QueryClientProvider>
  );
};

describe('ContractList', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render loading state initially', () => {
    mockFetchContracts.mockImplementation(() => new Promise(() => {}));

    renderWithClient(<ContractList />);

    expect(screen.getByText(/loading contracts/i)).toBeInTheDocument();
  });

  it('should render contracts when data is loaded', async () => {
    const mockData = {
      contracts: [
        {
          id: 1,
          company_name: 'Test Company A',
          contract_value: 100000,
          contract_date: '2024-01-15',
          category: 'goods' as const,
          description: 'Test description',
          created_at: '2024-01-15T10:00:00Z',
        },
        {
          id: 2,
          company_name: 'Test Company B',
          contract_value: 200000,
          contract_date: '2024-02-20',
          category: 'services' as const,
          description: null,
          created_at: '2024-02-20T10:00:00Z',
        },
      ],
      total: 2,
      page: 0,
      page_size: 50,
      has_more: false,
    };

    mockFetchContracts.mockResolvedValue(mockData);

    renderWithClient(<ContractList />);

    await waitFor(() => {
      expect(screen.getByText('Test Company A')).toBeInTheDocument();
      expect(screen.getByText('Test Company B')).toBeInTheDocument();
    });

    expect(screen.getByText('$100,000')).toBeInTheDocument();
    expect(screen.getByText('$200,000')).toBeInTheDocument();
    expect(screen.getByText('2 contracts · Page 1')).toBeInTheDocument();
  });

  it('should render empty state when no contracts', async () => {
    mockFetchContracts.mockResolvedValue({
      contracts: [],
      total: 0,
      page: 0,
      page_size: 50,
      has_more: false,
    });

    renderWithClient(<ContractList />);

    await waitFor(() => {
      expect(screen.getByText('No contracts found')).toBeInTheDocument();
    });
  });

  it('should render error state on API failure', async () => {
    mockFetchContracts.mockRejectedValue(new Error('API Error'));

    renderWithClient(<ContractList />);

    await waitFor(() => {
      expect(screen.getByText(/error loading contracts/i)).toBeInTheDocument();
    });
  });

  it('should filter by category', async () => {
    mockFetchContracts.mockResolvedValue({
      contracts: [],
      total: 0,
      page: 0,
      page_size: 50,
      has_more: false,
    });

    renderWithClient(<ContractList />);

    await waitFor(() => {
      expect(screen.getByRole('combobox')).toBeInTheDocument();
    });

    const categorySelect = screen.getByRole('combobox');
    fireEvent.change(categorySelect, { target: { value: 'goods' } });

    await waitFor(() => {
      expect(mockFetchContracts).toHaveBeenCalledWith(
        0,
        50,
        expect.objectContaining({ category: 'goods' })
      );
    });
  });

  it('should filter by value range', async () => {
    mockFetchContracts.mockResolvedValue({
      contracts: [],
      total: 0,
      page: 0,
      page_size: 50,
      has_more: false,
    });

    renderWithClient(<ContractList />);

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Min')).toBeInTheDocument();
    });

    const minValueInput = screen.getByPlaceholderText('Min');
    const maxValueInput = screen.getByPlaceholderText('Max');

    fireEvent.change(minValueInput, { target: { value: '1000' } });
    fireEvent.change(maxValueInput, { target: { value: '5000' } });

    // Wait for debounce
    await waitFor(
      () => {
        expect(mockFetchContracts).toHaveBeenCalledWith(
          0,
          50,
          expect.objectContaining({
            min_value: 1000,
            max_value: 5000,
          })
        );
      },
      { timeout: 1000 }
    );
  });

  it('should handle pagination', async () => {
    const mockData = {
      contracts: [
        {
          id: 1,
          company_name: 'Test Company',
          contract_value: 100000,
          contract_date: '2024-01-15',
          category: 'goods' as const,
          description: 'Test',
          created_at: '2024-01-15T10:00:00Z',
        },
      ],
      total: 100,
      page: 0,
      page_size: 50,
      has_more: true,
    };

    mockFetchContracts.mockResolvedValue(mockData);

    renderWithClient(<ContractList />);

    await waitFor(() => {
      expect(screen.getByText('Test Company')).toBeInTheDocument();
    });

    const nextButton = screen.getByRole('button', { name: /next/i });
    expect(nextButton).not.toBeDisabled();

    fireEvent.click(nextButton);

    await waitFor(() => {
      expect(mockFetchContracts).toHaveBeenCalledWith(1, 50, expect.any(Object));
    });
  });

  it('should disable previous button on first page', async () => {
    mockFetchContracts.mockResolvedValue({
      contracts: [],
      total: 0,
      page: 0,
      page_size: 50,
      has_more: false,
    });

    renderWithClient(<ContractList />);

    await waitFor(() => {
      const prevButton = screen.getByRole('button', { name: /previous/i });
      expect(prevButton).toBeDisabled();
    });
  });

  it('should disable next button when no more pages', async () => {
    mockFetchContracts.mockResolvedValue({
      contracts: [],
      total: 10,
      page: 0,
      page_size: 50,
      has_more: false,
    });

    renderWithClient(<ContractList />);

    await waitFor(() => {
      const nextButton = screen.getByRole('button', { name: /next/i });
      expect(nextButton).toBeDisabled();
    });
  });

  it('should reset to page 0 when filters change', async () => {
    mockFetchContracts.mockResolvedValue({
      contracts: [],
      total: 100,
      page: 0,
      page_size: 50,
      has_more: true,
    });

    renderWithClient(<ContractList />);

    // Wait for data to load (100 contracts, has_more: true so Next is enabled)
    await waitFor(() => {
      expect(screen.getByText(/100 contract/)).toBeInTheDocument();
    });

    // Go to page 2
    const nextButton = screen.getByRole('button', { name: 'Next' });
    fireEvent.click(nextButton);

    await waitFor(() => {
      expect(mockFetchContracts).toHaveBeenCalledWith(1, 50, expect.any(Object));
    });

    // Change filter - should reset to page 0
    const categorySelect = screen.getByRole('combobox');
    fireEvent.change(categorySelect, { target: { value: 'goods' } });

    await waitFor(() => {
      expect(mockFetchContracts).toHaveBeenCalledWith(
        0,
        50,
        expect.objectContaining({ category: 'goods' })
      );
    });
  });

  it('should display category badges correctly', async () => {
    mockFetchContracts.mockResolvedValue({
      contracts: [
        {
          id: 1,
          company_name: 'Test',
          contract_value: 100000,
          contract_date: '2024-01-15',
          category: 'goods' as const,
          description: null,
          created_at: '2024-01-15T10:00:00Z',
        },
      ],
      total: 1,
      page: 0,
      page_size: 50,
      has_more: false,
    });

    renderWithClient(<ContractList />);

    await waitFor(() => {
      const badge = screen.getByText('goods');
      expect(badge).toHaveClass('category-badge');
      expect(badge).toHaveClass('goods');
    });
  });
});

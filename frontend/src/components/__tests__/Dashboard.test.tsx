import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Dashboard } from '../Dashboard';
import * as api from '../../services/api';

// Mock the API
jest.mock('../../services/api');

const mockFetchStatistics = api.fetchStatistics as jest.MockedFunction<typeof api.fetchStatistics>;

// Mock Recharts to avoid canvas issues in tests
jest.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: any) => <div>{children}</div>,
  BarChart: ({ children }: any) => <div data-testid="bar-chart">{children}</div>,
  Bar: () => <div data-testid="bar" />,
  XAxis: () => <div data-testid="x-axis" />,
  YAxis: () => <div data-testid="y-axis" />,
  CartesianGrid: () => <div data-testid="grid" />,
  Tooltip: () => <div data-testid="tooltip" />,
  Legend: () => <div data-testid="legend" />,
}));

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

describe('Dashboard', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render loading state initially', () => {
    mockFetchStatistics.mockImplementation(() => new Promise(() => {}));

    renderWithClient(<Dashboard />);

    expect(screen.getByText(/loading statistics/i)).toBeInTheDocument();
  });

  it('should render statistics when data is loaded', async () => {
    const mockStats = {
      total_contracts: 100,
      total_value: 5000000,
      average_value: 50000,
      by_category: {
        goods: { count: 40, total_value: 2000000 },
        services: { count: 35, total_value: 1750000 },
        works: { count: 25, total_value: 1250000 },
      },
    };

    mockFetchStatistics.mockResolvedValue(mockStats);

    renderWithClient(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('100')).toBeInTheDocument();
    });

    expect(screen.getByText('$5,000,000.00')).toBeInTheDocument();
    expect(screen.getByText('$50,000.00')).toBeInTheDocument();
  });

  it('should render error state on API failure', async () => {
    mockFetchStatistics.mockRejectedValue(new Error('API Error'));

    renderWithClient(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText(/error loading statistics/i)).toBeInTheDocument();
    });
  });

  it('should display all stat cards', async () => {
    const mockStats = {
      total_contracts: 50,
      total_value: 2500000,
      average_value: 50000,
      by_category: {},
    };

    mockFetchStatistics.mockResolvedValue(mockStats);

    renderWithClient(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText(/total contracts/i)).toBeInTheDocument();
      expect(screen.getByText(/total value/i)).toBeInTheDocument();
      expect(screen.getByText(/average value/i)).toBeInTheDocument();
    });
  });

  it('should render chart when category data exists', async () => {
    const mockStats = {
      total_contracts: 100,
      total_value: 5000000,
      average_value: 50000,
      by_category: {
        goods: { count: 40, total_value: 2000000 },
        services: { count: 35, total_value: 1750000 },
        works: { count: 25, total_value: 1250000 },
      },
    };

    mockFetchStatistics.mockResolvedValue(mockStats);

    renderWithClient(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByTestId('bar-chart')).toBeInTheDocument();
    });

    expect(screen.getByText(/contracts by category/i)).toBeInTheDocument();
  });

  it('should not render chart when no category data', async () => {
    const mockStats = {
      total_contracts: 0,
      total_value: 0,
      average_value: 0,
      by_category: {},
    };

    mockFetchStatistics.mockResolvedValue(mockStats);

    renderWithClient(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('0')).toBeInTheDocument();
    });

    expect(screen.queryByTestId('bar-chart')).not.toBeInTheDocument();
    expect(screen.queryByText(/contracts by category/i)).not.toBeInTheDocument();
  });

  it('should format large numbers with commas', async () => {
    const mockStats = {
      total_contracts: 1234,
      total_value: 123456789.99,
      average_value: 99999.99,
      by_category: {},
    };

    mockFetchStatistics.mockResolvedValue(mockStats);

    renderWithClient(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('1,234')).toBeInTheDocument();
      expect(screen.getByText('$123,456,789.99')).toBeInTheDocument();
      expect(screen.getByText('$99,999.99')).toBeInTheDocument();
    });
  });

  it('should handle zero values', async () => {
    const mockStats = {
      total_contracts: 0,
      total_value: 0,
      average_value: 0,
      by_category: {},
    };

    mockFetchStatistics.mockResolvedValue(mockStats);

    renderWithClient(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('0')).toBeInTheDocument();
    });

    expect(screen.getAllByText('$0.00').length).toBeGreaterThanOrEqual(1);
  });

  it('should display decimal values correctly', async () => {
    const mockStats = {
      total_contracts: 10,
      total_value: 12345.67,
      average_value: 1234.56,
      by_category: {},
    };

    mockFetchStatistics.mockResolvedValue(mockStats);

    renderWithClient(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('$12,345.67')).toBeInTheDocument();
      expect(screen.getByText('$1,234.56')).toBeInTheDocument();
    });
  });

  it('should handle all three categories', async () => {
    const mockStats = {
      total_contracts: 100,
      total_value: 5000000,
      average_value: 50000,
      by_category: {
        goods: { count: 40, total_value: 2000000 },
        services: { count: 35, total_value: 1750000 },
        works: { count: 25, total_value: 1250000 },
      },
    };

    mockFetchStatistics.mockResolvedValue(mockStats);

    renderWithClient(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByTestId('bar-chart')).toBeInTheDocument();
    });

    // Chart should be rendered with data for all categories
    expect(mockFetchStatistics).toHaveBeenCalledTimes(1);
  });

  it('should handle partial category data', async () => {
    const mockStats = {
      total_contracts: 50,
      total_value: 2500000,
      average_value: 50000,
      by_category: {
        goods: { count: 50, total_value: 2500000 },
      },
    };

    mockFetchStatistics.mockResolvedValue(mockStats);

    renderWithClient(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByTestId('bar-chart')).toBeInTheDocument();
    });
  });

  it('should call API on mount', async () => {
    const mockStats = {
      total_contracts: 10,
      total_value: 500000,
      average_value: 50000,
      by_category: {},
    };

    mockFetchStatistics.mockResolvedValue(mockStats);

    renderWithClient(<Dashboard />);

    await waitFor(() => {
      expect(mockFetchStatistics).toHaveBeenCalledTimes(1);
    });
  });

  it('should have proper structure with title and cards', async () => {
    const mockStats = {
      total_contracts: 10,
      total_value: 500000,
      average_value: 50000,
      by_category: {},
    };

    mockFetchStatistics.mockResolvedValue(mockStats);

    renderWithClient(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('Dashboard')).toBeInTheDocument();
    });

    // Check that stat cards are rendered
    const statCards = screen.getAllByRole('heading', { level: 3 });
    expect(statCards).toHaveLength(3);
  });
});

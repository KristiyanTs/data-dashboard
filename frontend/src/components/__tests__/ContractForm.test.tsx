import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { ContractForm } from '../ContractForm';
import * as api from '../../services/api';
import { ContractCategory } from '../../types/contract';

// Mock the API and toast
jest.mock('../../services/api');
jest.mock('react-hot-toast');

const mockCreateContract = api.createContract as jest.MockedFunction<typeof api.createContract>;
const mockToast = toast as jest.Mocked<typeof toast>;

const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
      mutations: {
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

describe('ContractForm', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render form with all fields', () => {
    renderWithClient(<ContractForm />);

    expect(screen.getByLabelText(/company name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/contract value/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/contract date/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/category/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /create contract/i })).toBeInTheDocument();
  });

  it('should have default values', () => {
    renderWithClient(<ContractForm />);

    const companyInput = screen.getByLabelText(/company name/i) as HTMLInputElement;
    const valueInput = screen.getByLabelText(/contract value/i) as HTMLInputElement;
    const categorySelect = screen.getByLabelText(/category/i) as HTMLSelectElement;

    expect(companyInput.value).toBe('');
    expect(valueInput.value).toBe(''); // 0 renders as empty for number input
    expect(categorySelect.value).toBe(ContractCategory.GOODS);
  });

  it('should update form fields on input', () => {
    renderWithClient(<ContractForm />);

    const companyInput = screen.getByLabelText(/company name/i);
    const valueInput = screen.getByLabelText(/contract value/i);

    fireEvent.change(companyInput, { target: { value: 'Test Company' } });
    fireEvent.change(valueInput, { target: { value: '50000' } });

    expect(companyInput).toHaveValue('Test Company');
    expect(valueInput).toHaveValue(50000);
  });

  it('should submit form with valid data', async () => {
    const mockResponse = {
      id: 1,
      company_name: 'Test Company',
      contract_value: 50000,
      contract_date: '2024-01-15',
      category: ContractCategory.GOODS,
      description: 'Test description',
      created_at: '2024-01-15T10:00:00Z',
    };

    mockCreateContract.mockResolvedValue(mockResponse);
    mockToast.success = jest.fn();

    renderWithClient(<ContractForm />);

    const companyInput = screen.getByLabelText(/company name/i);
    const valueInput = screen.getByLabelText(/contract value/i);
    const dateInput = screen.getByLabelText(/contract date/i);
    const descriptionInput = screen.getByLabelText(/description/i);
    const submitButton = screen.getByRole('button', { name: /create contract/i });

    fireEvent.change(companyInput, { target: { value: 'Test Company' } });
    fireEvent.change(valueInput, { target: { value: '50000' } });
    fireEvent.change(dateInput, { target: { value: '2024-01-15' } });
    fireEvent.change(descriptionInput, { target: { value: 'Test description' } });

    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockCreateContract).toHaveBeenCalled();
      const payload = mockCreateContract.mock.calls[0][0];
      expect(payload.company_name).toBe('Test Company');
      expect(payload.contract_value).toBe(50000);
      expect(payload.description).toBe('Test description');
    });

    await waitFor(() => {
      expect(mockToast.success).toHaveBeenCalledWith('Contract created successfully!');
    });
  });

  it('should show error for empty company name', async () => {
    mockToast.error = jest.fn();

    renderWithClient(<ContractForm />);

    const valueInput = screen.getByLabelText(/contract value/i);
    const submitButton = screen.getByRole('button', { name: /create contract/i });

    fireEvent.change(valueInput, { target: { value: '50000' } });

    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockToast.error).toHaveBeenCalledWith('Company name is required');
    });

    expect(mockCreateContract).not.toHaveBeenCalled();
  });

  it('should show error for zero or negative contract value', async () => {
    mockToast.error = jest.fn();

    renderWithClient(<ContractForm />);

    const companyInput = screen.getByLabelText(/company name/i);
    const valueInput = screen.getByLabelText(/contract value/i);
    const submitButton = screen.getByRole('button', { name: /create contract/i });

    fireEvent.change(companyInput, { target: { value: 'Test Company' } });
    fireEvent.change(valueInput, { target: { value: '0' } });

    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockToast.error).toHaveBeenCalledWith('Contract value must be greater than 0');
    });

    expect(mockCreateContract).not.toHaveBeenCalled();
  });

  it('should handle API errors', async () => {
    mockCreateContract.mockRejectedValue({
      response: {
        data: {
          detail: 'Validation error',
        },
      },
    });
    mockToast.error = jest.fn();

    renderWithClient(<ContractForm />);

    const companyInput = screen.getByLabelText(/company name/i);
    const valueInput = screen.getByLabelText(/contract value/i);
    const submitButton = screen.getByRole('button', { name: /create contract/i });

    fireEvent.change(companyInput, { target: { value: 'Test Company' } });
    fireEvent.change(valueInput, { target: { value: '50000' } });

    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockToast.error).toHaveBeenCalledWith('Error creating contract: Validation error');
    });
  });

  it('should reset form after successful submission', async () => {
    const mockResponse = {
      id: 1,
      company_name: 'Test Company',
      contract_value: 50000,
      contract_date: '2024-01-15',
      category: ContractCategory.GOODS,
      description: 'Test',
      created_at: '2024-01-15T10:00:00Z',
    };

    mockCreateContract.mockResolvedValue(mockResponse);
    mockToast.success = jest.fn();

    renderWithClient(<ContractForm />);

    const companyInput = screen.getByLabelText(/company name/i) as HTMLInputElement;
    const valueInput = screen.getByLabelText(/contract value/i) as HTMLInputElement;
    const submitButton = screen.getByRole('button', { name: /create contract/i });

    fireEvent.change(companyInput, { target: { value: 'Test Company' } });
    fireEvent.change(valueInput, { target: { value: '50000' } });

    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockToast.success).toHaveBeenCalled();
    });

    // Form should be reset
    await waitFor(() => {
      expect(companyInput.value).toBe('');
      expect(valueInput.value).toBe('');
    });
  });

  it('should disable submit button while submitting', async () => {
    mockCreateContract.mockImplementation(() => new Promise(() => {})); // Never resolves

    renderWithClient(<ContractForm />);

    const companyInput = screen.getByLabelText(/company name/i);
    const valueInput = screen.getByLabelText(/contract value/i);
    const submitButton = screen.getByRole('button', { name: /create contract/i });

    fireEvent.change(companyInput, { target: { value: 'Test Company' } });
    fireEvent.change(valueInput, { target: { value: '50000' } });

    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(submitButton).toBeDisabled();
      expect(screen.getByText(/creating/i)).toBeInTheDocument();
    });
  });

  it('should allow selecting different categories', () => {
    renderWithClient(<ContractForm />);

    const categorySelect = screen.getByLabelText(/category/i) as HTMLSelectElement;

    expect(categorySelect.value).toBe(ContractCategory.GOODS);

    fireEvent.change(categorySelect, { target: { value: ContractCategory.SERVICES } });
    expect(categorySelect.value).toBe(ContractCategory.SERVICES);

    fireEvent.change(categorySelect, { target: { value: ContractCategory.WORKS } });
    expect(categorySelect.value).toBe(ContractCategory.WORKS);
  });

  it('should handle optional description field', async () => {
    const mockResponse = {
      id: 1,
      company_name: 'Test Company',
      contract_value: 50000,
      contract_date: '2024-01-15',
      category: ContractCategory.GOODS,
      description: '',
      created_at: '2024-01-15T10:00:00Z',
    };

    mockCreateContract.mockResolvedValue(mockResponse);
    mockToast.success = jest.fn();

    renderWithClient(<ContractForm />);

    const companyInput = screen.getByLabelText(/company name/i);
    const valueInput = screen.getByLabelText(/contract value/i);
    const submitButton = screen.getByRole('button', { name: /create contract/i });

    fireEvent.change(companyInput, { target: { value: 'Test Company' } });
    fireEvent.change(valueInput, { target: { value: '50000' } });

    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockCreateContract).toHaveBeenCalled();
      const callArg = mockCreateContract.mock.calls[0][0];
      expect(callArg.company_name).toBe('Test Company');
      expect(callArg.contract_value).toBe(50000);
      expect(callArg.description === '' || callArg.description === undefined).toBe(true);
    });
  });
});

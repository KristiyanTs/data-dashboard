# Frontend Testing Guide

This document explains how to run and understand the frontend tests for the Procurement Data Dashboard React application.

## Test Structure

The frontend tests are organized by component and service:

- **Component Tests**:
  - `src/components/__tests__/ContractList.test.tsx` - Contract listing and filtering
  - `src/components/__tests__/ContractForm.test.tsx` - Contract creation form
  - `src/components/__tests__/Dashboard.test.tsx` - Statistics dashboard
- **Service Tests**:
  - `src/services/__tests__/api.test.ts` - API client functions

## Prerequisites

Install dependencies (if not already installed):

```bash
cd frontend
npm install
```

## Running Tests

### Run all tests
```bash
npm test
```

### Run tests in watch mode (default)
```bash
npm test
```

Press `a` to run all tests, or follow the interactive prompts.

### Run tests once (CI mode)
```bash
npm test -- --watchAll=false
```

### Run with coverage
```bash
npm test -- --coverage --watchAll=false
```

### Run specific test file
```bash
npm test ContractList
npm test ContractForm
npm test Dashboard
npm test api
```

### Run tests matching a pattern
```bash
npm test -- --testNamePattern="should render"
```

## Test Coverage

The tests cover:

### ContractList Component (`ContractList.test.tsx`)
- ✅ Loading state
- ✅ Rendering contracts
- ✅ Empty state
- ✅ Error handling
- ✅ Category filtering
- ✅ Value range filtering (with debounce)
- ✅ Pagination (next/previous)
- ✅ Filter reset on change
- ✅ Category badges
- ✅ Button states (disabled/enabled)

### ContractForm Component (`ContractForm.test.tsx`)
- ✅ Form rendering with all fields
- ✅ Default values
- ✅ Input updates
- ✅ Form submission with valid data
- ✅ Validation (empty name, zero value)
- ✅ API error handling
- ✅ Form reset after success
- ✅ Submit button disabled state
- ✅ Category selection
- ✅ Optional description field

### Dashboard Component (`Dashboard.test.tsx`)
- ✅ Loading state
- ✅ Statistics rendering
- ✅ Error handling
- ✅ Stat cards display
- ✅ Chart rendering with data
- ✅ No chart when no data
- ✅ Number formatting (commas, decimals)
- ✅ Zero values
- ✅ All category types
- ✅ Partial category data

### API Service (`api.test.ts`)
- ✅ Fetching contracts with filters
- ✅ Fetching single contract
- ✅ Creating contracts
- ✅ Fetching statistics
- ✅ Error handling (400, 404, 422, 500)
- ✅ Query parameter construction
- ✅ Pagination parameters

## Testing Libraries

The tests use:

- **React Testing Library**: Component testing with user-centric queries
- **Jest**: Test runner and assertion library
- **@testing-library/user-event**: Simulating user interactions
- **axios-mock-adapter**: Mocking HTTP requests
- **@tanstack/react-query**: Query client for data fetching

## Test Patterns

### Component Testing Pattern

```tsx
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const renderWithClient = (component: React.ReactElement) => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } }
  });
  return render(
    <QueryClientProvider client={queryClient}>
      {component}
    </QueryClientProvider>
  );
};

test('example test', async () => {
  renderWithClient(<MyComponent />);
  
  await waitFor(() => {
    expect(screen.getByText('Expected Text')).toBeInTheDocument();
  });
});
```

### API Testing Pattern

```typescript
import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';

describe('API Service', () => {
  let mock: MockAdapter;

  beforeEach(() => {
    mock = new MockAdapter(axios);
  });

  afterEach(() => {
    mock.restore();
  });

  it('should fetch data', async () => {
    mock.onGet('/endpoint').reply(200, { data: 'value' });
    const result = await apiFunction();
    expect(result).toEqual({ data: 'value' });
  });
});
```

## Debugging Tests

### Run tests with verbose output
```bash
npm test -- --verbose
```

### Debug a specific test
Add `debugger` statement in your test and run:
```bash
node --inspect-brk node_modules/.bin/jest --runInBand
```

Then open `chrome://inspect` in Chrome.

### View test output
Tests automatically show console output for failing tests. To see all output:
```bash
npm test -- --verbose --no-coverage
```

## Common Issues

### Tests timing out
Increase timeout for specific tests:
```typescript
it('slow test', async () => {
  // test code
}, 10000); // 10 second timeout
```

### Mock not working
Make sure mocks are cleared between tests:
```typescript
beforeEach(() => {
  jest.clearAllMocks();
});
```

### Query client issues
Always create a fresh QueryClient for each test to avoid state pollution:
```typescript
const createTestQueryClient = () => new QueryClient({
  defaultOptions: { queries: { retry: false } }
});
```

## Continuous Integration

To run tests in CI/CD:

```bash
# Install dependencies
npm ci

# Run tests once with coverage
npm test -- --coverage --watchAll=false

# Check coverage thresholds (optional)
npm test -- --coverage --watchAll=false --coverageThreshold='{"global":{"branches":80,"functions":80,"lines":80,"statements":80}}'
```

## Writing New Tests

When adding new components or features:

1. Create a test file next to your component: `ComponentName.test.tsx`
2. Mock external dependencies (API calls, etc.)
3. Test user interactions, not implementation details
4. Use accessible queries (getByRole, getByLabelText) over getByTestId
5. Test error states and edge cases

Example structure:

```tsx
describe('MyComponent', () => {
  beforeEach(() => {
    // Setup
  });

  it('should render correctly', () => {
    // Test rendering
  });

  it('should handle user interaction', async () => {
    // Test interactions
  });

  it('should handle errors', async () => {
    // Test error cases
  });
});
```

## Coverage Goals

Aim for:
- **Statements**: >80%
- **Branches**: >75%
- **Functions**: >80%
- **Lines**: >80%

View coverage report:
```bash
npm test -- --coverage --watchAll=false
open coverage/lcov-report/index.html
```

# React Component Testing Guide

This document provides comprehensive information about testing the React frontend components of the research study platform.

## Test Setup

### Dependencies
- **@testing-library/react**: React component testing utilities
- **@testing-library/jest-dom**: Custom Jest matchers for DOM elements
- **@testing-library/user-event**: User interaction simulation
- **msw**: Mock Service Worker for API mocking
- **jest-environment-jsdom**: JSDOM environment for Jest

### Configuration Files
- `src/setupTests.ts`: Global test configuration and setup
- `src/test-utils.tsx`: Custom render function and test utilities
- `src/mocks/server.ts`: Mock server for API responses

## Test Structure

### Component Tests
Tests are organized by component type:

```
src/components/
├── admin/
│   └── __tests__/
│       └── AdminDashboard.test.tsx
├── auth/
│   └── __tests__/
│       └── LoginForm.test.tsx
├── quiz/
│   └── __tests__/
│       └── QuizInterface.test.tsx
├── study/
│   └── __tests__/
│       └── StudySession.test.tsx
└── __tests__/
    └── integration.test.tsx
```

### Test Coverage Areas

#### 1. AdminDashboard Component
- **Authentication**: Tests admin/staff access control
- **Navigation**: Tab switching and content display
- **UI States**: Loading states and error handling
- **User Permissions**: Role-based access control

#### 2. LoginForm Component
- **Form Validation**: Username and password validation
- **Authentication Flow**: Login success/failure handling
- **User Interaction**: Form submission and error display
- **Accessibility**: ARIA attributes and keyboard navigation

#### 3. QuizInterface Component
- **Quiz Flow**: Multi-question navigation and completion
- **Answer Tracking**: Response recording and validation
- **Progress Tracking**: Time elapsed and completion percentage
- **Submission**: Quiz completion and result display

#### 4. StudySession Component
- **Session Flow**: Multi-phase study progression
- **Group Handling**: PDF vs ChatGPT study paths
- **Progress Tracking**: Phase completion and overall progress
- **State Management**: Session persistence and error recovery

#### 5. Integration Tests
- **App-level Flow**: Authentication and routing integration
- **State Management**: User state across components
- **Error Boundaries**: Error handling and recovery
- **Route Protection**: Access control and redirects

## Running Tests

### Basic Test Commands
```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run tests for CI/CD
npm run test:ci
```

### Test Patterns

#### Component Rendering
```typescript
it('renders component correctly', () => {
  render(<Component />);
  expect(screen.getByText('Expected Text')).toBeInTheDocument();
});
```

#### User Interactions
```typescript
it('handles user interaction', async () => {
  const user = userEvent.setup();
  render(<Component />);
  
  await user.click(screen.getByRole('button'));
  expect(screen.getByText('Result')).toBeInTheDocument();
});
```

#### Async Operations
```typescript
it('handles async operations', async () => {
  render(<Component />);
  
  await waitFor(() => {
    expect(screen.getByText('Loaded Data')).toBeInTheDocument();
  });
});
```

#### API Mocking
```typescript
it('handles API calls', async () => {
  // Mock API response in server.ts
  render(<Component />);
  
  await waitFor(() => {
    expect(screen.getByText('API Data')).toBeInTheDocument();
  });
});
```

## Test Utilities

### Custom Render Function
```typescript
import { render, mockUser } from '../test-utils';

// Render with authenticated user
render(<Component />, { initialUser: mockUser });

// Render with admin user
render(<Component />, { initialUser: mockAdmin });
```

### Mock Data
Pre-defined mock objects for testing:
- `mockUser`: Regular user object
- `mockAdmin`: Admin user object
- `mockStudy`: Study object
- `mockParticipant`: Participant object
- `mockQuiz`: Quiz object

### Helper Functions
- `createMockEvent()`: Create mock DOM events
- `waitForAsync()`: Wait for async operations
- `mockApiResponse()`: Mock API responses
- `mockApiError()`: Mock API errors

## Mock Server

The test setup includes a comprehensive mock server that simulates backend API responses:

### Endpoints Covered
- Authentication (`/api/auth/`)
- Studies (`/api/research/studies/`)
- Participants (`/api/research/participants/`)
- Logging (`/api/research/log/`)
- Quizzes (`/api/quiz/`)
- Exports (`/api/research/export/`)
- Privacy (`/api/research/privacy/`)
- Utilities (`/api/research/utils/`)
- Dashboard (`/api/dashboard/`)

### Adding New Mocks
To add new API endpoints:

1. Add handler to `src/mocks/server.ts`:
```typescript
http.get('*/api/new-endpoint/', () => {
  return HttpResponse.json({ data: 'mock response' });
})
```

2. Add mock data as needed
3. Update tests to use the new endpoint

## Test Best Practices

### Component Testing
1. **Test user behavior**, not implementation details
2. **Use accessible queries** (getByRole, getByLabelText)
3. **Test happy path and error cases**
4. **Mock external dependencies** (APIs, timers)
5. **Keep tests focused** on single responsibilities

### Async Testing
1. **Use waitFor** for async operations
2. **Mock timers** when testing time-dependent code
3. **Handle loading states** in tests
4. **Test error boundaries** and fallbacks

### Mock Management
1. **Clear mocks** between tests
2. **Use specific mocks** for each test scenario
3. **Test both success and failure cases**
4. **Mock at appropriate levels** (component vs service)

## Coverage Requirements

### Target Coverage
- **Statements**: 80%+
- **Branches**: 75%+
- **Functions**: 80%+
- **Lines**: 80%+

### Coverage Reports
```bash
# Generate coverage report
npm run test:coverage

# View coverage report
open coverage/lcov-report/index.html
```

### Excluded from Coverage
- Type definitions (*.d.ts)
- Test files (*test.tsx, *spec.tsx)
- Setup files (setupTests.ts, index.tsx)
- Mock files (mocks/*)

## Debugging Tests

### Common Issues
1. **Async operations not awaited**
   - Use `waitFor` or `findBy` queries
   - Check for proper async/await usage

2. **Elements not found**
   - Use `screen.debug()` to see rendered output
   - Check element accessibility and timing

3. **Mock not working**
   - Verify mock is properly configured
   - Check import order and hoisting

4. **Test isolation problems**
   - Clear mocks in beforeEach
   - Reset state between tests

### Debugging Tools
```typescript
// Debug rendered output
screen.debug();

// Debug specific element
screen.debug(screen.getByText('Button'));

// Check what queries are available
screen.logTestingPlaygroundURL();
```

## Continuous Integration

### CI Configuration
Tests are configured to run in CI with:
- Coverage reporting
- Parallel test execution
- Artifact collection
- Failure notifications

### Pre-commit Hooks
Consider adding pre-commit hooks for:
- Running tests
- Checking coverage thresholds
- Linting and formatting
- Type checking

## Performance Testing

### Test Performance
- Keep tests fast (< 5 seconds each)
- Use shallow rendering when appropriate
- Mock heavy operations
- Avoid unnecessary DOM queries

### Bundle Size Testing
Consider adding tests for:
- Component bundle size
- Lazy loading effectiveness
- Code splitting boundaries

## Accessibility Testing

### A11y Testing
Include accessibility tests for:
- Keyboard navigation
- Screen reader compatibility
- ARIA attributes
- Color contrast
- Focus management

### Tools
- @testing-library/jest-dom matchers
- axe-core for automated a11y testing
- Manual testing with screen readers

## Resources

### Documentation
- [Testing Library Docs](https://testing-library.com/docs/react-testing-library/intro)
- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [MSW Documentation](https://mswjs.io/docs/)

### Best Practices
- [Testing Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)
- [Testing Patterns](https://testing-library.com/docs/react-testing-library/cheatsheet)

This comprehensive testing setup ensures reliable, maintainable tests that provide confidence in the frontend functionality of the research study platform.
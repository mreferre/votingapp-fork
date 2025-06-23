# Unit Testing Setup for Voting App

## Overview
Successfully created a comprehensive unit testing suite for the Flask voting application with **98% code coverage** and **15 passing tests**.

## Files Created

### Test Files
- **`test_app.py`** - Main test file containing all unit tests
- **`test_requirements.txt`** - Testing dependencies
- **`run_tests.sh`** - Test runner script

### Docker Files
- **`Dockerfile.test`** - Docker container setup for testing environment

### Configuration Files
- Updated **`requirements.txt`** with compatible dependency versions

## Test Coverage

### Functions Tested
1. **Utility Functions**
   - `f(x)` - CPU stress function
   - `readvote(restaurant)` - DynamoDB read operations
   - `updatevote(restaurant, votes)` - DynamoDB write operations

2. **Flask Route Handlers**
   - `home()` - Welcome page
   - `outback()` - Outback restaurant voting
   - `bucadibeppo()` - Bucadibeppo restaurant voting  
   - `ihop()` - IHOP restaurant voting
   - `chipotle()` - Chipotle restaurant voting
   - `getvotes()` - Retrieve all votes
   - `getheavyvotes()` - Retrieve votes with CPU/memory stress

3. **Environment Variable Handling**
   - Default values testing
   - Custom environment values testing

4. **Error Handling**
   - DynamoDB connection failures
   - Update operation failures

## Test Categories

### 1. TestUtilityFunctions (4 tests)
- Tests core business logic functions
- Mocks DynamoDB operations using `moto` library
- Covers success and error scenarios

### 2. TestFlaskRoutes (7 tests)
- Tests all HTTP endpoints
- Uses Flask test client
- Mocks DynamoDB with realistic data
- Verifies response codes and content

### 3. TestEnvironmentVariables (2 tests)
- Tests environment variable loading
- Verifies default and custom configurations

### 4. TestErrorHandling (2 tests)
- Tests error scenarios
- Ensures proper exception handling

## Key Testing Features

### Mocking Strategy
- **DynamoDB**: Mocked using `moto[dynamodb]` for realistic testing
- **Multiprocessing**: Mocked to avoid heavy CPU operations in tests
- **Environment Variables**: Mocked for configuration testing

### Test Infrastructure
- **pytest**: Primary testing framework
- **pytest-flask**: Flask-specific testing utilities
- **pytest-mock**: Enhanced mocking capabilities
- **moto**: AWS service mocking
- **coverage**: Code coverage reporting

### Coverage Report
- **98% code coverage** achieved
- Only 2 lines uncovered (main execution block)
- Detailed HTML coverage report generated in `htmlcov/`

## Running the Tests

### Prerequisites
```bash
# Create virtual environment
python3 -m venv test_env
source test_env/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r test_requirements.txt
```

### Running Tests
```bash
# Set environment variables
export DDB_AWS_REGION=us-east-1
export DDB_TABLE_NAME=test-votingapp-restaurants
export CPUSTRESSFACTOR=1
export MEMSTRESSFACTOR=1

# Run tests with coverage
python -m pytest test_app.py -v --cov=app --cov-report=html --cov-report=term-missing

# Or use the test script
bash run_tests.sh
```

### Generated Reports
- **`htmlcov/`** - Interactive HTML coverage report
- **`coverage.xml`** - XML coverage report for CI/CD
- **`test-results.xml`** - JUnit-style test results

## Docker Support

### Test-Specific Dockerfile
- **`Dockerfile.test`** includes all test dependencies
- Supports both application and test execution
- Configured with proper environment variables

### Usage
```bash
# Build test image
docker build -f Dockerfile.test -t votingapp-test .

# Run tests in container
docker run --rm votingapp-test bash run_tests.sh
```

## Test Results Summary

✅ **15 tests passed**  
✅ **98% code coverage**  
✅ **All functions tested**  
✅ **Error scenarios covered**  
✅ **Flask routes validated**  
✅ **DynamoDB operations mocked**  
✅ **Environment configuration tested**  

## Benefits

1. **Reliability**: Comprehensive testing ensures code quality
2. **Maintainability**: Tests catch regressions during refactoring
3. **Documentation**: Tests serve as usage examples
4. **CI/CD Ready**: Compatible with automated testing pipelines
5. **Containerized**: Tests run consistently across environments

## Dependencies Used

### Production Dependencies
- Flask==2.0.3
- Flask-Cors==3.0.10
- Werkzeug==2.2.2
- boto3==1.26.76
- botocore==1.29.76
- simplejson==3.17.2

### Test Dependencies
- pytest==7.4.3
- pytest-flask==1.3.0
- pytest-mock==3.12.0
- pytest-cov==6.2.1
- moto[dynamodb]==4.2.14
- coverage==7.9.1

The testing setup is production-ready and provides excellent coverage of all application functionality!
import pytest
import json
import os
from unittest.mock import patch, MagicMock, Mock
from moto import mock_dynamodb
import boto3
from multiprocessing import cpu_count

# Import the Flask app and functions to test
from app import app, f, readvote, updatevote, cpustressfactor, memstressfactor


class TestUtilityFunctions:
    """Test utility functions that don't depend on Flask routes"""
    
    def test_f_function_execution(self):
        """Test that the CPU stress function f(x) executes without errors"""
        # This function should complete without raising exceptions
        # We'll test with a small value to avoid long test execution
        with patch.dict(os.environ, {'CPUSTRESSFACTOR': '1'}):
            try:
                f(1)  # Should not raise any exception
                assert True
            except Exception as e:
                pytest.fail(f"Function f(x) raised an exception: {e}")
    
    @mock_dynamodb
    def test_readvote_success(self):
        """Test reading vote count from DynamoDB successfully"""
        # Setup mock DynamoDB table
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table_name = 'test-votingapp-restaurants'
        
        # Create table
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'name',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'name',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Put test data
        table.put_item(
            Item={
                'name': 'outback',
                'restaurantcount': 5
            }
        )
        
        # Patch the global DynamoDB table in app.py
        with patch('app.ddbtable', table):
            votes = readvote('outback')
            assert votes == '5'
    
    @mock_dynamodb 
    def test_readvote_restaurant_not_found(self):
        """Test reading vote count when restaurant doesn't exist"""
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table_name = 'test-votingapp-restaurants'
        
        # Create empty table
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'name',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'name',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        with patch('app.ddbtable', table):
            with pytest.raises(KeyError):
                readvote('nonexistent')
    
    @mock_dynamodb
    def test_updatevote_success(self):
        """Test updating vote count in DynamoDB successfully"""
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table_name = 'test-votingapp-restaurants'
        
        # Create table
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'name',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'name',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Put initial data
        table.put_item(
            Item={
                'name': 'outback',
                'restaurantcount': 5
            }
        )
        
        with patch('app.ddbtable', table):
            result = updatevote('outback', 10)
            assert result == '10'
            
            # Verify the update actually happened
            updated_votes = readvote('outback')
            assert updated_votes == '10'


class TestFlaskRoutes:
    """Test Flask route handlers"""
    
    @pytest.fixture
    def client(self):
        """Create a test client for the Flask app"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_home_route(self, client):
        """Test the home route returns correct HTML"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Welcome to the Voting App' in response.data
        assert b'/api/outback' in response.data
        assert b'/api/getvotes' in response.data
    
    @mock_dynamodb
    def test_outback_route(self, client):
        """Test the outback voting route"""
        # Setup mock DynamoDB
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='test-votingapp-restaurants',
            KeySchema=[{'AttributeName': 'name', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'name', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Put initial data
        table.put_item(Item={'name': 'outback', 'restaurantcount': 5})
        
        with patch('app.ddbtable', table):
            response = client.get('/api/outback')
            assert response.status_code == 200
            assert response.data == b'6'  # Should increment from 5 to 6
    
    @mock_dynamodb
    def test_bucadibeppo_route(self, client):
        """Test the bucadibeppo voting route"""
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='test-votingapp-restaurants',
            KeySchema=[{'AttributeName': 'name', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'name', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        
        table.put_item(Item={'name': 'bucadibeppo', 'restaurantcount': 3})
        
        with patch('app.ddbtable', table):
            response = client.get('/api/bucadibeppo')
            assert response.status_code == 200
            assert response.data == b'4'
    
    @mock_dynamodb
    def test_ihop_route(self, client):
        """Test the ihop voting route"""
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='test-votingapp-restaurants',
            KeySchema=[{'AttributeName': 'name', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'name', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        
        table.put_item(Item={'name': 'ihop', 'restaurantcount': 7})
        
        with patch('app.ddbtable', table):
            response = client.get('/api/ihop')
            assert response.status_code == 200
            assert response.data == b'8'
    
    @mock_dynamodb
    def test_chipotle_route(self, client):
        """Test the chipotle voting route"""
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='test-votingapp-restaurants',
            KeySchema=[{'AttributeName': 'name', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'name', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        
        table.put_item(Item={'name': 'chipotle', 'restaurantcount': 2})
        
        with patch('app.ddbtable', table):
            response = client.get('/api/chipotle')
            assert response.status_code == 200
            assert response.data == b'3'
    
    @mock_dynamodb
    def test_getvotes_route(self, client):
        """Test the getvotes route returns all votes in JSON format"""
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='test-votingapp-restaurants',
            KeySchema=[{'AttributeName': 'name', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'name', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Setup test data for all restaurants
        restaurants = [
            {'name': 'outback', 'restaurantcount': 10},
            {'name': 'bucadibeppo', 'restaurantcount': 5},
            {'name': 'ihop', 'restaurantcount': 8},
            {'name': 'chipotle', 'restaurantcount': 12}
        ]
        
        for restaurant in restaurants:
            table.put_item(Item=restaurant)
        
        with patch('app.ddbtable', table):
            response = client.get('/api/getvotes')
            assert response.status_code == 200
            
            # Parse the returned JSON string
            response_data = response.data.decode('utf-8')
            parsed_data = json.loads(response_data)
            
            # Verify all restaurants are present with correct values
            assert len(parsed_data) == 4
            
            restaurant_votes = {item['name']: item['value'] for item in parsed_data}
            assert restaurant_votes['outback'] == 10
            assert restaurant_votes['bucadibeppo'] == 5
            assert restaurant_votes['ihop'] == 8
            assert restaurant_votes['chipotle'] == 12
    
    @mock_dynamodb
    @patch('app.Pool')
    @patch('app.cpu_count')
    def test_getheavyvotes_route(self, mock_cpu_count, mock_pool, client):
        """Test the getheavyvotes route with CPU and memory stress"""
        # Mock CPU count and multiprocessing Pool
        mock_cpu_count.return_value = 2
        mock_pool_instance = MagicMock()
        mock_pool.return_value = mock_pool_instance
        
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='test-votingapp-restaurants',
            KeySchema=[{'AttributeName': 'name', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'name', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Setup test data
        restaurants = [
            {'name': 'outback', 'restaurantcount': 15},
            {'name': 'bucadibeppo', 'restaurantcount': 7},
            {'name': 'ihop', 'restaurantcount': 9},
            {'name': 'chipotle', 'restaurantcount': 20}
        ]
        
        for restaurant in restaurants:
            table.put_item(Item=restaurant)
        
        with patch('app.ddbtable', table):
            response = client.get('/api/getheavyvotes')
            assert response.status_code == 200
            
            # Verify the response contains the same data as getvotes
            response_data = response.data.decode('utf-8')
            parsed_data = json.loads(response_data)
            
            restaurant_votes = {item['name']: item['value'] for item in parsed_data}
            assert restaurant_votes['outback'] == 15
            assert restaurant_votes['bucadibeppo'] == 7
            assert restaurant_votes['ihop'] == 9
            assert restaurant_votes['chipotle'] == 20
            
            # Verify that multiprocessing was called
            mock_pool.assert_called_once_with(2)
            mock_pool_instance.map.assert_called_once()


class TestEnvironmentVariables:
    """Test environment variable handling"""
    
    def test_default_environment_values(self):
        """Test that default environment variable values are set properly"""
        # Test that cpustressfactor and memstressfactor have default values
        assert cpustressfactor is not None
        assert memstressfactor is not None
    
    @patch.dict(os.environ, {'CPUSTRESSFACTOR': '3', 'MEMSTRESSFACTOR': '2'})
    def test_custom_environment_values(self):
        """Test that custom environment values are read correctly"""
        # We need to reload the module to get the new environment values
        import importlib
        import app
        importlib.reload(app)
        
        assert app.cpustressfactor == '3'
        assert app.memstressfactor == '2'


class TestErrorHandling:
    """Test error handling scenarios"""
    
    @pytest.fixture
    def client(self):
        """Create a test client for the Flask app"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    @patch('app.readvote')
    def test_route_with_dynamodb_error(self, mock_readvote, client):
        """Test route behavior when DynamoDB operations fail"""
        # Mock readvote to raise an exception
        mock_readvote.side_effect = Exception("DynamoDB connection failed")
        
        with pytest.raises(Exception):
            client.get('/api/outback')
    
    @patch('app.updatevote')
    @patch('app.readvote')
    def test_route_with_update_error(self, mock_readvote, mock_updatevote, client):
        """Test route behavior when vote update fails"""
        mock_readvote.return_value = '5'
        mock_updatevote.side_effect = Exception("Update failed")
        
        with pytest.raises(Exception):
            client.get('/api/outback')


if __name__ == '__main__':
    # Run tests with coverage
    pytest.main(['-v', '--cov=app', '--cov-report=html', '--cov-report=term'])
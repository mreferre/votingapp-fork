import unittest
from unittest.mock import patch, MagicMock, Mock
import os
import json
from multiprocessing import cpu_count
import boto3
from moto import mock_dynamodb

# Set up environment variables before importing app
os.environ['DDB_AWS_REGION'] = 'us-east-1'
os.environ['DDB_TABLE_NAME'] = 'test-votingapp-restaurants'
os.environ['CPUSTRESSFACTOR'] = '1'
os.environ['MEMSTRESSFACTOR'] = '1'

import app


class TestVotingApp(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        app.app.config['TESTING'] = True
        self.client = app.app.test_client()
        self.ctx = app.app.app_context()
        self.ctx.push()
        
    def tearDown(self):
        """Clean up after each test method."""
        self.ctx.pop()

    def test_f_function(self):
        """Test the CPU stress function f()"""
        # Test that the function executes without error
        try:
            app.f(1)
            # If we get here, the function completed successfully
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Function f() raised an exception: {e}")

    @mock_dynamodb
    def test_readvote_success(self):
        """Test successful vote reading from DynamoDB"""
        # Create mock DynamoDB table
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='test-votingapp-restaurants',
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
        
        # Add test data
        table.put_item(Item={'name': 'outback', 'restaurantcount': 5})
        
        # Mock the DynamoDB resource and table in app
        with patch.object(app, 'ddbtable', table):
            result = app.readvote('outback')
            self.assertEqual(result, '5')

    @mock_dynamodb
    def test_readvote_nonexistent_restaurant(self):
        """Test reading votes for non-existent restaurant"""
        # Create empty mock DynamoDB table
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='test-votingapp-restaurants',
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
        
        # Test reading non-existent restaurant
        with patch.object(app, 'ddbtable', table):
            with self.assertRaises(KeyError):
                app.readvote('nonexistent')

    @mock_dynamodb
    def test_updatevote_success(self):
        """Test successful vote update in DynamoDB"""
        # Create mock DynamoDB table
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='test-votingapp-restaurants',
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
        
        # Add initial data
        table.put_item(Item={'name': 'outback', 'restaurantcount': 5})
        
        # Mock the DynamoDB resource and table in app
        with patch.object(app, 'ddbtable', table):
            result = app.updatevote('outback', 10)
            self.assertEqual(result, '10')
            
            # Verify the update was successful
            response = table.get_item(Key={'name': 'outback'})
            self.assertEqual(response['Item']['restaurantcount'], 10)

    def test_home_route(self):
        """Test the home route"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to the Voting App', response.data)
        self.assertIn(b'/api/outback', response.data)
        self.assertIn(b'/api/bucadibeppo', response.data)
        self.assertIn(b'/api/ihop', response.data)
        self.assertIn(b'/api/chipotle', response.data)

    @patch.object(app, 'readvote')
    @patch.object(app, 'updatevote')
    def test_outback_route(self, mock_updatevote, mock_readvote):
        """Test the outback voting route"""
        mock_readvote.return_value = '5'
        mock_updatevote.return_value = '6'
        
        response = self.client.get('/api/outback')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), '6')
        
        mock_readvote.assert_called_once_with('outback')
        mock_updatevote.assert_called_once_with('outback', 6)

    @patch.object(app, 'readvote')
    @patch.object(app, 'updatevote')
    def test_bucadibeppo_route(self, mock_updatevote, mock_readvote):
        """Test the bucadibeppo voting route"""
        mock_readvote.return_value = '3'
        mock_updatevote.return_value = '4'
        
        response = self.client.get('/api/bucadibeppo')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), '4')
        
        mock_readvote.assert_called_once_with('bucadibeppo')
        mock_updatevote.assert_called_once_with('bucadibeppo', 4)

    @patch.object(app, 'readvote')
    @patch.object(app, 'updatevote')
    def test_ihop_route(self, mock_updatevote, mock_readvote):
        """Test the ihop voting route"""
        mock_readvote.return_value = '7'
        mock_updatevote.return_value = '8'
        
        response = self.client.get('/api/ihop')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), '8')
        
        mock_readvote.assert_called_once_with('ihop')
        mock_updatevote.assert_called_once_with('ihop', 8)

    @patch.object(app, 'readvote')
    @patch.object(app, 'updatevote')
    def test_chipotle_route(self, mock_updatevote, mock_readvote):
        """Test the chipotle voting route"""
        mock_readvote.return_value = '2'
        mock_updatevote.return_value = '3'
        
        response = self.client.get('/api/chipotle')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), '3')
        
        mock_readvote.assert_called_once_with('chipotle')
        mock_updatevote.assert_called_once_with('chipotle', 3)

    @patch.object(app, 'readvote')
    def test_getvotes_route(self, mock_readvote):
        """Test the getvotes route"""
        # Mock return values for each restaurant
        mock_readvote.side_effect = ['5', '3', '8', '2']  # outback, ihop, bucadibeppo, chipotle
        
        response = self.client.get('/api/getvotes')
        self.assertEqual(response.status_code, 200)
        
        # Parse the response and verify JSON structure
        response_data = response.data.decode()
        expected_json = '[{"name": "outback", "value": 5},{"name": "bucadibeppo", "value": 8},{"name": "ihop", "value": 3}, {"name": "chipotle", "value": 2}]'
        
        # Verify the response contains all restaurants
        self.assertIn('"name": "outback"', response_data)
        self.assertIn('"name": "bucadibeppo"', response_data)
        self.assertIn('"name": "ihop"', response_data)
        self.assertIn('"name": "chipotle"', response_data)
        
        # Verify readvote was called for each restaurant
        self.assertEqual(mock_readvote.call_count, 4)

    @patch('app.Pool')
    @patch.object(app, 'readvote')
    @patch('app.randrange')
    def test_getheavyvotes_route(self, mock_randrange, mock_readvote, mock_pool_class):
        """Test the getheavyvotes route with CPU and memory stress"""
        # Mock return values
        mock_readvote.side_effect = ['5', '3', '8', '2']
        mock_randrange.return_value = 1000
        
        # Mock the Pool class and its methods
        mock_pool = MagicMock()
        mock_pool_class.return_value = mock_pool
        
        response = self.client.get('/api/getheavyvotes')
        self.assertEqual(response.status_code, 200)
        
        # Verify the response contains all restaurants
        response_data = response.data.decode()
        self.assertIn('"name": "outback"', response_data)
        self.assertIn('"name": "bucadibeppo"', response_data)
        self.assertIn('"name": "ihop"', response_data)
        self.assertIn('"name": "chipotle"', response_data)
        
        # Verify CPU stress components were called
        mock_pool_class.assert_called_once_with(cpu_count())
        mock_pool.map.assert_called_once()
        
        # Verify memory stress component
        mock_randrange.assert_called_once_with(10000)


class TestEnvironmentVariables(unittest.TestCase):
    """Test environment variable handling"""
    
    def test_default_environment_variables(self):
        """Test default values when environment variables are not set"""
        # These should match the defaults in app.py
        self.assertEqual(str(app.cpustressfactor), '1')
        self.assertEqual(str(app.memstressfactor), '1')
        self.assertEqual(app.ddb_table_name, 'test-votingapp-restaurants')  # Set in our test setup

    def test_custom_environment_variables(self):
        """Test that environment variables are properly read"""
        # Save original values
        original_cpu = os.environ.get('CPUSTRESSFACTOR', '1')
        original_mem = os.environ.get('MEMSTRESSFACTOR', '1')
        
        # Set custom values
        os.environ['CPUSTRESSFACTOR'] = '5'
        os.environ['MEMSTRESSFACTOR'] = '3'
        
        try:
            # Re-import app to pick up new environment variables
            import importlib
            importlib.reload(app)
            
            self.assertEqual(str(app.cpustressfactor), '5')
            self.assertEqual(str(app.memstressfactor), '3')
        finally:
            # Restore original values
            if original_cpu == '1':
                os.environ.pop('CPUSTRESSFACTOR', None)
            else:
                os.environ['CPUSTRESSFACTOR'] = original_cpu
                
            if original_mem == '1':
                os.environ.pop('MEMSTRESSFACTOR', None)
            else:
                os.environ['MEMSTRESSFACTOR'] = original_mem
                
            # Reload app again to restore original state
            importlib.reload(app)


if __name__ == '__main__':
    unittest.main()
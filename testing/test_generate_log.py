# testing/test_generate_log.py

import os
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from generate_log import generate_log

def test_log_file_created():
    """Test that the log file is created with today's date in the filename."""
    with patch('generate_log.datetime') as mock_datetime:
        mock_datetime.now.return_value.strftime.return_value = '20230101'
        with patch('generate_log.open', create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file
            
            args = type('Args', (), {})()  # Create simple args object
            generate_log(args)
            
            mock_open.assert_called_once_with('log_20230101.txt', 'w')

def test_log_file_name_format():
    """Test that the filename follows the expected naming convention."""
    with patch('generate_log.datetime') as mock_datetime:
        mock_datetime.now.return_value.strftime.return_value = '20230101'
        with patch('generate_log.open', create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file
            
            args = type('Args', (), {})()  # Create simple args object
            generate_log(args)
            
            mock_open.assert_called_once_with('log_20230101.txt', 'w')

def test_log_file_content_matches_expected():
    """Test that the content written to the log matches the expected hardcoded list."""
    with patch('generate_log.datetime') as mock_datetime:
        mock_datetime.now.return_value.strftime.return_value = '20230101'
        with patch('generate_log.open', create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file
            
            args = type('Args', (), {})()  # Create simple args object
            generate_log(args)
            
            # Check that write was called with the expected log entries
            expected_calls = [
                'User logged in\n',
                'User updated profile\n', 
                'Report exported\n'
            ]
            for expected_call in expected_calls:
                mock_file.write.assert_any_call(expected_call)

def test_generate_log_prints_confirmation_message():
    """Test that the function prints a confirmation message."""
    with patch('generate_log.datetime') as mock_datetime:
        mock_datetime.now.return_value.strftime.return_value = '20230101'
        with patch('builtins.print') as mock_print:
            args = type('Args', (), {})()  # Create simple args object
            generate_log(args)
            
            mock_print.assert_called_once_with('Log written to log_20230101.txt')

def test_log_file_is_created_and_removed():
    """Test that the log file is created and can be removed."""
    with patch('generate_log.datetime') as mock_datetime:
        mock_datetime.now.return_value.strftime.return_value = '20230101'
        
        # Create a real file for this test
        args = type('Args', (), {})()  # Create simple args object
        generate_log(args)
        
        # Check that file was created
        filename = 'log_20230101.txt'
        assert os.path.exists(filename), f"{filename} not found."
        
        # Check file contents
        with open(filename, 'r') as f:
            content = f.read()
            assert 'User logged in' in content
            assert 'User updated profile' in content
            assert 'Report exported' in content
        
        # Clean up
        if os.path.exists(filename):
            os.remove(filename)

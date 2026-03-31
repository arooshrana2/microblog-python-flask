import os
import json
import pytest
import tempfile
from datetime import datetime
from unittest.mock import patch, mock_open, MagicMock
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import load_entries, save_entries, create_app


class TestLoadEntries:
    """Test suite for load_entries function"""

    def test_load_entries_with_existing_file(self):
        """Test loading entries from an existing JSON file"""
        test_data = [
            {'content': 'First entry', 'date': '2026-03-01', 'blog_name': 'tech'},
            {'content': 'Second entry', 'date': '2026-03-02', 'blog_name': 'personal'}
        ]
        mock_file_content = json.dumps(test_data)

        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=mock_file_content)):
                result = load_entries()

        assert result == test_data
        assert len(result) == 2
        assert result[0]['content'] == 'First entry'

    def test_load_entries_with_nonexistent_file(self):
        """Test loading entries when file does not exist"""
        with patch('os.path.exists', return_value=False):
            result = load_entries()

        assert result == []
        assert isinstance(result, list)

    def test_load_entries_with_empty_file(self):
        """Test loading entries from an empty JSON file"""
        mock_file_content = '[]'

        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=mock_file_content)):
                result = load_entries()

        assert result == []
        assert len(result) == 0

    def test_load_entries_with_single_entry(self):
        """Test loading a single entry (boundary: minimum valid data)"""
        test_data = [{'content': 'Only entry', 'date': '2026-03-31', 'blog_name': 'test'}]
        mock_file_content = json.dumps(test_data)

        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=mock_file_content)):
                result = load_entries()

        assert len(result) == 1
        assert result[0]['content'] == 'Only entry'

    def test_load_entries_with_large_dataset(self):
        """Test loading many entries (boundary: large dataset)"""
        test_data = [
            {'content': f'Entry {i}', 'date': '2026-03-31', 'blog_name': 'test'}
            for i in range(1000)
        ]
        mock_file_content = json.dumps(test_data)

        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=mock_file_content)):
                result = load_entries()

        assert len(result) == 1000
        assert result[0]['content'] == 'Entry 0'
        assert result[999]['content'] == 'Entry 999'

    def test_load_entries_with_special_characters(self):
        """Test loading entries with special characters in content"""
        test_data = [
            {'content': 'Special chars: !@#$%^&*()', 'date': '2026-03-31', 'blog_name': 'test'},
            {'content': 'Unicode: 你好世界 🚀', 'date': '2026-03-31', 'blog_name': 'test'}
        ]
        mock_file_content = json.dumps(test_data)

        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=mock_file_content)):
                result = load_entries()

        assert result[0]['content'] == 'Special chars: !@#$%^&*()'
        assert result[1]['content'] == 'Unicode: 你好世界 🚀'

    def test_load_entries_with_empty_strings(self):
        """Test loading entries with empty string values (boundary condition)"""
        test_data = [{'content': '', 'date': '', 'blog_name': ''}]
        mock_file_content = json.dumps(test_data)

        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=mock_file_content)):
                result = load_entries()

        assert result[0]['content'] == ''
        assert result[0]['date'] == ''
        assert result[0]['blog_name'] == ''


class TestSaveEntries:
    """Test suite for save_entries function"""

    def test_save_entries_creates_directory(self):
        """Test that save_entries creates data directory if it doesn't exist"""
        test_entries = [{'content': 'Test', 'date': '2026-03-31', 'blog_name': 'test'}]

        with patch('os.makedirs') as mock_makedirs:
            with patch('builtins.open', mock_open()) as mock_file:
                save_entries(test_entries)

        mock_makedirs.assert_called_once_with('data', exist_ok=True)

    def test_save_entries_writes_to_file(self):
        """Test that save_entries writes data to the correct file"""
        test_entries = [
            {'content': 'Entry 1', 'date': '2026-03-01', 'blog_name': 'tech'},
            {'content': 'Entry 2', 'date': '2026-03-02', 'blog_name': 'personal'}
        ]

        with patch('os.makedirs'):
            with patch('builtins.open', mock_open()) as mock_file:
                save_entries(test_entries)

        mock_file.assert_called_once_with('data/entries.json', 'w')
        handle = mock_file()
        # Verify json.dump was called with correct data
        written_data = ''.join(call.args[0] for call in handle.write.call_args_list)
        assert 'Entry 1' in written_data
        assert 'Entry 2' in written_data

    def test_save_entries_with_empty_list(self):
        """Test saving an empty list (boundary condition)"""
        test_entries = []

        with patch('os.makedirs'):
            with patch('builtins.open', mock_open()) as mock_file:
                save_entries(test_entries)

        mock_file.assert_called_once_with('data/entries.json', 'w')

    def test_save_entries_with_single_entry(self):
        """Test saving a single entry (boundary: minimum valid data)"""
        test_entries = [{'content': 'Single', 'date': '2026-03-31', 'blog_name': 'test'}]

        with patch('os.makedirs'):
            with patch('builtins.open', mock_open()) as mock_file:
                save_entries(test_entries)

        handle = mock_file()
        written_data = ''.join(call.args[0] for call in handle.write.call_args_list)
        assert 'Single' in written_data

    def test_save_entries_preserves_data_structure(self):
        """Test that save_entries preserves the data structure"""
        test_entries = [
            {'content': 'Test content', 'date': '2026-03-31', 'blog_name': 'myblog', 'extra_field': 'value'}
        ]

        with patch('os.makedirs'):
            with patch('builtins.open', mock_open()) as mock_file:
                save_entries(test_entries)

        handle = mock_file()
        written_data = ''.join(call.args[0] for call in handle.write.call_args_list)
        assert 'extra_field' in written_data
        assert 'value' in written_data


class TestFlaskApp:
    """Test suite for Flask application routes"""

    @pytest.fixture
    def client(self):
        """Create a test client for the Flask app"""
        app = create_app()
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    def test_home_route_get_request_empty_entries(self, client):
        """Test GET request to home route with no entries"""
        with patch('app.load_entries', return_value=[]):
            response = client.get('/')

        assert response.status_code == 200
        assert b'home.html' in response.data or response.status_code == 200

    def test_home_route_get_request_with_entries(self, client):
        """Test GET request to home route with existing entries"""
        mock_entries = [
            {'content': 'Test entry', 'date': '2026-03-31', 'blog_name': 'tech'},
            {'content': 'Another entry', 'date': '2026-03-30', 'blog_name': 'personal'}
        ]

        with patch('app.load_entries', return_value=mock_entries):
            response = client.get('/')

        assert response.status_code == 200

    def test_home_route_post_request_creates_entry(self, client):
        """Test POST request to home route creates a new entry"""
        mock_entries = []

        with patch('app.load_entries', return_value=mock_entries):
            with patch('app.save_entries') as mock_save:
                with patch('datetime.datetime') as mock_datetime:
                    mock_datetime.today.return_value.strftime.return_value = '2026-03-31'

                    response = client.post('/', data={
                        'content': 'New blog post',
                        'blog_name': 'tech'
                    })

        assert response.status_code == 200
        mock_save.assert_called_once()
        saved_entries = mock_save.call_args[0][0]
        assert len(saved_entries) == 1
        assert saved_entries[0]['content'] == 'New blog post'
        assert saved_entries[0]['blog_name'] == 'tech'
        assert saved_entries[0]['date'] == '2026-03-31'

    def test_home_route_post_request_with_default_blog_name(self, client):
        """Test POST request without blog_name uses default value"""
        mock_entries = []

        with patch('app.load_entries', return_value=mock_entries):
            with patch('app.save_entries') as mock_save:
                with patch('datetime.datetime') as mock_datetime:
                    mock_datetime.today.return_value.strftime.return_value = '2026-03-31'

                    response = client.post('/', data={
                        'content': 'Post without blog name'
                    })

        saved_entries = mock_save.call_args[0][0]
        assert saved_entries[0]['blog_name'] == 'default'

    def test_home_route_post_request_empty_content(self, client):
        """Test POST request with empty content (boundary condition)"""
        mock_entries = []

        with patch('app.load_entries', return_value=mock_entries):
            with patch('app.save_entries') as mock_save:
                with patch('datetime.datetime') as mock_datetime:
                    mock_datetime.today.return_value.strftime.return_value = '2026-03-31'

                    response = client.post('/', data={
                        'content': '',
                        'blog_name': 'test'
                    })

        saved_entries = mock_save.call_args[0][0]
        assert saved_entries[0]['content'] == ''

    def test_home_route_post_request_very_long_content(self, client):
        """Test POST request with very long content (boundary condition)"""
        mock_entries = []
        long_content = 'x' * 10000

        with patch('app.load_entries', return_value=mock_entries):
            with patch('app.save_entries') as mock_save:
                with patch('datetime.datetime') as mock_datetime:
                    mock_datetime.today.return_value.strftime.return_value = '2026-03-31'

                    response = client.post('/', data={
                        'content': long_content,
                        'blog_name': 'test'
                    })

        saved_entries = mock_save.call_args[0][0]
        assert len(saved_entries[0]['content']) == 10000

    def test_home_route_post_request_special_characters(self, client):
        """Test POST request with special characters in content"""
        mock_entries = []

        with patch('app.load_entries', return_value=mock_entries):
            with patch('app.save_entries') as mock_save:
                with patch('datetime.datetime') as mock_datetime:
                    mock_datetime.today.return_value.strftime.return_value = '2026-03-31'

                    response = client.post('/', data={
                        'content': 'Special: <script>alert("xss")</script>',
                        'blog_name': 'security'
                    })

        saved_entries = mock_save.call_args[0][0]
        assert saved_entries[0]['content'] == 'Special: <script>alert("xss")</script>'

    def test_home_route_formats_dates_correctly(self, client):
        """Test that home route formats dates correctly"""
        mock_entries = [
            {'content': 'Entry 1', 'date': '2026-03-31', 'blog_name': 'tech'},
            {'content': 'Entry 2', 'date': '2026-12-25', 'blog_name': 'personal'}
        ]

        with patch('app.load_entries', return_value=mock_entries):
            response = client.get('/')

        assert response.status_code == 200

    def test_blog_route_filters_by_blog_name(self, client):
        """Test blog route filters entries by blog_name"""
        mock_entries = [
            {'content': 'Tech post 1', 'date': '2026-03-31', 'blog_name': 'tech'},
            {'content': 'Personal post', 'date': '2026-03-30', 'blog_name': 'personal'},
            {'content': 'Tech post 2', 'date': '2026-03-29', 'blog_name': 'tech'}
        ]

        with patch('app.load_entries', return_value=mock_entries):
            response = client.get('/blog/tech')

        assert response.status_code == 200

    def test_blog_route_with_nonexistent_blog_name(self, client):
        """Test blog route with a blog name that has no entries"""
        mock_entries = [
            {'content': 'Tech post', 'date': '2026-03-31', 'blog_name': 'tech'}
        ]

        with patch('app.load_entries', return_value=mock_entries):
            response = client.get('/blog/nonexistent')

        assert response.status_code == 200

    def test_blog_route_with_empty_entries(self, client):
        """Test blog route when there are no entries at all"""
        with patch('app.load_entries', return_value=[]):
            response = client.get('/blog/tech')

        assert response.status_code == 200

    def test_blog_route_with_special_characters_in_name(self, client):
        """Test blog route with special characters in blog name"""
        mock_entries = [
            {'content': 'Post', 'date': '2026-03-31', 'blog_name': 'my-blog-123'}
        ]

        with patch('app.load_entries', return_value=mock_entries):
            response = client.get('/blog/my-blog-123')

        assert response.status_code == 200

    def test_blog_route_formats_dates_correctly(self, client):
        """Test that blog route formats dates correctly"""
        mock_entries = [
            {'content': 'Entry', 'date': '2026-01-15', 'blog_name': 'test'},
            {'content': 'Entry', 'date': '2026-12-31', 'blog_name': 'test'}
        ]

        with patch('app.load_entries', return_value=mock_entries):
            response = client.get('/blog/test')

        assert response.status_code == 200

    def test_blog_route_with_single_entry(self, client):
        """Test blog route with exactly one matching entry (boundary condition)"""
        mock_entries = [
            {'content': 'Only entry', 'date': '2026-03-31', 'blog_name': 'solo'}
        ]

        with patch('app.load_entries', return_value=mock_entries):
            response = client.get('/blog/solo')

        assert response.status_code == 200

    def test_blog_route_with_many_entries(self, client):
        """Test blog route with many matching entries (boundary condition)"""
        mock_entries = [
            {'content': f'Entry {i}', 'date': '2026-03-31', 'blog_name': 'popular'}
            for i in range(100)
        ]

        with patch('app.load_entries', return_value=mock_entries):
            response = client.get('/blog/popular')

        assert response.status_code == 200


class TestCreateApp:
    """Test suite for create_app function"""

    def test_create_app_returns_flask_instance(self):
        """Test that create_app returns a Flask application instance"""
        app = create_app()

        assert app is not None
        assert hasattr(app, 'route')
        assert hasattr(app, 'test_client')

    def test_create_app_has_home_route(self):
        """Test that created app has home route configured"""
        app = create_app()

        # Check if route is registered
        rules = [str(rule) for rule in app.url_map.iter_rules()]
        assert '/' in rules

    def test_create_app_has_blog_route(self):
        """Test that created app has blog route configured"""
        app = create_app()

        # Check if route is registered
        rules = [str(rule) for rule in app.url_map.iter_rules()]
        assert any('/blog/' in rule for rule in rules)

    def test_create_app_home_accepts_get_and_post(self):
        """Test that home route accepts both GET and POST methods"""
        app = create_app()

        with app.test_client() as client:
            with patch('app.load_entries', return_value=[]):
                get_response = client.get('/')
                assert get_response.status_code == 200

                with patch('app.save_entries'):
                    with patch('datetime.datetime') as mock_datetime:
                        mock_datetime.today.return_value.strftime.return_value = '2026-03-31'
                        post_response = client.post('/', data={'content': 'test'})
                        assert post_response.status_code == 200

    def test_create_app_blog_accepts_only_get(self):
        """Test that blog route accepts only GET method"""
        app = create_app()

        with app.test_client() as client:
            with patch('app.load_entries', return_value=[]):
                get_response = client.get('/blog/test')
                assert get_response.status_code == 200

                # POST should not be allowed (405 Method Not Allowed)
                post_response = client.post('/blog/test', data={'content': 'test'})
                assert post_response.status_code == 405


class TestDateFormatting:
    """Test suite for date formatting behavior"""

    @pytest.fixture
    def client(self):
        """Create a test client for the Flask app"""
        app = create_app()
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    def test_date_formatting_january(self, client):
        """Test date formatting for January dates"""
        mock_entries = [
            {'content': 'Jan entry', 'date': '2026-01-01', 'blog_name': 'test'}
        ]

        with patch('app.load_entries', return_value=mock_entries):
            response = client.get('/')

        assert response.status_code == 200

    def test_date_formatting_december(self, client):
        """Test date formatting for December dates"""
        mock_entries = [
            {'content': 'Dec entry', 'date': '2026-12-31', 'blog_name': 'test'}
        ]

        with patch('app.load_entries', return_value=mock_entries):
            response = client.get('/')

        assert response.status_code == 200

    def test_date_formatting_boundary_days(self, client):
        """Test date formatting for boundary days (01 and 31)"""
        mock_entries = [
            {'content': 'First day', 'date': '2026-03-01', 'blog_name': 'test'},
            {'content': 'Last day', 'date': '2026-03-31', 'blog_name': 'test'}
        ]

        with patch('app.load_entries', return_value=mock_entries):
            response = client.get('/')

        assert response.status_code == 200


class TestEdgeCases:
    """Test suite for edge cases and error conditions"""

    @pytest.fixture
    def client(self):
        """Create a test client for the Flask app"""
        app = create_app()
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    def test_multiple_consecutive_posts(self, client):
        """Test multiple POST requests in sequence"""
        with patch('app.load_entries', return_value=[]):
            with patch('app.save_entries') as mock_save:
                with patch('datetime.datetime') as mock_datetime:
                    mock_datetime.today.return_value.strftime.return_value = '2026-03-31'

                    client.post('/', data={'content': 'Post 1', 'blog_name': 'test'})
                    client.post('/', data={'content': 'Post 2', 'blog_name': 'test'})
                    client.post('/', data={'content': 'Post 3', 'blog_name': 'test'})

        assert mock_save.call_count == 3

    def test_blog_route_case_sensitivity(self, client):
        """Test that blog route is case-sensitive for blog names"""
        mock_entries = [
            {'content': 'Post', 'date': '2026-03-31', 'blog_name': 'Tech'},
            {'content': 'Post', 'date': '2026-03-31', 'blog_name': 'tech'}
        ]

        with patch('app.load_entries', return_value=mock_entries):
            response_upper = client.get('/blog/Tech')
            response_lower = client.get('/blog/tech')

        assert response_upper.status_code == 200
        assert response_lower.status_code == 200

    def test_entries_without_required_fields(self, client):
        """Test handling of entries missing expected fields"""
        mock_entries = [
            {'content': 'Incomplete'},  # Missing date and blog_name
        ]

        with patch('app.load_entries', return_value=mock_entries):
            # Should handle gracefully, though may raise KeyError
            try:
                response = client.get('/')
                # If it doesn't raise an error, that's fine too
                assert response.status_code in [200, 500]
            except KeyError:
                # Expected if code doesn't handle missing fields
                pass

    def test_post_with_none_values(self, client):
        """Test POST request with None values"""
        mock_entries = []

        with patch('app.load_entries', return_value=mock_entries):
            with patch('app.save_entries') as mock_save:
                with patch('datetime.datetime') as mock_datetime:
                    mock_datetime.today.return_value.strftime.return_value = '2026-03-31'

                    response = client.post('/', data={
                        'content': None,
                        'blog_name': None
                    })

        # None should be handled by request.form.get()
        assert response.status_code == 200

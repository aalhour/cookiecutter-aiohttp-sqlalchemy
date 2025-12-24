"""
Unit tests for Example API Controller.

Tests all CRUD operations: Create, Read, Update, Delete.
"""
from unittest import mock
from unittest.mock import AsyncMock, patch

from tests.fixtures.database import TransactionalSessionFixture
from tests.fixtures.models.example import ExampleFixture


class TestHttpGetAllUnitTestCase:
    """Tests for GET /api/v1.0/examples endpoint."""

    @patch('{{cookiecutter.app_name}}.models.example.Example.get_all', new_callable=AsyncMock)
    @patch('{{cookiecutter.app_name}}.controllers.example_api.transactional_session')
    async def test_returns_data_from_model_successfully(self, session, get_all_examples, client):
        # Arrange
        session_mock = mock.MagicMock(name='transactional_session_mock')
        session.return_value = TransactionalSessionFixture(target_mock=session_mock)
        get_all_examples.return_value = ExampleFixture.get_all.success.output()

        # Act
        response = await client.get("/api/v1.0/examples")

        # Assert
        assert response.status == 200
        json_response = await response.json()
        assert isinstance(json_response, list)
        assert len(json_response) == 3
        get_all_examples.assert_called_once()

    @patch('{{cookiecutter.app_name}}.models.example.Example.get_all', new_callable=AsyncMock)
    @patch('{{cookiecutter.app_name}}.controllers.example_api.transactional_session')
    async def test_returns_empty_list_when_model_is_empty(self, session, get_all_examples, client):
        # Arrange
        session_mock = mock.MagicMock(name='transactional_session_mock')
        session.return_value = TransactionalSessionFixture(target_mock=session_mock)
        get_all_examples.return_value = ExampleFixture.get_all.empty_list.output()

        # Act
        response = await client.get("/api/v1.0/examples")

        # Assert
        assert response.status == 200
        json_response = await response.json()
        assert isinstance(json_response, list)
        assert len(json_response) == 0


class TestHttpGetByIdUnitTestCase:
    """Tests for GET /api/v1.0/examples/{id} endpoint."""

    @patch('{{cookiecutter.app_name}}.models.example.Example.get_by_id', new_callable=AsyncMock)
    @patch('{{cookiecutter.app_name}}.controllers.example_api.transactional_session')
    async def test_success(self, session, get_by_id, client):
        # Arrange
        example_id = "1"
        session_mock = mock.MagicMock(name='transactional_session_mock')
        session.return_value = TransactionalSessionFixture(target_mock=session_mock)
        get_by_id.return_value = ExampleFixture.get_by_id.success.output()

        # Act
        response = await client.get(f"/api/v1.0/examples/{example_id}")

        # Assert
        assert response.status == 200
        json_response = await response.json()
        assert isinstance(json_response, dict)
        assert 'id' in json_response
        assert 'name' in json_response

    @patch('{{cookiecutter.app_name}}.models.example.Example.get_by_id', new_callable=AsyncMock)
    @patch('{{cookiecutter.app_name}}.controllers.example_api.transactional_session')
    async def test_returns_404_if_resource_not_found(self, session, get_by_id, client):
        # Arrange
        example_id = "9999"
        session_mock = mock.MagicMock(name='transactional_session_mock')
        session.return_value = TransactionalSessionFixture(target_mock=session_mock)
        get_by_id.return_value = ExampleFixture.get_by_id.none.output()

        # Act
        response = await client.get(f"/api/v1.0/examples/{example_id}")

        # Assert
        assert response.status == 404
        json_response = await response.json()
        assert isinstance(json_response, dict)
        assert 'message' in json_response


class TestHttpCreateUnitTestCase:
    """Tests for POST /api/v1.0/examples endpoint."""

    @patch('{{cookiecutter.app_name}}.models.example.Example.create', new_callable=AsyncMock)
    @patch('{{cookiecutter.app_name}}.controllers.example_api.transactional_session')
    async def test_creates_example_successfully(self, session, create_example, client):
        # Arrange
        session_mock = mock.MagicMock(name='transactional_session_mock')
        session.return_value = TransactionalSessionFixture(target_mock=session_mock)
        create_example.return_value = ExampleFixture.create.success.output()

        payload = {
            "name": "New Example",
            "description": "Test description",
            "price": 29.99,
            "is_active": True
        }

        # Act
        response = await client.post("/api/v1.0/examples", json=payload)

        # Assert
        assert response.status == 201
        json_response = await response.json()
        assert isinstance(json_response, dict)
        assert 'id' in json_response
        create_example.assert_called_once()

    @patch('{{cookiecutter.app_name}}.controllers.example_api.transactional_session')
    async def test_returns_422_when_name_is_missing(self, session, client):
        # Arrange - Pydantic validation returns 422 for validation errors
        session_mock = mock.MagicMock(name='transactional_session_mock')
        session.return_value = TransactionalSessionFixture(target_mock=session_mock)

        payload = {
            "description": "Missing name field"
        }

        # Act
        response = await client.post("/api/v1.0/examples", json=payload)

        # Assert - Pydantic validation error returns 422
        assert response.status == 422
        json_response = await response.json()
        assert 'error' in json_response
        assert json_response['error'] == 'validation_error'


class TestHttpUpdateUnitTestCase:
    """Tests for PUT /api/v1.0/examples/{id} endpoint."""

    @patch('{{cookiecutter.app_name}}.models.example.Example.get_by_id', new_callable=AsyncMock)
    @patch('{{cookiecutter.app_name}}.controllers.example_api.transactional_session')
    async def test_updates_example_successfully(self, session, get_by_id, client):
        # Arrange
        example_id = "1"
        session_mock = mock.MagicMock(name='transactional_session_mock')
        session.return_value = TransactionalSessionFixture(target_mock=session_mock)

        mock_example = ExampleFixture.get_by_id.success.output()
        mock_example.update = AsyncMock(return_value=mock_example)
        get_by_id.return_value = mock_example

        payload = {
            "name": "Updated Example",
            "price": 39.99
        }

        # Act
        response = await client.put(f"/api/v1.0/examples/{example_id}", json=payload)

        # Assert
        assert response.status == 200
        json_response = await response.json()
        assert isinstance(json_response, dict)

    @patch('{{cookiecutter.app_name}}.models.example.Example.get_by_id', new_callable=AsyncMock)
    @patch('{{cookiecutter.app_name}}.controllers.example_api.transactional_session')
    async def test_returns_404_when_example_not_found(self, session, get_by_id, client):
        # Arrange
        example_id = "9999"
        session_mock = mock.MagicMock(name='transactional_session_mock')
        session.return_value = TransactionalSessionFixture(target_mock=session_mock)
        get_by_id.return_value = None

        payload = {"name": "Updated Example"}

        # Act
        response = await client.put(f"/api/v1.0/examples/{example_id}", json=payload)

        # Assert
        assert response.status == 404


class TestHttpDeleteUnitTestCase:
    """Tests for DELETE /api/v1.0/examples/{id} endpoint."""

    @patch('{{cookiecutter.app_name}}.models.example.Example.delete_by_id', new_callable=AsyncMock)
    @patch('{{cookiecutter.app_name}}.controllers.example_api.transactional_session')
    async def test_deletes_example_successfully(self, session, delete_by_id, client):
        # Arrange
        example_id = "1"
        session_mock = mock.MagicMock(name='transactional_session_mock')
        session.return_value = TransactionalSessionFixture(target_mock=session_mock)
        delete_by_id.return_value = True

        # Act
        response = await client.delete(f"/api/v1.0/examples/{example_id}")

        # Assert
        assert response.status == 200
        json_response = await response.json()
        assert 'message' in json_response

    @patch('{{cookiecutter.app_name}}.models.example.Example.delete_by_id', new_callable=AsyncMock)
    @patch('{{cookiecutter.app_name}}.controllers.example_api.transactional_session')
    async def test_returns_404_when_example_not_found(self, session, delete_by_id, client):
        # Arrange
        example_id = "9999"
        session_mock = mock.MagicMock(name='transactional_session_mock')
        session.return_value = TransactionalSessionFixture(target_mock=session_mock)
        delete_by_id.return_value = False

        # Act
        response = await client.delete(f"/api/v1.0/examples/{example_id}")

        # Assert
        assert response.status == 404

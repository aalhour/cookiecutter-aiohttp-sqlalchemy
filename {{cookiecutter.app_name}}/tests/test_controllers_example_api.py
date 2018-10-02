from unittest import mock

import asynctest

from tests.fixtures.database import TransactionalSessionFixture
from tests.fixtures.models.example import ExampleFixture


class HttpGetAllUnitTestCase:
    @asynctest.patch('{{cookiecutter.app_name}}.models.example.Example.get_all')
    @asynctest.patch('{{cookiecutter.app_name}}.controllers.example_api.transactional_session')
    async def test_returns_data_from_model_successfully(self, session, get_all_examples, client):
        ###
        # Arrange
        session.return_value = TransactionalSessionFixture()
        get_all_examples.return_value = ExampleFixture.get_all.success.output()

        ###
        # Act
        response = await client.get("/api/v1.0/examples")

        ###
        # Assert
        assert response.status == 200
        json_response = await response.json()
        assert isinstance(json_response, list)
        assert len(json_response) == 3
        get_all_examples.assert_called_once_with(session=mock.ANY)

    @asynctest.patch('{{cookiecutter.app_name}}.models.example.Example.get_all')
    @asynctest.patch('{{cookiecutter.app_name}}.controllers.example_api.transactional_session')
    async def test_returns_empty_list_when_model_is_empty(self, session, get_all_examples, client):
        ###
        # Arrange
        session.return_value = TransactionalSessionFixture()
        get_all_examples.return_value = ExampleFixture.get_all.empty_list.output()

        ###
        # Act
        response = await client.get("/api/v1.0/examples")

        ###
        # Assert
        assert response.status == 200
        json_response = await response.json()
        assert isinstance(json_response, list)
        assert len(json_response) == 0
        get_all_examples.assert_called_once_with(session=mock.ANY)


class HttpGetByIdUnitTestCase:
    @asynctest.patch('{{cookiecutter.app_name}}.models.example.Example.get_by_id')
    @asynctest.patch('{{cookiecutter.app_name}}.controllers.example_api.transactional_session')
    async def test_success(self, session, get_by_id, client):
        ###
        # Arrange
        session.return_value = TransactionalSessionFixture()
        get_by_id.return_value = ExampleFixture.get_by_id.success.output()

        ###
        # Act
        response = await client.get("/api/v1.0/examples")

        ###
        # Assert
        assert response.status == 200
        json_response = await response.json()
        assert isinstance(json_response, dict)
        get_by_id.assert_called_once_with(session=mock.ANY)


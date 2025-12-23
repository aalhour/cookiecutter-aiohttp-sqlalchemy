from datetime import datetime, timezone
from random import randint
from typing import Any
from uuid import uuid4

from example_web_app.models.example import Example


class ExampleFixture:
    """Test fixtures for Example model."""

    user_input_template: dict[str, Any] = {
        "name": f"test_example_{uuid4()}",
        "description": "Test description",
        "price": 19.99,
        "is_active": True,
    }

    expected_db_data_template: dict[str, Any] = {
        **user_input_template,
        "id": randint(1_000, 10_000),
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }

    @classmethod
    def create_mock(
        cls,
        user_input: dict[str, Any] | None = None,
        expected_db_data: dict[str, Any] | None = None,
    ) -> Example:
        """
        Creates a new mocked Example and returns it.
        """
        _user_input = {**cls.user_input_template, **(user_input or {})}
        _expected_db_data = {**cls.expected_db_data_template, **(expected_db_data or {})}

        example_instance = Example(
            name=_user_input.get("name"),
            description=_user_input.get("description"),
            price=_user_input.get("price"),
            is_active=_user_input.get("is_active", True),
        )

        for attr_name, attr_value in _expected_db_data.items():
            setattr(example_instance, attr_name, attr_value)

        return example_instance

    class get_by_id:
        class success:
            @staticmethod
            def output() -> Example:
                return ExampleFixture.create_mock()

        class none:
            @staticmethod
            def output() -> Example | None:
                return None

    class get_all:
        class success:
            @staticmethod
            def output() -> list[Example]:
                return [ExampleFixture.create_mock() for _ in range(3)]

        class empty_list:
            @staticmethod
            def output() -> list[Example]:
                return []

    class create:
        class success:
            @staticmethod
            def output() -> Example:
                return ExampleFixture.create_mock()

    class update:
        class success:
            @staticmethod
            def output() -> Example:
                return ExampleFixture.create_mock(
                    user_input={"name": "Updated Example"}
                )

    class delete_by_id:
        class success:
            @staticmethod
            def output() -> bool:
                return True

        class not_found:
            @staticmethod
            def output() -> bool:
                return False

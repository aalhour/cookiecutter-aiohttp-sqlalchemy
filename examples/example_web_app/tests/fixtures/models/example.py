from uuid import uuid4
from random import randint
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from example_web_app.models.example import Example


class ExampleFixture:
    user_input_template = {
        "name": f"test_example_{uuid4()}"
    }

    expected_db_data_template = {
        **user_input_template,
        "id": randint(1_000, 10_000),
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }

    @classmethod
    def create_mock(cls, user_input: Dict[str, Any] = None, expected_db_data: Dict[str, Any] = None) -> Example:
        """
        Creates a new mocked Example and returns it using the user's input (what the user typed in when
        creating the instance, and the expected DB data (what the database is expected to return if the
        instance/record creation was successful)
        """
        _user_input = {**cls.user_input_template, **(user_input or {})}
        _expected_db_data = {**cls.expected_db_data_template, **(expected_db_data or {})}

        example_instance = Example(**_user_input)

        for attr_name, attr_value in _expected_db_data.items():
            setattr(example_instance, attr_name, attr_value)

        return example_instance

    #############################################################
    #                                                           #
    #               METHOD CALLS FIXTURES                       #
    #                                                           #
    #############################################################
    class get_by_id:
        class success:
            @staticmethod
            def output() -> Example:
                return ExampleFixture.create_mock()

        class none:
            @staticmethod
            def output() -> Optional[Example]:
                return None

    class get_all:
        class success:
            @staticmethod
            def output() -> List[Example]:
                return [ExampleFixture.create_mock() for _ in range(3)]

        class empty_list:
            @staticmethod
            def output() -> List[Example]:
                return []

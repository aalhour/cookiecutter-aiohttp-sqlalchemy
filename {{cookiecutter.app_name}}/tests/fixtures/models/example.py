from uuid import uuid4
from random import randint
from datetime import datetime
from typing import Dict, Any, List, Optional

from {{cookiecutter.app_name}}.models.example import Example


class ExampleFixture:
    user_input_template = {
        "name": f"test_example_{uuid4()}"
    }

    expected_db_data_template = {
        **user_input_template,
        "id": randint(1_000, 10_000),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    @classmethod
    async def create_mock(cls, user_input: Dict[str, Any] = None, expected_db_data: Dict[str, Any] = None) -> Example:
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
            async def output() -> Example:
                return await ExampleFixture.create_mock()

        class none:
            @staticmethod
            async def output() -> Optional[Example]:
                return None

    class get_all:
        class success:
            @staticmethod
            async def output() -> List[Example]:
                return [await ExampleFixture.create_mock()] * 3

        class empty_list:
            @staticmethod
            async def output() -> List[Example]:
                return []

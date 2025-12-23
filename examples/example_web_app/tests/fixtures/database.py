from unittest.mock import MagicMock


class TransactionalSessionFixture:
    def __init__(self, *args, target_mock: MagicMock = None, **kwargs):
        """

        :param args:
        :param target_mock MagicMock: Pass a mock here if you want to assert against it later
        :param kwargs:
        """
        if target_mock:
            self._session = target_mock
        else:
            self._session = MagicMock(name='transactional_session_mock')

    def __enter__(self, *args, **kwargs):
        return self._session

    def __exit__(self, exc_type, exc, tb):
        pass

    async def __aenter__(self, *args, **kwargs):
        return self._session

    async def __aexit__(self, exc_type, exc, tb, *args, **kwargs):
        pass

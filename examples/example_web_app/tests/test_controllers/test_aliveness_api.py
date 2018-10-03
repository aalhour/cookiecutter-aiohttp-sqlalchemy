"""
This module tests the /api/-/aliveness
"""

import json


class TestGet:
    async def test_healthy(self, client):
        ###
        # Act
        #
        response = await client.get("/api/-/aliveness")

        ###
        # Assert
        #
        assert response.status == 200

        response_dict = json.loads(await response.text())
        assert response_dict == {
            "message": "I'm alive and kicking!!!"
        }


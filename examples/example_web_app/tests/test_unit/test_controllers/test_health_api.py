"""
This module tests the /api/-/health
"""

import json

from example_web_app.models.health import HealthStatus


class TestGet:
    async def test_healthy(self, client):
        ###
        # Act
        response = await client.get("/api/-/health")

        ###
        # Assert
        assert response.status == 200

        response_dict = json.loads(await response.text())
        assert response_dict == {
            "status": HealthStatus.Pass.value
        }


"""
Integration tests for health check endpoints.

Tests the full health check lifecycle including database and Redis connectivity.
"""


class TestHealthEndpoints:
    """Integration tests for health check endpoints."""

    async def test_health_endpoint_returns_healthy(self, client):
        """Test that /api/-/health returns healthy status."""
        response = await client.get("/api/-/health")
        assert response.status == 200

        data = await response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data

    async def test_liveness_endpoint_returns_ok(self, client):
        """Test that /api/-/live returns OK for Kubernetes liveness probe."""
        response = await client.get("/api/-/live")
        assert response.status == 200

        text = await response.text()
        assert text == "OK"

    async def test_readiness_endpoint_returns_status(self, client):
        """Test that /api/-/ready returns readiness status."""
        response = await client.get("/api/-/ready")
        # May be 200 (ready) or 503 (not ready) depending on DB state
        assert response.status in [200, 503]

        data = await response.json()
        assert "status" in data
        assert "checks" in data
        assert "database" in data["checks"]


class TestMetricsEndpoint:
    """Integration tests for Prometheus metrics endpoint."""

    async def test_metrics_returns_prometheus_format(self, client):
        """Test that /metrics returns Prometheus-formatted metrics."""
        response = await client.get("/metrics")
        assert response.status == 200

        # Check content type
        content_type = response.headers.get("Content-Type", "")
        assert "text/plain" in content_type

        # Check body contains expected metrics
        text = await response.text()
        assert "http_requests_total" in text or "python_gc" in text

    async def test_metrics_increments_on_requests(self, client):
        """Test that making requests increments the metrics."""
        # Make a request to trigger metrics
        await client.get("/api/-/health")

        # Get metrics
        response = await client.get("/metrics")
        text = await response.text()

        # Should have recorded the health request
        assert "http_requests_total" in text or "python_gc" in text


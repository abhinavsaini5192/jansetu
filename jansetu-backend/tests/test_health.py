def test_root_health_endpoint(client):
    """Test GET /health returns expected status and service name."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "jansetu-backend"


def test_api_health_endpoint(client):
    """Test GET /api/v1/health returns expected status."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "jansetu-backend"


def test_system_status_endpoint(client):
    """Test GET /api/v1/system/status returns application details without exposing secrets."""
    response = client.get("/api/v1/system/status")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    sys_data = data["data"]
    assert "application" in sys_data
    assert "environment" in sys_data
    assert "api_version" in sys_data
    assert "database" in sys_data
    assert "status" in sys_data["database"]
    # Ensure sensitive settings are not exposed
    assert "jwt_secret_key" not in str(data).lower()
    assert "password" not in str(data).lower()


def test_global_404_error_envelope(client):
    """Test that requesting an invalid route returns standardized error envelope."""
    response = client.get("/api/v1/nonexistent-route-xyz")
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert "error" in data
    assert data["error"]["code"] == "RESOURCE_NOT_FOUND"


def test_cors_preflight(client):
    """Test CORS preflight headers for frontend origin."""
    response = client.options(
        "/api/v1/system/status",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"

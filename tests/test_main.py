from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


def test_access_token_route_no_auth(client):
    response = client.get("/protected-with-access-token")
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_id_token_route_no_auth(client):
    response = client.get("/protected-with-id-token")
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_access_token_route_malformed_auth(client):
    response = client.get(
        "/protected-with-access-token",
        headers={"Authorization": "NotBearer sometoken"},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED

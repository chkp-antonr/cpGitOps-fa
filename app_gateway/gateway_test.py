# import pytest
from fastapi.testclient import TestClient

from src.main import  app

client = TestClient(app)


def test_gw_index():
    response = client.get("/gateway")
    assert response.status_code == 200
    assert "Maestro" in response.text

def test_gw_details():
    response = client.get("/gateway/mdmPrime/cpGitOps/ctim")
    assert response.status_code == 200
    assert "ctim.il.cparch.in" in response.text

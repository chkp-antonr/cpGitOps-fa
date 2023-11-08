# import pytest
from fastapi.testclient import TestClient

from src.main import  app

client = TestClient(app)


def test_mgmt_index():
    response = client.get("/management")
    assert response.status_code == 200
    # assert "Maestro" in response.text


def test_mgmt_show_domains():
    response = client.get("/management/show_domains/")
    assert response.status_code == 200
    assert "Select server" in response.text

def test_mgmt_show_domains():
    response = client.get("/management/show_domains/")
    assert response.status_code == 200
    assert "Select server" in response.text

def test_mgmt_show_domains_update_ssot_dirs():
    response = client.get("/management/show_domains/?mgmt_server=mdmPrime&action=update_ssot_dirs")
    assert response.status_code == 200
    assert "Domains in SSoT" in response.text

def test_mgmt_show_domains_fetch_api(): # time consuming
    response = client.get("/management/show_domains/?mgmt_server=mdmPrime&action=fetch_api&domain=cpGitOps")
    assert response.status_code == 200
    # assert "Domains in SSoT" in response.text


import pytest
from include.cpf import Mgmt, show_domains #get_mgmt_server_login_info
from src import schemas as sch

mdm_name = "mdmPrime"
mdm_fqdn = "mdmPrime.il.cparch.in"
dmn = "cpGitOps"

# @pytest.fixture(scope="module")



def test_login_first():
    status, client = Mgmt().login(sch.ManagementToLogin(name=mdm_name))
    assert client is not None
    assert "Logged to" in status.comment

def test_login_cached():
    status, client = Mgmt().login(sch.ManagementToLogin(name=mdm_name))
    assert client is not None
    assert "Found cached login" in status.comment



def test_api_call_version():
    client = Mgmt().login(sch.ManagementToLogin(name=mdm_name))[1]
    res = client.api_call("show-api-versions")
    assert len(res.data['supported-versions']) > 0

def test_api_call_domains():
    client = Mgmt().login(sch.ManagementToLogin(name=mdm_fqdn, dmn="System Data"))[1]
    res = client.api_call("show-domains")
    assert res.data['total'] > 1


def test_show_domains():
    res = show_domains("mdmPrime")
    assert len(res) > 1

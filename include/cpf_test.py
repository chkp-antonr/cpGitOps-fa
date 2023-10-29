import pytest
from include.cpf import Mgmt, get_mgmt_server_login_info
from src import schemas as sch

mdm_name = "mdmPrime"
dmn = "cpGitOps"

# Use this mgmt object
# @pytest.fixture(scope="module")
def mgmt() -> Mgmt:
    mgmt_server_info = get_mgmt_server_login_info('mdmPrime.il.cparch.in')
    return Mgmt(mgmt_server_info)


def test_get_mgmt_login_info():
    mgmt_server_info = get_mgmt_server_login_info('mdmPrime.il.cparch.in')
    assert mgmt_server_info.port == 443
    assert mgmt_server_info.name == "mdmPrime"


def test_Mgmt_singletone():
    mgmt_server_info = get_mgmt_server_login_info('mdmPrime.il.cparch.in')
    m1 = Mgmt(mgmt_server_info)
    m2 = Mgmt(mgmt_server_info)
    assert id(m1) == id(m2)


def test_login_first():
    status, client = mgmt().login(sch.ManagementToLogin(name=mdm_name, dmn=dmn))
    assert client is not None
    assert "Logged to" in status.comment

def test_login_cached():
    status, client = mgmt().login(sch.ManagementToLogin(name=mdm_name, dmn=dmn))
    assert client is not None
    assert "Found cached login" in status.comment


def test_api_call_version():
    client = mgmt().login(sch.ManagementToLogin(name=mdm_name))[1]
    res = client.api_call("show-api-versions")
    assert len(res.data['supported-versions']) > 0

def test_api_call_domains():
    client = mgmt().login(sch.ManagementToLogin(name=mdm_name, dmn="System Data"))[1]
    res = client.api_call("show-domains")
    assert res.data['total'] > 1

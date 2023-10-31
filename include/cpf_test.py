import pytest
from include.cpf import Mgmt, show_domains #get_mgmt_server_login_info
from src import schemas as sch

mdm_name = "mdmPrime"
mdm_fqdn = "mdmPrime.il.cparch.in"
dmn = "cpGitOps"
# domains = ['cpGitOps']
# domains = ['cpGitOps', 'General', 'System Data']

# @pytest.fixture(scope="module")

@pytest.fixture(params=['cpGitOps'])
# @pytest.fixture(params=['cpGitOps', 'General', 'System Data'])
def fixt_dmn(request):
    return request.param

# -m login to run only marked
@pytest.mark.login
def test_login_first(fixt_dmn):
    status, client = Mgmt().login(sch.ManagementToLogin(name=mdm_fqdn, dmn=fixt_dmn))
    assert client is not None
    assert "Logged to" in status.comment

@pytest.mark.login
def test_login_cached(fixt_dmn):
    status, client = Mgmt().login(sch.ManagementToLogin(name=mdm_name, dmn=fixt_dmn))
    assert client is not None
    assert "Found cached login" in status.comment

@pytest.mark.login
def test_login_cached_again(fixt_dmn):
    status, client = Mgmt().login(sch.ManagementToLogin(name=mdm_name, dmn=fixt_dmn))
    assert client is not None
    assert "Found cached login" in status.comment

def test_api_call_version():
    client = Mgmt().login(sch.ManagementToLogin(name=mdm_name))[1]
    res = client.api_call("show-api-versions")
    assert len(res.data['supported-versions']) > 0, "Received data=" + str(res.data)

def test_api_call_domains():
    client = Mgmt().login(sch.ManagementToLogin(name=mdm_fqdn, dmn="System Data"))[1]
    res = client.api_call("show-domains")
    assert res.data['total'] > 1


def test_show_domains():
    res = show_domains("mdmPrime")
    assert len(res) > 1

@pytest.mark.test
def test_fetch_packages_dmn():
    res = Mgmt().fetch_packages_dmn(mdm_name, dmn)
    assert res is None

# pytest .\include\cpf_test.py -v -s -m test

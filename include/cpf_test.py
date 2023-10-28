from include.cpf import Mgmt, get_mgmt_login_info

def test_get_mgmt_login_info():
    mgmt_login_info = get_mgmt_login_info('mdmPrime.il.cparch.in')
    assert mgmt_login_info.port == 443
    assert mgmt_login_info.name == "mdmPrime"


def test_Mgmt_singletone():
    mgmt_login_info = get_mgmt_login_info('mdmPrime.il.cparch.in')
    m1 = Mgmt(mgmt_login_info)
    m2 = Mgmt(mgmt_login_info)
    assert id(m1) == id(m2)


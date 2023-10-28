import pytest
from include.cpg import gateway_descr_by_fqdn, gateway_by_name

def test_gateway_descr_by_fqdn_missed():
    assert gateway_descr_by_fqdn("xxx.in") == None

def test_gateway_descr_by_fqdn_real():
    assert gateway_descr_by_fqdn("ctim.il.cparch.in").annotation.name == "ctim"


def test_gateway_by_name_fake():
    assert gateway_by_name("xxx", "cpGitOps", "ctim") == None
    assert gateway_by_name("mdmPrime", "xxx", "ctim") == None
    assert gateway_by_name("mdmPrime", "cpGitOps", "xxx") == None
    assert gateway_by_name("x", "x", "x") == None
    assert gateway_by_name("", "", "") == None

def test_gateway_by_name():
    assert gateway_by_name("mdmPrime", "cpGitOps", "ctim").fqdn == "ctim.il.cparch.in"
    assert gateway_by_name("mdmPrime", "cpGitOps", "ctim").descr_file.annotation.ipv4_address == "172.23.23.29"


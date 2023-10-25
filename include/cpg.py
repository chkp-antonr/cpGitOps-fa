""" GitOps-related module """

import os
from typing import Dict, List
import yaml
from fastapi import APIRouter, Request


import src.schemas as sch
# from include import cgl
from include.cgl import logger, settings

router = APIRouter(
    prefix="/cpg",
    tags=["CPG"]
)


#region Gateways
def gateway_descr_by_fqdn(gw_fqdn) -> Dict:
    """ Returns _descr_.yaml form gw_fqdn """

    descr = {}
    dir_gw = settings.DIR_SSOT + "/" + settings.DIR_GW
    try:
        f_descr = os.path.join(dir_gw, gw_fqdn) + "/" + settings.FN_DESCR
        with open(f_descr, "r") as yaml_file:
            descr.update(yaml.safe_load(yaml_file))
    except FileNotFoundError:
        print(f"{f_descr} not found")
    return descr # gateway_descr_by_fqdn


def list_gateways() -> List[Dict]:
    gw_descr_list = []

    dir_gw = settings.DIR_SSOT + "/" + settings.DIR_GW
    for path in os.listdir(dir_gw):
        if os.path.isdir(os.path.join(dir_gw, path)) and path != "Global":
            descr = {"fqdn":path}
            descr.update(gateway_descr_by_fqdn(path)['annotation'])
            gw_descr_list.append(descr)
    return gw_descr_list # list_gateways

#endregion Gateways

#region Management

@router.get("/mgmt_descr_by_fqdn/{mgmt_fqdn}")
def mgmt_descr_by_fqdn(mgmt_fqdn:str) -> sch.DescrManagement:
    """ Returns _descr_.yaml form mgmt_fqdn """

    descr = {}
    dir_gw = settings.DIR_SSOT + "/" + settings.DIR_MGMT
    try:
        f_descr = os.path.join(dir_gw, mgmt_fqdn) + "/" + settings.FN_DESCR
        with open(f_descr, "r") as yaml_file:
            descr.update(yaml.safe_load(yaml_file))
    except FileNotFoundError:
        print(f"{f_descr} not found")
    return descr # mgmt_descr_by_fqdn


@router.get("/list_mgmt_domains")
def list_mgmt_domains() -> List[Dict]:
    """ Return List of management servers
    [{"mdmPrime.il.cparch.in": {"__descr__": <__descr__.yaml>, dmns:[cpGitOps,<without Global>]},]
    dmns = {} for SmartCenter
    """

    mgmt_domains_list = []
    dir_mgmt = settings.DIR_SSOT + "/" + settings.DIR_MGMT
    for mdm_fqdn in os.listdir(dir_mgmt):
        mdm_path = os.path.join(dir_mgmt, mdm_fqdn)
        dmns = []
        for dmn in os.listdir(mdm_path):
            if os.path.isdir(os.path.join(mdm_path, dmn)) and dmn != "Global":
                dmns.append(dmn)
        descr = mgmt_descr_by_fqdn(mdm_fqdn)['annotation']
        mgmt_domain = {mdm_fqdn:
            {
                "__descr__": descr,
                "dmns": dmns,
            }
        }
        mgmt_domains_list.append(mgmt_domain)
        # logger.debug(mgmt_domains_list)
    return mgmt_domains_list # list_mgmt_domains

#endregion Management

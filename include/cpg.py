""" GitOps-related module """

import os
from typing import List
import yaml
from fastapi import APIRouter


import src.schemas as sch
# from include import cgl
from include.cgl import settings, logger

#region
router = APIRouter(
    prefix="/cpg",
    tags=["CPG"]
)

class MyDumper(yaml.Dumper):
    ''' Adds ident before "-"
        yaml.dump(self.hosts_curr, Dumper=cpg.MyDumper,
                  sort_keys=False, indent=2, default_flow_style=False)
    '''
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)
        # return super(MyDumper, self).increase_indent(flow, False)

#endregion


#region Gateways
@router.get("/gateway_descr_by_fqdn/{mgmt_fqdn}",
            description="Returns _descr_.yaml for gw_fqdn")
def gateway_descr_by_fqdn(gw_fqdn) -> sch.DescrGateway:
    """ Returns _descr_.yaml for gw_fqdn """

    dir_gw = settings.DIR_SSOT + "/" + settings.DIR_GW
    try:
        f_descr = os.path.join(dir_gw, gw_fqdn) + "/" + settings.FN_DESCR
        with open(f_descr, "r") as yaml_file:
            descr = yaml.safe_load(yaml_file)
    except FileNotFoundError:
        print(f"{f_descr} not found")
        return None
    # t = sch.DescrGateway(descr)
    return sch.DescrGateway(**descr) # gateway_descr_by_fqdn


@router.get("/gateway_by_name/{mgmt_server}/{dmn}/{name}",
            description="Returns _descr_.yaml for gw by name")
def gateway_by_name(mgmt_name, dmn, name) -> sch.GatewaySingle:
    """ Returns fqdn + _descr_.yaml for gw by its name """

    # for item in list_gateways():
    #     gw = item.model_dump()
    #     if gw['descr_file']['annotation']['mdm'] == mgmt_server \
    #         and gw['descr_file']['annotation']['dmn'] == dmn \
    #         and gw['descr_file']['annotation']['name'] == name:
    #         logger.debug(item)
    #         return item
    gw = next((gw for gw in list_gateways() \
              if gw.descr_file.annotation.mgmt_name == mgmt_name
            and gw.descr_file.annotation.dmn == dmn
            and gw.descr_file.annotation.name == name), None
            )
    # gw = next((gw for gw in [item.model_dump() for item in list_gateways()] \
    #           if gw['descr_file']['annotation']['mgmt_name'] == mgmt_name
    #         and gw['descr_file']['annotation']['dmn'] == dmn
    #         and gw['descr_file']['annotation']['name'] == name), None
    #         )
    # logger.debug(gw)
    return gw # gateway_descr_by_fqdn


@router.get("/list_gateways",
            description="List all gateways")
def list_gateways() -> sch.ListOfGatewaySingle:
    gw_descr_list = []

    dir_gw = settings.DIR_SSOT + "/" + settings.DIR_GW
    for path in os.listdir(dir_gw):
        if os.path.isdir(os.path.join(dir_gw, path)) and path != "Global":
            gw = sch.GatewaySingle(
                fqdn=path, descr_file=gateway_descr_by_fqdn(path))
            gw_descr_list.append(gw)
            # logger.debug(gw)
    return gw_descr_list # list_gateways

#endregion Gateways


#region Management
@router.get("/mgmt_descr_by_fqdn/{mgmt_fqdn}",
            description="Returns _descr_.yaml for by fqdn or name")
def mgmt_descr_by_fqdn(mgmt_fqdn) -> sch.DescrManagement:
    """ Returns _descr_.yaml by fqdn or name """

    dir_gw = settings.DIR_SSOT + "/" + settings.DIR_MGMT
    try:
        f_descr = os.path.join(dir_gw, mgmt_fqdn) + "/" + settings.FN_DESCR
        with open(f_descr, "r") as yaml_file:
            descr = yaml.safe_load(yaml_file)
    except FileNotFoundError:
        print(f"{f_descr} not found")
        return None
    return sch.DescrManagement(**descr) # mgmt_descr_by_fqdn


@router.get("/list_mgmt_domains",
            description="List all management servers")
def list_mgmt_domains() -> sch.ListOfManagementServerSingle:
    """ Return List of management servers
    [{"fqdn": "mdmPrime.il.cparch.in", "__descr__": <__descr__.yaml>,
        dmns:[cpGitOps,<without Global>]},]
    dmns = [] for SmartCenter
    """

    mgmt_domains_list = []
    dir_mgmt = settings.DIR_SSOT + "/" + settings.DIR_MGMT
    for mdm_fqdn in os.listdir(dir_mgmt):
        mdm_path = os.path.join(dir_mgmt, mdm_fqdn)
        dmns = []
        for dmn in os.listdir(mdm_path):
            if os.path.isdir(os.path.join(mdm_path, dmn)) and dmn != "Global":
                dmns.append(dmn)
        descr_file = mgmt_descr_by_fqdn(mdm_fqdn)
        mgmt_domain = sch.ManagementServerSingle(
            fqdn=mdm_fqdn, descr_file=descr_file, dmns=dmns)
        # logger.debug(mgmt_domain.model_dump(by_alias=True))
        mgmt_domains_list.append(mgmt_domain)
        # logger.debug(f"\n{yaml.dump(mgmt_domains_list, indent=4, Dumper=MyDumper)}")
    return mgmt_domains_list # list_mgmt_domains

@router.get("/mgmt_descr_by_fqdn/{mgmt_fqdn}",
            description="Returns _descr_.yaml for by fqdn or name")
def mgmt_get_fqdn_by_name(mgmt_name) -> str:
    """ Returns fqdn by management server name """

    dir_mgmt = settings.DIR_SSOT + "/" + settings.DIR_MGMT
    for mdm_fqdn in os.listdir(dir_mgmt):
        descr_file = mgmt_descr_by_fqdn(mdm_fqdn)
        if descr_file.annotation.name == mgmt_name:
            return mdm_fqdn
    return None # mgmt_descr_by_fqdn

#endregion Management

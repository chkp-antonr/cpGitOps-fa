""" Check Point related functions """

import os
from typing import Dict, List, Tuple
import yaml
import json
from fastapi import APIRouter
#
from cpapi import APIClient, APIClientArgs, APIResponse
from include.cgl import logger
from include.cpg import settings, mgmt_descr_by_fqdn, mgmt_get_fqdn, MyDumper
from src.schemas import ManagementToLogin, ManagementServerCachedInfo, \
    ListOfManagementServerCachedInfo, ManagementToLogin, ApiStatus

# region GlobalsAndSettings
DEFAULT_COLOR = "Crete Blue"  # for new objects if not specified
# [aquamarine, black, blue, crete blue, burlywood, cyan, dark green,
# khaki, orchid, dark orange, dark sea green, pink, turquoise, dark blue,
# firebrick, brown, forest green, gold, dark gold, gray, dark gray,
# light green, lemon chiffon, coral, sea green, sky blue, magenta, purple,
# slate blue, violet red, navy blue, olive, orange, red, sienna, yellow]
DEFAULT_TAGS = "auto"
HTTP_DEBUG_LEVEL = 0
#endregion GlobalsAndSettings

#region Functions
def strip_res_obj(response: APIResponse, indent=4) -> str:
    var_json = json.loads(str(response)[12:-1])
    try:
        del var_json['res_obj']
    except:
        pass
    return json.dumps(var_json, indent=indent) # strip_res_obj

#endregion Functions


class Mgmt():
    """ Management server with caching - singleton """
    instance = None
    mgmt_servers:ListOfManagementServerCachedInfo = []

    def __new__(cls):
        if cls.instance is None:
            # Called only once
            # logger.error("Call once")
            cls.instance = super().__new__(cls)
        return cls.instance  # return existing instance

    def login(self, server_to_login:ManagementToLogin=None,
              unsafe_auto_accept=True, force_login=False) -> Tuple[ApiStatus, APIClient]:
        """ Login to SMS or DMN if not logged

        :param Dict server_to_login: _description_
        :param bool unsafe_auto_accept: ignore fingerprint check, defaults to True
        :param force_login: re-login if if cached found (maybe expired...)
        :return _type_: success code
        """

        # Check in cache
        if server_to_login.fqdn:
            cached_login = next((login for login in self.mgmt_servers
                          if login.fqdn == server_to_login.fqdn
                            and login.dmn == server_to_login.dmn), None)
        elif server_to_login.name:
            cached_login = next((login for login in self.mgmt_servers
                          if login.name == server_to_login.name
                            and login.dmn == server_to_login.dmn), None)
        if cached_login is not None \
            and cached_login.client is not None:
            logger.info(f"Found cached login for "
                         f"{server_to_login.fqdn} {server_to_login.name}")
            result = ApiStatus(success=True, status_code=201,
                comment=f"Found cached login for "
                        f"{server_to_login.dmn}@{cached_login.name}")
            return (result, cached_login.client)

        # There might be not cached login for the domain,
        # but already cached credentials for MDM

        if server_to_login.fqdn:
            matched_server = next((server for server in self.mgmt_servers
                          if server.fqdn == server_to_login.fqdn), None)
        elif server_to_login.name:
            matched_server = next((server for server in self.mgmt_servers
                          if server.name == server_to_login.name), None)

        if matched_server is not None:
            client_args = APIClientArgs(server=matched_server.server_ip,
                unsafe_auto_accept=unsafe_auto_accept, http_debug_level=HTTP_DEBUG_LEVEL)
            client = APIClient(client_args)
        else:
            logger.warning(f"No cached data for login to "
                f"{server_to_login.fqdn} {server_to_login.name}")
            # return ApiStatus(success=False, error_message= \
            #                  f"No cached data for login to "
            #                  f"{server_to_login.fqdn} {server_to_login.name}")
            if server_to_login.fqdn:
                mgmt_server_info = self.get_mgmt_server_login_info(server_to_login.fqdn)
            else:
                mgmt_server_info = self.get_mgmt_server_login_info(server_to_login.name)

            # Preliminary prep and check (for New server only)
            client_args = APIClientArgs(server=mgmt_server_info.server_ip,
                unsafe_auto_accept=unsafe_auto_accept, http_debug_level=HTTP_DEBUG_LEVEL)
            client = APIClient(client_args)
            if client.check_fingerprint() is False:
                logger.critical(
                        f"{mgmt_server_info.name}: Could not get the server's fingerprint -"
                        f"Check connectivity with the server.")
                return ApiStatus(success=False,
                        error_message=f"{mgmt_server_info.name}: Could not get the server's fingerprint",
                        comment="Check connectivity with the server.")

            # Cache credentials (without client yet) if connection is OK
            self.mgmt_servers.append(mgmt_server_info)
            matched_server = next((server for server in self.mgmt_servers
                          if server.fqdn == mgmt_server_info.fqdn), None)


        # New login
        dmn = None
        if server_to_login.dmn:
            dmn = server_to_login.dmn
        if matched_server.api_key:
            res = client.login_with_api_key(matched_server.api_key.get_secret_value(), domain = dmn)
        else:
            res = client.login(username=matched_server.username,
                               password=matched_server.password.get_secret_value(),
                               domain = dmn)
        if res.success:
            logger.info(f"Logged to {server_to_login.dmn}@{matched_server.name} as {res.data['user-name']}")
            result = ApiStatus(success=True, status_code=201,
                comment=f"Logged to {server_to_login.dmn}@{matched_server.name} as {res.data['user-name']}")
            matched_server.client = client
        else:
            logger.error(f"Login to {server_to_login.dmn}@{matched_server.name} failed."
                         f"{res.status_code}: '{res.error_message}'")
            result = ApiStatus(error_message=f"{res.status_code}: '{res.error_message}'",
                               comment=f"Login to {server_to_login.dmn}@{matched_server.name} failed.")
            client = None
        # logger.debug(f"\n{yaml.dump(res, indent=4, Dumper=MyDumper)}")
        return (result, client) # login

    def get_mgmt_server_login_info(self, fqdn_name: str) -> ManagementServerCachedInfo:
        """ Get login info by fqdn or name.
        Expect universal login to MDM (not to each DMN)
        """

        mgmt_descr = mgmt_descr_by_fqdn(mgmt_get_fqdn(fqdn_name))

        # logger.debug(mgmt_descr)

        mgmt_server_login_info = ManagementServerCachedInfo(
            fqdn=fqdn_name,
            name=mgmt_descr.annotation.name,
            server_ip=mgmt_descr.annotation.ipv4_address,
            # port: int = 443
            # ToDo replace with credentials from pluginenvenv
            api_key="attNU1d69sTjjZo3qRIIkg==",
            username="_api_",
            # password: str = ""
            kind = mgmt_descr.annotation.kind
        )
        logger.debug(mgmt_server_login_info)
        return mgmt_server_login_info # get_mgmt_login_info


def show_domains(mdm_fqdn_name: str) -> List[str]:
    client = Mgmt().login( \
            ManagementToLogin(fqdn=mgmt_get_fqdn(mdm_fqdn_name), dmn="System Data"))[1]
    res = client.api_call("show-domains", {
            "limit" : 250,
            "offset" : 0,
            "details-level" : "standard"})
    domains = [(domain['name'], domain) for domain in res.data['objects']]
    logger.debug(domains)
    return domains # show_domains

#region cpf
router = APIRouter(
    prefix="/cpf",
    tags=["CPF"]
)

@router.get("/update_ssot_mgmt_domains/{mdm_server}",
            description="Returns _descr_.yaml for by fqdn or name")
def update_ssot_mgmt_domains(mdm_server:str) -> Dict[str, List[str]]:
    domain_names = [domain[0] for domain in show_domains(mdm_server)]
    domain_names.append("Global")

    mdm_fqdn = mgmt_get_fqdn(mdm_server)
    mdm_path = f"{settings.DIR_SSOT}/{settings.DIR_MGMT}/{mdm_fqdn}"
    dirs_created = []
    dirs_not_created = []
    for dmn in domain_names:
        dmn_path = os.path.join(mdm_path, dmn)
        if not os.path.isdir(dmn_path):
            try:
                logger.warning(f"Creating {dmn_path}")
                os.mkdir(dmn_path)
                dirs_created.append(dmn_path)
            except FileExistsError:
                logger.error(f"Can't create {dmn_path}. FileExists?")
                dirs_not_created.append(dmn_path)

        for dir in [settings.MGMT_DIR_DECL, settings.MGMT_DIR_LAST, settings.MGMT_DIR_TEMP]:
            mgmt_dir = os.path.join(dmn_path, dir)
            if not os.path.isdir(mgmt_dir):
                try:
                    logger.info(f"Creating {mgmt_dir}")
                    os.mkdir(mgmt_dir)
                    dirs_created.append(mgmt_dir)
                except FileExistsError:
                    logger.error(f"Can't create {mgmt_dir}. FileExists?")
                    dirs_not_created.append(mgmt_dir)
    result = {
        "dirs_created": dirs_created,
        "dirs_not_created": dirs_not_created,
    }
    return result # update_ssot
#endregion cpf
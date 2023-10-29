""" Check Point related functions """

from typing import Dict, List, Tuple
import yaml
import json
#
from cpapi import APIClient, APIClientArgs, APIResponse
from .cgl import logger
from .cpg import mgmt_descr_by_fqdn, MyDumper
from src.schemas import ManagementToLogin, ManagementServerCachedInfo, \
    ListOfManagementServerCachedInfo, ListOfManagementLoginInfo, ApiStatus

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
def get_mgmt_server_login_info(fqdn: str) -> ManagementServerCachedInfo:
    """ Get login info by fqdn.
    Expect universal login to MDM (not to each DMN)
    """

    mgmt_descr = mgmt_descr_by_fqdn(fqdn)
    # logger.debug(mgmt_descr)

    mgmt_server_login_info = ManagementServerCachedInfo(
        fqdn=fqdn,
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
    cached_logins:ListOfManagementLoginInfo = []

    def __new__(cls, mgmt_server_info:ManagementServerCachedInfo=None):
        if cls.instance is None:
            # Called only once
            # logger.error("Call once")
            cls.instance = super().__new__(cls)
        return cls.instance  # return existing instance

    def __init__(self, mgmt_server_info:ManagementServerCachedInfo=None):
        if mgmt_server_info is not None:
            match = next((server for server in self.mgmt_servers
                        if server.fqdn == mgmt_server_info.fqdn), None)
            if not match:
                logger.debug(f'Adding {mgmt_server_info}')
                self.mgmt_servers.append(mgmt_server_info)
            else:
                logger.debug(match.model_dump())
        return # __init__

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
            cached_login = next((login for login in self.cached_logins
                          if login.fqdn == server_to_login.fqdn
                            and login.dmn == server_to_login.dmn), None)
        elif server_to_login.name:
            cached_login = next((login for login in self.cached_logins
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

        # Login Not cached? Check if server defined
        if server_to_login.fqdn:
            match = next((server for server in self.mgmt_servers
                          if server.fqdn == server_to_login.fqdn), None)
        elif server_to_login.name:
            match = next((server for server in self.mgmt_servers
                          if server.name == server_to_login.name), None)
        else:
            logger.error(f"No cached data for login to "
                f"{server_to_login.fqdn} {server_to_login.name}")
            return ApiStatus(success=False, error_message= \
                             f"No cached data for login to "
                             f"{server_to_login.fqdn} {server_to_login.name}")

        # Preliminary prep and check
        client_args = APIClientArgs(server=match.server_ip,
            unsafe_auto_accept=unsafe_auto_accept, http_debug_level=HTTP_DEBUG_LEVEL)
        client = APIClient(client_args)
        if client.check_fingerprint() is False:
            logger.critical(
                "Could not get the server's fingerprint - Check connectivity with the server.")
            return ApiStatus(success=False,
                        error_message="Could not get the server's fingerprint",
                        comment="Check connectivity with the server.")

        # New login
        dmn = None
        if server_to_login.dmn:
            dmn = server_to_login.dmn
        if match.api_key:
            res = client.login_with_api_key(match.api_key.get_secret_value(), domain = dmn)
        else:
            res = client.login(username=match.username, password=match.password.get_secret_value(),
                                domain = dmn)
        if res.success:
            logger.info(f"Logged to {server_to_login.dmn}@{match.name} as {res.data['user-name']}")
            result = ApiStatus(success=True, status_code=201,
                comment=f"Logged to {server_to_login.dmn}@{match.name} as {res.data['user-name']}")
            server_to_login.client = client
            self.cached_logins.append(server_to_login)
        else:
            logger.error(f"Login to {server_to_login.dmn}@{match.name} failed."
                         f"{res.status_code}: '{res.error_message}'")
            result = ApiStatus(error_message=f"{res.status_code}: '{res.error_message}'",
                               comment=f"Login to {server_to_login.dmn}@{match.name} failed.")
            client = None
        # logger.debug(f"\n{yaml.dump(res, indent=4, Dumper=MyDumper)}")
        return (result, client) # login


    def api_call(self, mgmt:ManagementToLogin, command:str,
                 params={}, dmn="") -> APIResponse:
        """ by mdm_name, if not found try as fqdn """
        # mgmt_server = next((server for server in self.mgmt_servers
        #               if server.name == mgmt), None)
        # if not mgmt_server:
        #     mgmt_server = next((server for server in self.mgmt_servers
        #                 if server.fqdn == mgmt), None)
        # if not mgmt_server:
        #     logger.critical(f"Mgmt class not initialized for {mgmt}")
        #     return {"status_code": 401, "mgmt":mgmt}

        status, client = self.login(mgmt)
        res = client.api_call(mgmt, command, params, dmn)
        res = {"status_code": 200, "mdm_name":mgmt}
        return res # api_cli

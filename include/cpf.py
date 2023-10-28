""" Check Point related functions """

from typing import Dict, List
import yaml
#
from cpapi import APIClient, APIClientArgs, APIResponse
from .cgl import logger
from .cpg import mgmt_descr_by_fqdn, MyDumper
from src.schemas import ManagementLoginInfo, ApiStatus

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
def get_mgmt_login_info(fqdn: str) -> ManagementLoginInfo:
    """ Get login info by fqdn.
    Expect universal login to MDM (not to each DMN)
    """

    mgmt_descr = mgmt_descr_by_fqdn(fqdn)
    # logger.debug(mgmt_descr)

    mgmt_login_info = ManagementLoginInfo(
        fqdn=fqdn,
        name=mgmt_descr['annotation']['name'],
        # name=mgmt_descr.annotation.name,
        server=mgmt_descr['annotation']['ipv4_address'],
        # port: int = 443
        # ToDo replace with credentials from pluginenvenv
        api_key="attNU1d69sTjjZo3qRIIkg==",
        username="_api_",
        # password: str = ""
    )
    logger.debug(mgmt_login_info)
    return mgmt_login_info # get_mgmt_login_info
#endregion Functions

class Mgmt():
    """ Management server with caching - sngleton """
    instance = None
    mgmt_servers = []

    def __new__(cls, mgmt_login_info:ManagementLoginInfo):
        if cls.instance is None:
            # Called only once
            # logger.error("Call once")
            cls.instance = super().__new__(cls)
        return cls.instance  # return existing instance

    def __init__(self, mgmt_login_info:ManagementLoginInfo):
        match = next((server for server in self.mgmt_servers
                      if server['fqdn'] == mgmt_login_info.fqdn), None)
        if not match:
            logger.debug(f'Adding {mgmt_login_info}')
            self.mgmt_servers.append({
                "fqdn": mgmt_login_info.fqdn,
                "name": mgmt_login_info.name,
                # name=mgmt_descr.annotation.name,
                "server": mgmt_login_info.server,
                # port: int = 443
                # ToDo replace with credentials from pluginenvenv
                "api_key": "attNU1d69sTjjZo3qRIIkg==",
                "username": "_api_",
                # password: str = ""
            })
        # logger.error(self.mgmt_servers)
        return # return existing instance

    def login(self, mgmt_server:{}, unsafe_auto_accept=True) -> ApiStatus:
        """ Login to SMS or DMN if not logged

        :param Dict mgmt_server: _description_
        :param bool unsafe_auto_accept: ignore fingerprint check, defaults to True
        :return _type_: success code
        """
        client_args = APIClientArgs(
            server=mgmt_server['server'], unsafe_auto_accept=unsafe_auto_accept, http_debug_level=HTTP_DEBUG_LEVEL)

        client = APIClient(client_args)
        if client.check_fingerprint() is False:
            logger.critical(
                "Could not get the server's fingerprint - Check connectivity with the server.")
            return ApiStatus(False,
                        "Could not get the server's fingerprint",
                        "nCheck connectivity with the server.")

        res = client.api_call("show-api-versions")
        logger.debug(res)

        res = client.api_call("show-api-versions")
        logger.debug(res)
        # logger.debug(f"\n{yaml.dump(res, indent=4, Dumper=MyDumper)}")
        return ApiStatus(comment=f"Mgmt: {mgmt_server['name']}") # login


    def api_cli(self, mgmt:str, command:str, params = {}, dmn=""):
        """ by mdm_name, if not found try as fqdn """
        mgmt_server = next((server for server in self.mgmt_servers
                      if server['name'] == mgmt), None)
        if not mgmt_server:
            mgmt_server = next((server for server in self.mgmt_servers
                        if server['fqdn'] == mgmt), None)
        if not mgmt_server:
            logger.critical(f"Mgmt class not initialized for {mgmt}")
            return {"status_code": 401, "mgmt":mgmt}

        res = self.login(mgmt_server)
        res = {"status_code": 200, "mdm_name":mgmt}
        return res # api_cli

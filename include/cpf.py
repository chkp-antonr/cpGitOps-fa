""" Check Point related functions """

import os
from typing import Dict, List, Tuple, Text
import yaml
import json
from time import sleep
from fastapi import APIRouter
#
from cpapi import APIClient, APIClientArgs, APIResponse
from include.cgl import logger
from include.cpg import settings, mgmt_descr_by_fqdn, mgmt_get_fqdn, MyDumper
from src.schemas import ManagementToLogin, ManagementServerCachedInfo, \
    ListOfManagementServerCachedInfo, ManagementToLogin, ApiStatus, ApiCallRequest

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
            # Check if login still valid
            response = cached_login.client.api_call("show-api-versions")
            if not response.success: # expired
                cached_login.client = None # invalidate client
                return self.login(server_to_login) # call again and return
            logger.info(f"Found cached login for "
                         f"{cached_login.dmn}@{cached_login.name} {cached_login.name}")
            result = ApiStatus(success=True, status_code=201,
                comment=f"Found cached login for "
                        f"{cached_login.dmn}@{cached_login.name} {cached_login.name}")
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
            mgmt_server_info = matched_server.copy()
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
        mgmt_server_info.dmn = server_to_login.dmn

        # Cache credentials (without client yet) if connection is OK
        self.mgmt_servers.append(mgmt_server_info)
        matched_server = next((server for server in self.mgmt_servers
                        if server.fqdn == mgmt_server_info.fqdn
                          and server.dmn == server_to_login.dmn), None)

        # New login
        dmn = ""
        if server_to_login.dmn:
            dmn = server_to_login.dmn

        for count in range(0,9):
            if matched_server.api_key:
                res = client.login_with_api_key(matched_server.api_key.get_secret_value(), domain = dmn)
            else:
                res = client.login(username=matched_server.username,
                                password=matched_server.password.get_secret_value(),
                                domain = dmn)
            if not res.success \
                and "err_too_many_requests" in res.error_message:
                logger.debug(f"Login: err_too_many_requests. Try {count}")
                sleep(5)
            else:
                break

        if res.success:
            logger.info(f"Logged to {server_to_login.dmn}@{matched_server.name} as {res.data['user-name']}")
            result = ApiStatus(success=True, status_code=201,
                comment=f"Logged to {server_to_login.dmn}@{matched_server.name} as {res.data['user-name']}")
            matched_server.client = client
            matched_server.username = res.data['user-name']
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

    def enum_mgmt_api_calls_for_ver(self, api_version:Text="1.8",
                                    include_show_objects=False) -> List[Text]:
        """
        :return: list of dictionary containing following solo request components for checkpoint management server
            - resource: e.g. 'show-packages'
        """
        query = {
            "1.8": [
                # Network Objects
                "show-hosts",
                "show-networks",
                "show-groups",
                "show-security-zones",
                # Service & Applications
                "show-services-tcp",
                "show-services-udp",
                "show-services-icmp",
                "show-services-sctp",
                "show-services-other",
                "show-service-groups",
                "show-services-dce-rpc",
                "show-services-rpc",
                "show-services-gtp",
                "show-services-citrix-tcp",
                "show-services-compound-tcp",
                # Misc
                "show-gateways-and-servers",
                # "show-objects", # ToDo too much
                "show-wildcards",
            ]
        }
        result = query[api_version]
        if include_show_objects: # very big
            result.append("show-objects")
        return result  # enum_mgmt_api_calls_for_ver

    def fetch_packages_dmn(self, mdm_server:Text, dmn:Text=""):
        fqdn = mgmt_get_fqdn(mdm_server)
        client = Mgmt().login( \
                ManagementToLogin(fqdn=fqdn, dmn=dmn))[1]
        if not client:
            raise Exception(f"fetch_api_dmn: Login failed for {mdm_server}/{dmn}")

        response = client.api_query("show-packages", details_level="full")
        packages_list = [package for package in response.data['packages']]

        for package in packages_list:
            logger.info(f"Retrieving details for package {package['name']} in {dmn}@{fqdn}")
            pkg_name = package['name']
            pkg_uid = package['uid']
            pkg_details = client.api_call("show-package", {
                                "name": pkg_name,
                                "details-level": "full"
                            },)

            package_dir = \
                f"{settings.DIR_SSOT}/{settings.DIR_MGMT}/" \
                f"{fqdn}/{dmn}/{settings.MGMT_DIR_TEMP}/{pkg_name}"

            try:
                file_name = f"{package_dir}/show-package.json"
                if not os.path.isdir(package_dir):
                    logger.warning(f"Creating {package_dir}")
                    os.mkdir(package_dir)
                with open(file_name, "w") as json_file:
                    json_file.write(strip_res_obj(pkg_details))
            except Exception as e:
                logger.error(f"Can't write {file_name}: {e}")

            access_layers = []  # output of `show-access-rulebase`
            acc_layers_in_pkg = pkg_details.data.get("access-layers", [])
            for acc_layer in acc_layers_in_pkg:
                acc_layer_name = acc_layer['name']
                logger.debug(f"Retrieving details for access-rulebase {acc_layer_name} in {pkg_name}")
                access_rulebase = client.api_call("show-access-rulebase", {
                        "name": acc_layer_name,
                        "details-level": "full",
                        "use-object-dictionary": True},)
                access_layers.append(json.loads(strip_res_obj(access_rulebase)))
            try:
                file_name = f"{package_dir}/show-access-rulebase.json"
                with open(file_name, "w") as json_file:
                    json_file.write(json.dumps(access_layers, indent=4))
            except Exception as e:
                logger.error(f"Can't write {file_name}: {e}")

            logger.debug(f"Retrieving details for nat-rulebase in {pkg_name}")
            nat_rules = client.api_call("show-nat-rulebase", {
                        "package": pkg_name,
                        "details-level": "full",
                        "use-object-dictionary": True},)
            try:
                file_name = f"{package_dir}/nat_rules.json"
                with open(file_name, "w") as json_file:
                    json_file.write(strip_res_obj(nat_rules))
            except Exception as e:
                logger.error(f"Can't write {file_name}: {e}")
        return # fetch_packages_dmn ToDo add ApiResponse

    def fetch_api_dmn(self, mdm_server:Text, dmn:Text="") -> ApiStatus:
        """Fetch show-* from API and saves to TEMPCURR

        :param Text mdm_server: MDM server fqdn or name
        :param Text dmn: DMN optional (for SMS)
        :return _type_: _description_
        """
        fqdn = mgmt_get_fqdn(mdm_server)
        client = Mgmt().login( \
                ManagementToLogin(fqdn=fqdn, dmn=dmn))[1]
        if not client:
            raise Exception(f"fetch_api_dmn: Login failed for {mdm_server}/{dmn}")

        commands = self.enum_mgmt_api_calls_for_ver("1.8") # ToDo version
        # commands = ["show-hosts"]
        for command in commands:
            logger.debug(f"{command} on DMN {mdm_server}/{dmn}")
            response = client.api_query(command, details_level="full")
            # logger.debug(f"{command} on DMN {mdm_server}/{dmn}\n{strip_res_obj(response)}\n")

            try:
                file_name = f"{settings.DIR_SSOT}/{settings.DIR_MGMT}/" \
                            f"{fqdn}/{dmn}/{settings.MGMT_DIR_TEMP}/{command}.json"
                with open(file_name, "w") as json_file:
                    json_file.write(strip_res_obj(response))
            except Exception as e:
                logger.error(f"Can't write {file_name}: {e}")

        # fetch policies
        self.fetch_packages_dmn(mdm_server, dmn)

        result = ApiStatus(success=True, comment="Test OK", status_code=201)
        return result # fetch_api


def show_domains(mdm_fqdn_name: str) -> List[str]:
    client = Mgmt().login( \
            ManagementToLogin(fqdn=mgmt_get_fqdn(mdm_fqdn_name), dmn="System Data"))[1]
    res = client.api_call("show-domains", {
            "limit" : 250,
            "offset" : 0,
            "details-level" : "standard"})
    domains = [(domain['name'], domain) for domain in res.data['objects']]
    # logger.debug(domains)
    return domains # show_domains

#region cpf
router = APIRouter(
    prefix="/cpf",
    tags=["CPF"]
)


@router.post("/api_call/",
            description="Arbitrary api call")
def api_call(request:ApiCallRequest):
    client = Mgmt().login( \
            ManagementToLogin(fqdn=mgmt_get_fqdn(request.mgmt_server),
                              dmn=request.dmn))[1]
    response = client.api_call(request.command, request.payload)
    logger.debug(response)
    return response # api_call

@router.get("/update_ssot_mgmt_domains/{mdm_server}",
            description="Update SSoT directory structure for the domain by fqdn or name")
def update_ssot_mgmt_domains(mdm_server:Text) -> Dict[Text, List[Text]]:
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
                logger.info(f"Creating {dmn_path}")
                os.mkdir(dmn_path)
                dirs_created.append(dmn_path)
            except FileExistsError:
                logger.error(f"Can't create {dmn_path}. FileExists?")
                dirs_not_created.append(dmn_path)

        for dir in [settings.MGMT_DIR_DECL, settings.MGMT_DIR_LAST, settings.MGMT_DIR_TEMP]:
            mgmt_dir = os.path.join(dmn_path, dir)
            if not os.path.isdir(mgmt_dir):
                try:
                    logger.debug(f"Creating {mgmt_dir}")
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


@router.get("/fetch_api_mgmt_domains/{mdm_server}",
            description="Fetch all jsons from API to TEMPCURR from the domain by fqdn or name")
def fetch_api_mgmt_domains(mdm_server:Text) -> Dict[Text, List[Text]]:
    # Use checkboxes to select domains?
    domain_names = [domain[0] for domain in show_domains(mdm_server)]
    domain_names.append("Global")

    for dmn in domain_names:
        logger.warning(dmn)
        res = Mgmt().fetch_api_dmn(mdm_server, dmn=dmn)

    result = {
        "updated_domains": [],
        "not_updated_domains": []
    }
    return result # fetch_last_mgmt_domains

#endregion cpf


# def get_policy_components(
#         device_name: Text, device_ip: Text, domain: Text, url: Text, api_key: Text, output_path: Text, logger,
# ) -> None:

#     # Notes:
#     # "show-packages" gets the policy package list
#     #
#     # "show-package"  gets a specific policy package. this will have a list of access-layers, which needs to get fed
#     # into `show-access-rulebase` API call to get details of the layer (sections, inline layers, rules)
#     #
#     # "show-access-rulebase" should return everything we need in terms of access rules.
#     # According to their API docs:
#     # Shows the entire Access Rules layer. This layer is divided into sections. An Access Rule may be within a
#     # section, or independent of a section (in which case it is said to be under the "global" section).
#     # The reply features a list of objects. Each object may be a section of the layer, with all its rules in,
#     # or a rule itself, for the case of rules which are under the global section. An optional "filter" field
#     # may be added in order to filter out only those rules that match a search criteria. So we don't need to
#     # worry about using `show-access-layers`, `show-access-sections` or `show-access-rule` APIs
#     #
#     # "show-nat-rulebase" should return everything we need in terms of nat rules. it needs a package name as input
#     # According to their API docs:
#     # Shows the entire NAT Rules layer. This layer is divided into sections. A NAT Rule may be within a section,
#     # or independent of a section (in which case it is said to be under the "global" section). There are two
#     # types of sections: auto generated read only sections and general sections which are created manually.
#     # The reply features a list of objects. Each object may be a section of the layer, within which its rules
#     # may be found, or a rule itself, for the case of rules which are under the global section. An optional
#     # "filter" field may be added in order to filter out only those rules that match a search criteria.
#     # So we don't need to worry about using `show-nat-section` or `show-nat-rule` APIs

#     # retrieve list of packages
#     logger.info(f"Getting list of packages in domain {domain}")
#     packages_list = api_call(url, "show-packages", {"details-level": "full"}, api_key, pagination=True, logger=logger)
#     save_output_to_file(
#         device_name, domain, "show-packages", packages_list, output_path
#     )

#     # retrieve details of each package

#     # packages_list can have multiple package dictionaries embedded in it, due to the nature of data collection
#     # and pagination. So have to loop through all of the dictionaries in it and find the list of packages in
#     # each entry
#     for packages in packages_list:
#         for package in packages['packages']:
#             logger.debug(f"Retrieving details for package {package} in domain {domain} on {device_name}")
#             pkg_name = package['name']
#             pkg_uid = package['uid']
#             pkg_details = api_call(url, "show-package", {"name": pkg_name, "details-level": "full"},
#                                    api_key, pagination=False, logger=logger)
#             save_output_to_package_file(
#                 device_name, domain, pkg_name, "show-package", pkg_details,
#                 output_path)

#             logger.debug(f"Package {pkg_name} details: {pkg_details}")
#             if len(pkg_details) != 1:
#                 # API doesn't support pagination so results is a list with a single element
#                 exc_str = f"Call to get {pkg_name} details returned list that is not a single element"
#                 logger.error(exc_str)
#                 raise Exception(exc_str)

#             access_layers = []  # collect output of `show-access-rulebase` for each layer in package and append here
#             _acc_layers = pkg_details[0].get("access-layers", [])
#             for _acc_layer in _acc_layers:
#                 acc_layer_name = _acc_layer['name']
#                 logger.info(f"Retrieving access-rule-base {acc_layer_name} in package {pkg_name} "
#                              f"in domain {domain} on {device_name}")
#                 access_rulebase = api_call(url, "show-access-rulebase",
#                                            {"name": acc_layer_name, "details-level": "full", "use-object-dictionary": True},
#                                            api_key, pagination=True, logger=logger)
#                 access_layers.extend(access_rulebase)

#             save_output_to_package_file(
#                 device_name, domain, pkg_name, "show-access-rulebase", access_layers, output_path
#             )

#             logger.info(f"Retrieving nat-rulebase in package {pkg_name} in domain {domain} on {device_name}")
#             nat_rules = api_call(url, "show-nat-rulebase",
#                                  {"package": pkg_name, "details-level": "full", "use-object-dictionary": True},
#                                 api_key,  pagination=True, logger=logger)

#             save_output_to_package_file(
#                 device_name, domain, pkg_name, "show-nat-rulebase", nat_rules, output_path
#             )

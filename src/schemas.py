from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field, SecretStr, IPvAnyAddress
# from dataclasses import dataclass
from cpapi import APIClient

#region Gateway
class DescrGatewayDescription(BaseModel):
    """ Description section of __descr__.yaml for Gateway """
    description: str
    kind: Literal['SimpleGW', 'Maestro']
    name: str
    ipv4_address: IPvAnyAddress = Field(serialization_alias='ipv4-address')
    mgmt_name: str # SMS or MDM
    dmn: str = "" # Empty for SMS
    version: str
    JHF: Optional[int]

class DescrGateway(BaseModel):
    """ Full __descr__.yaml for the Management server / MDM """
    annotation: DescrGatewayDescription
    credentials: Dict = None

class GatewaySingle(BaseModel):
    """ Descr with fqdn """
    fqdn: str
    descr_file: DescrGateway

ListOfGatewaySingle = List[GatewaySingle]
#endregion Gateway


#region Management
class ApiCallRequest(BaseModel):
    mgmt_server: str
    dmn: str = ""
    command: str
    payload: Dict

class DescrManagementDescription(BaseModel):
    """ Description section of __descr__.yaml for the Management server / MDM """
    description: str
    kind: Literal["MDM", "SMS"]
    name: str
    ipv4_address: IPvAnyAddress = Field(serialization_alias='ipv4-address')
    version: str
    JHF: Optional[int]

class DescrManagement(BaseModel):
    """ Full __descr__.yaml for the Management server / MDM """

    annotation: DescrManagementDescription
    credentials: Dict = []

class ManagementServerSingle(BaseModel):
    fqdn: str
    descr_file: DescrManagement
    dmns: List[str] = []

class ManagementServerCachedInfo(BaseModel):
    fqdn: str
    name: str
    server_ip: IPvAnyAddress
    port: int = 443
    api_key: SecretStr = ""
    username: str = ""
    password: SecretStr = ""
    kind: str = ""
    dmn: str = ""
    client: APIClient = None

    class Config:
        arbitrary_types_allowed = True

class ManagementToLogin(BaseModel):
    """fqdn|name, [dmn], [cached client]"""
    fqdn: str = ""
    name: str = ""
    dmn: str = ""
    client: APIClient = None

    class Config:
        arbitrary_types_allowed = True

ListOfManagementServerSingle = List[ManagementServerSingle]
ListOfManagementServerCachedInfo = List[ManagementServerCachedInfo]
# ListOfManagementLoginInfo = List[ManagementToLogin]
#endregion Management

#region Etc
class ApiStatus(BaseModel):
    success: bool = False
    error_message: str = ""
    comment: str = ""
    status_code: int = 444 # default error
#endregion Etc

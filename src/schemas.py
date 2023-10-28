from typing import Dict, List, Literal
from pydantic import BaseModel, Field, SecretStr
# from dataclasses import dataclass


#region Gateway
class DescrGatewayDescription(BaseModel):
    """ Description section of __descr__.yaml for Gateway """
    description: str
    kind: Literal['SimpleGW', 'Maestro']
    name: str
    ipv4_address: str = Field(serialization_alias='ipv4-address')
    mgmt_name: str # SMS or MDM
    dmn: str = "" # Empty for SMS
    version: str
    JHF: int = None

class DescrGateway(BaseModel):
    """ Full __descr__.yaml for the Management server / MDM """
    annotation: DescrGatewayDescription
    credentials: Dict

class GatewaySingle(BaseModel):
    """ Descr with fqdn """
    fqdn: str
    descr_file: DescrGateway

ListOfGatewaySingle = List[GatewaySingle]
#endregion Gateway


#region Management
class DescrManagementDescription(BaseModel):
    """ Description section of __descr__.yaml for the Management server / MDM """
    description: str
    kind: Literal["MDM", "SMS"]
    name: str
    ipv4_address: str = Field(serialization_alias='ipv4-address')
    version: str
    JHF: int = None

class DescrManagement(BaseModel):
    """ Full __descr__.yaml for the Management server / MDM """
    annotation: DescrManagementDescription
    credentials: Dict = []

class ManagementServerSingle(BaseModel):
    fqdn: str
    descr_file: DescrManagement
    dmns: List[str] = []

class ManagementLoginInfo(BaseModel):
    fqdn: str
    name: str
    server: str
    port: int = 443
    api_key: SecretStr = ""
    username: str = ""
    password: SecretStr = ""
    kind: str = ""

ListOfManagementServerSingle = List[ManagementServerSingle]
#endregion Management

#region Etc
class ApiStatus(BaseModel):
    success: bool = False
    error_message: str = ""
    comment: str = ""
    status_code: int = 444 # default error
#endregion Etc

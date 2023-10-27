from typing import Dict, List, Literal
from pydantic import BaseModel, Field



#region Gateway
class DescrGatewayDescription(BaseModel):
    """ Description section of __descr__.yaml for Gateway """
    description: str
    kind: Literal['SimpleGW', 'Maestro']
    name: str
    ipv4_address: str = Field(serialization_alias='ipv4-address')
    mdm: str
    dmn: str
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

class ManagementDomainSingle(BaseModel):
    fqdn: str
    descr_file: DescrManagement
    dmns: List[str] = []
#endregion Management

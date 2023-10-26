from typing import Dict, List
from pydantic import BaseModel


#region Management
class DescrManagementDescription(BaseModel):
    """ description section of __descr__.yaml for the Management server / MDM """
    description: str
    kind: str
    name: str
    ipv4_address: str
    version: str
    JHF: str = ""

class DescrManagement(BaseModel):
    """ __descr__.yaml for the Management server / MDM """
    annotation: DescrManagementDescription
    credentials: Dict

class ManagementDomainSingle(BaseModel):
    fqdn:   str
    descr_file: DescrManagement
    dmns: List[str] = []
#endregion Management

from typing import Dict, List
from pydantic import BaseModel


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
    __descr__: DescrManagementDescription
    dmns: List[str] = []

class ManagementDomainsList(BaseModel):
    element: List[Dict[str, ManagementDomainSingle]]

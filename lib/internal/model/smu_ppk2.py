from lib.external.pythontools.dict_adaptable import DictAdaptable
from lib.external.pythontools.ppk2_api_modified import PPK2_API


# ==================== Settings for PPK2 ======================= #
class SMUPPK2Config(DictAdaptable):
    ID: str
    Port: str
    Voltage: int
    Device: PPK2_API

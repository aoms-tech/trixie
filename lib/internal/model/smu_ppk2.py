from lib.external.pythontools.dict_adaptable import DictAdaptable
from ppk2_api.ppk2_api import PPK2_API


# ==================== Settings for PPK2 ======================= #
class SMUPPK2Config(DictAdaptable):
    ID: str
    Port: str
    Voltage: int
    Device: PPK2_API

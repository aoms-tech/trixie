from lib.external.pythontools.dict_adaptable import DictAdaptable
from lib.internal.model.smu_ppk2 import SMUPPK2Config
from lib.external.mCommon3.model.serialcomm import SerialConfig


# ==================== Settings for Trixie ======================= #
class TrixieConfig(DictAdaptable):
    Channel1: SMUPPK2Config
    Channel2: SMUPPK2Config
    InputComm: SerialConfig

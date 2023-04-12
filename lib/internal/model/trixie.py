from lib.external.pythontools.dict_adaptable import DictAdaptable
from lib.internal.model.smu_ppk2 import SMUPPK2Config
from lib.external.mCommon3.model.serialcomm import SerialConfig
from adafruit_mcp3xxx.mcp3008 import MCP3008


# ==================== Settings for Trixie ======================= #
class TrixieConfig(DictAdaptable):
    Channel1: SMUPPK2Config
    Channel2: SMUPPK2Config
    Feedback: MCP3008
    InputComm: SerialConfig

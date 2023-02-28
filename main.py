from os import path

from lib.external.pythontools.config import get_settings_dict_from_yaml

from lib.internal.service.trixie_service import run_application
from lib.internal.model.trixie import TrixieConfig


if __name__ == '__main__':
    run_application(
        TrixieConfig(
            get_settings_dict_from_yaml(
                path.join(path.dirname(path.abspath(__file__)), 'config', 'settings_config.yaml'),
                path.dirname(path.abspath(__file__))
            )
        )
    )

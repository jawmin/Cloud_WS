import os
import logging.config
import yaml


def setup_logging(default_path='logging.yaml', default_level=logging.INFO, env_key='LOG_CFG'):
    """
    Setup logging configuration from the logging file
    :param default_path: path for the logging file, default being logging.yaml
    :param default_level: level for the log, default being INFO
    :param env_key: environment value to get the path of the file
    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.load(f.read())
            logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

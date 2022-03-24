import logging
import logging.config
import yaml
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
with open("./log_config.yaml", "r") as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

logger = logging.getLogger(__name__)

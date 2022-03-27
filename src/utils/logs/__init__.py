import logging
import logging.config
import yaml
import os


def create_logfile(log_file_list: list[str], path: str):
    for log_file in log_file_list:
        try:
            file = open(path + "/" + log_file, "r")
            file.close()
        except IOError:
            file = open(path + "/" + log_file, "w")
            file.close()


base_log_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(base_log_path)
log_file_path = base_log_path + "/logfile"
log_files_name = ["error.log", "debug.log", "info.log"]
if not os.path.exists(log_file_path):
    os.makedirs(log_file_path)

create_logfile(log_files_name, log_file_path)

with open("./log_config.yaml", "r") as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)
    f.close()

logger = logging.getLogger(__name__)

import logging


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger

class Workflow:
    def __init__(self, name, workflow_config):
        self.name = name
        self.workflow_config = workflow_config
        self.tasks = []

    def add_task(self, node, task_name, *args):
        self.tasks.append((node, task_name, args))
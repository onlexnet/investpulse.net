import logging


log = logging.getLogger()
log.setLevel(logging.DEBUG)
__formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
__handler = logging.StreamHandler()  # Log to the console
__handler.setFormatter(__formatter)
log.addHandler(__handler)

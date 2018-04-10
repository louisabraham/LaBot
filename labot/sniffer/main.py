from .network import launch_in_thread
from . import ui


ui.init(launch_in_thread)
ui.async_start()

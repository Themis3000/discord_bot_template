"""
Manages yaml config file handling
"""
import yaml


class Config:
    """
    A very basic yaml file handler class
    """
    def __init__(self, filepath):
        self.filepath = filepath
        self.handlers = {}
        with open(self.filepath, 'r') as f:
            self.settings = yaml.load(f, Loader=yaml.BaseLoader)

    def __getitem__(self, key):
        """
        Get key processed through any get handlers if they exist for a given path. pass key in as if it where accessing
        yaml file as a flattened nested dict with a . as the separator
        e.g.
        instead of calling Config['setting']['subsetting']
        you would call Config['setting.subsetting']

        If you wish to get raw settings dict without any processing, use Config.settings
        """
        path = key.split(".")
        _dict = self.settings
        for _key in path:
            _dict = _dict[_key]
        if key in self.handlers:
            return self.handlers[key](_dict)
        return _dict

    def register_get_handler(self, key):
        """
        A decorator that registers a function to be used for modifying the output of a __getitem__ call
        """
        def registerhandler(handler):
            self.handlers[key] = handler
            return handler
        return registerhandler

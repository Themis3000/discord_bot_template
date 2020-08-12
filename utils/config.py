"""
Manages yaml config file handling
"""
import yaml


class Config:
    """
    A very basic yaml file handler class, made to be used as a parent class the key_update_event decorator can be utilized
    """
    def __init__(self, filepath):
        self.filepath = filepath
        self.handlers = {}
        with open(self.filepath, 'r') as f:
            self.settings = yaml.load(f)

    def update(self, key: str, value):
        """
        handles basic key, value updates and writes changes to file immediately
        """
        self.call(key)
        self.settings[key] = value
        with open(self.filepath, "w") as f:
            f.write(yaml.dump(f, self.settings))

    def key_update_event(self, key: str):
        """
        A function decorator that adds a given function to the handlers to be used when a setting is updated
        :param key: The key of the setting the function will be ran for on update
        """
        def registerhandler(handler):
            if key in self.handlers:
                self.handlers[key].append(handler)
            else:
                self.handlers[key] = [handler]
            return handler
        return registerhandler

    def call(self, event_name):
        if event_name in self.handlers:
            for h in self.handlers[event_name]:
                h()


class MainConfig(Config):
    """
    used for the min config.yaml file
    """
    def __init__(self, client=None):
        Config.__init__(self, "./config.yml")
        self.client = client

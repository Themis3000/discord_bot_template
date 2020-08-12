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
            self.settings = yaml.load(f, Loader=yaml.BaseLoader)

    def update(self, key: str, value):
        """
        handles basic key, value updates and writes changes to file immediately
        """
        self.update_event(key)
        self.settings[key] = value
        with open(self.filepath, "w") as f:
            yaml.dump(self.settings, f, yaml.Dumper)

    def register_update_handler(self, key: str):
        """
        A function decorator that adds a function to the event handlers dict
        """
        def registerhandler(handler):
            if key in self.handlers:
                self.handlers[key].append(handler)
            else:
                self.handlers[key] = [handler]
            return handler
        return registerhandler

    def update_event(self, event_name):
        if event_name in self.handlers:
            for h in self.handlers[event_name]:
                h()


#class MainConfig(Config):
#    """
#    used for the min config.yaml file
#    """
#    def __init__(self):
#        Config.__init__(self, "./config.yaml")
#
#        @self.register_update_handler(self, "foo")
#        def foo():
#            print("updated")

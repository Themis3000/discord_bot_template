"""
Manages yaml config file handling
"""
import yaml
import discord


converter_dict = {"online": discord.Status.online,
                  "offline": discord.Status.offline,
                  "idle": discord.Status.idle,
                  "dnd": discord.Status.dnd,
                  "invisible": discord.Status.invisible,
                  "game": discord.Game,
                  "streaming": discord.Streaming,
                  "custom": discord.CustomActivity}


# todo add __dict__ magic statement possibly with converting built in
class Config:
    """
    A very basic yaml file handler class
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

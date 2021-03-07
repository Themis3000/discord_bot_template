"""Includes useful utilities for time based operations"""


def convert_millis(millis):
    seconds = (millis / 1000) % 60
    minutes = (millis / (1000 * 60)) % 60
    hours = (millis / (1000 * 60 * 60)) % 24
    return seconds, minutes, hours


def convert_millis_str(millis):
    seconds, minutes, hours = convert_millis(millis)
    if hours > 0:
        return f"{hours}:{minutes}:{seconds}"
    return f"{minutes}:{seconds}"

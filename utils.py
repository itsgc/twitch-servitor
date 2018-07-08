import yaml

def make_auth(credsfile_path):
    with open(credsfile_path, 'r') as credsfile:
        return yaml.load(credsfile)

def make_settings(settingsfile_path):
    with open(settingsfile_path, 'r') as settingsfile:
        return yaml.load(settingsfile)
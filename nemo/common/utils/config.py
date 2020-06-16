#!/usr/bin/env python3
# coding: utf-8
import yaml


def load_config(config_file='instance/config.yaml'):
    with open(config_file) as f:
        return yaml.load(f, Loader=yaml.CLoader)


def save_config(config_jsondata, config_file='instance/config.yaml'):
    with open(config_file, 'w') as f:
        yaml.dump(config_jsondata, f)

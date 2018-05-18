#!/usr/bin/env python2
# -*- coding:utf-8 -*-

### **************************************************************************** ###
# 
# Project: Snips Web Admin
# Created Date: Sunday, May 6th 2018, 9:12:44 am
# Author: Greg
# -----
# Last Modified: Thu May 17 2018
# Modified By: Greg
# -----
# Copyright (c) 2018 Greg
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN
# AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# 
### **************************************************************************** ###




import os
import yaml
from ..flask_yaml import OrderedDictYAMLLoader
from collections import OrderedDict


def get_assistant_info_(snipfile):
        """ Initialisation.
        :param snipsfile: path for the Snipsfile.
        """

        #'/usr/share/snips/assistant'
        snipsfile = snipfile
    
        assistant_url = None

        if not os.path.isfile(snipsfile):
            return {'error': 'No Snipsfile found at path {}.'.format(snipsfile)}

        yaml_config = None
        with open(snipsfile, 'r') as yaml_file:
            try:
                #yaml_config = yaml.load(yaml_file)
                yaml_config = yaml.load(yaml_file, Loader=OrderedDictYAMLLoader)
            except yaml.scanner.ScannerError as err:
                return {'error': str(err)}

        if not yaml_config:
            return {}

        adict = {}

        for k, v in yaml_config.items():
            if  k != "skills":
                adict[k] = v
            else:
                adict['slots'] = v

        return adict


        
        '''
        assistant_id = get(yaml_config, ['assistant_id'])
        assistant_file = get(yaml_config, ['assistant_file'])
        assistant_url = get(yaml_config, ['assistant_url'])
        snips_sdk_version = get(yaml_config, ['snips_sdk', 'version'])
        locale = get(yaml_config, ['locale'], 'en_US')
        tts_service = get(yaml_config, ['tts', 'service'])
        default_location = get(yaml_config, ['default_location'], 'Paris,fr')
        mqtt_hostname = get(yaml_config, ['mqtt_broker', 'hostname'], 'localhost')
        mqtt_port = get(yaml_config, ['mqtt_broker', 'port'], 1883)
        modify_asoundconf = get(yaml_config, ['modify_asoundconf'], True)
        #microphone_config = MicrophoneConfig(yaml_config)
        #speaker_config = SpeakerConfig(yaml_config)

        
        skilldefs = []

        for skill in get(yaml_config, ['skills'], []):
            url = get(skill, ['url'], get(skill, ['pip']))
            package_name = get(skill, ['package_name'])

            params = {}
            for key, value in get(skill, ['params'], {}).items():
                params[key] = value

            snipsspec_file = None
            try:
                if package_name is not None:
                    snipsspec_file = SnipsSpec(package_name)
            except (SnipsspecNotFoundError, SnipsfileParseException) as e:
                pass
            name = get_skill_attribute(skill, snipsspec_file, 'name')
            class_name = get_skill_attribute(skill, snipsspec_file, 'class_name')
            requires_tts = get_skill_attribute(skill, snipsspec_file, 'requires_tts', False)
            addons = get_skill_attribute(skill, snipsspec_file, 'addons', [])

            intent_defs = get_intent_defs(skill, snipsspec_file)
            notification_defs = get_notification_defs(skill, snipsspec_file)
            dialogue_events_defs = get_dialogue_events_defs(skill, snipsspec_file)

            skilldefs.append(SkillDef(name, package_name, class_name, url,
                                           params, intent_defs, dialogue_events_defs, notification_defs,
                                           requires_tts, addons))
            
            '''

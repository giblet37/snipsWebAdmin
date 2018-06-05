#!/usr/bin/env python2
# -*- coding:utf-8 -*-

### **************************************************************************** ###
# 
# Project: Snips Web Admin
# Created Date: Sunday, May 27th 2018, 10:39:55 pm
# Author: Greg
# -----
# Last Modified: Tue Jun 05 2018
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





from flask_table import Table, Col, html 
import yaml
import json


            
class Item(object):
    def __init__(self, name, description=None):
        self.name = name
        self.description = description

class ItemTable(Table):
    no_items = 'No assistant installed'
    classes = ['table']
    name = Col(
        'Config Setting',
        # Apply this class to both the th and all tds in this column
        column_html_attrs={'class': 'my-name-class'},
        th_html_attrs={'class': 'table-active'},
    )
    description = Col(
        'Value', 
        # Apply these to both
        column_html_attrs={
            'data-something': 'my-data',
            'class': 'my-description-class'},
        # Apply this to just the th
        th_html_attrs={'class': 'table-active'},
        # Apply this to just the td - note that this will things from
        # overwrite column_html_attrs.
        td_html_attrs={'data-something': 'my-td-only-data'},
        
    )

class SkillsItem(object):
    def __init__(self, name, url):
        self.name = name
        self.url = url

class SkillsItemTable(Table):
    no_items = 'Nothing to show'
    classes = ['table']
    name = Col(
        'Skill',
        # Apply this class to both the th and all tds in this column
        column_html_attrs={'class': 'my-name-class'},
        th_html_attrs={'class': 'table-active'},
    )
    url = Col(
        'URL', 
        # Apply these to both
        column_html_attrs={
            'data-something': 'my-data',
            'class': 'my-description-class'},
        # Apply this to just the th
        th_html_attrs={'class': 'table-active'},
        # Apply this to just the td - note that this will things from
        # overwrite column_html_attrs.
        td_html_attrs={'data-something': 'my-td-only-data'},
        
    )

class SnippetItem(object):
    def __init__(self, name):
        self.name = name

class SnippetItemTable(Table):
    no_items = 'Nothing to show'
    classes = ['table']
    name = Col(
        'Snippet Directories',
        # Apply this class to both the th and all tds in this column
        column_html_attrs={'class': 'my-name-class'},
        th_html_attrs={'class': 'table-active'},
    )

    #def __init__(self, name):
    #    self.name = name



def get_assistant_table(snippets=[], snipsyaml='', snipsjson=''):
    #slots
    #base info from file
    try:
        #******************* assistant info
        assitantdict = {}
        yaml_config = yaml.load(snipsyaml.replace("<br>","\n"))
        
        try:
            for k, v in yaml_config.items():
                if  k != "skills":
                    assitantdict[k] = v
                else:
                    assitantdict['slots'] = v
        except:
            pass
        
    
        assistant_items = []
        assistant_slots = []
        try:
            for key, value in assitantdict.items():
                if key == "slots":
                    for v in value:
                        assistant_slots.append(SkillsItem(v['name'],v['url']))
        except:
            pass
        
        #******************* assistant json
        try:
            json_config = json.loads(snipsjson.replace("<br>","\n"))
            assistant_items.append(Item("Project ID", json_config['id']))
            assistant_items.append(Item("Assistant", json_config['name']))
            assistant_items.append(Item("Language", json_config['language']))
            assistant_items.append(Item("ASR Type", json_config['asr']['type']))
            assistant_items.append(Item("Hotword", json_config['hotword']))
            istring = ''
            for it in json_config['intents']:
                istring += "{}&lt;br/&gt;".format(it['name'])

            assistant_items.append(Item("Intents", istring))
        except:
            pass
            
     
        #******************* snippets
        snippets_items = []
        for si in snippets.split("<br>"):
            snippets_items.append(SnippetItem(name=si))

        #print(assistant_items)
        #print(assistant_slots)
        #print(snippets_items)
        table_assistant = ItemTable(assistant_items)
        table_slots = SkillsItemTable(assistant_slots)
        table_slots.no_items = "No Skills have been included in the assistant file"
        table_snippets = SnippetItemTable(snippets_items)
        table_snippets.no_items = "No Snippets to list"
        return table_assistant, table_slots, table_snippets
    except Exception as e:
        print(e)
        return None,None,None
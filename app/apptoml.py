#!/usr/bin/env python2
# -*- coding:utf-8 -*-

### **************************************************************************** ###
# 
# Project: Snips Web Admin
# Created Date: Tuesday, May 29th 2018, 6:12:46 pm
# Author: Greg
# -----
# Last Modified: Sat Jun 02 2018
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




import toml
from collections import OrderedDict

import logging
logger = logging.getLogger('snipsWebAdmin-toml')


class tomlDB():

    def __init__(self, file=None):
        
        self.data = {} 
        self.file = file

        if self.file:
            self.data = toml.load(self.file, _dict=OrderedDict)


    def get_toml_data(self, heading):
        if heading in self.data:
            return self.data[heading]
        else:
            return None
    
    def get_slot_toml_data(self, slot):
        for key in self.data:
            for k in self.data[key]:
                if slot == k:
                    return self.data[key][k]
        return None

    #def delete_heading(self, heading):
    #    if heading in self.data: 
    #        del self.data[heading]
    def delete_by_hostname(self,device):
        devicelist = self.get_toml_data("DEVICES")
        dev = filter(lambda x : x['HOSTNAME'] == device, devicelist) 

        self.data["DEVICES"].remove(dev[0])
        self.save_toml_file()


    def delete_slot(self, slot):
        del self.data['Custom'][slot]
        self.save_toml_file()

    def set_toml_data(self, heading, datain):
        datain = [x for x in datain if x] #remove empty list items
        self.data[heading] = datain
        #self.save_toml_file()

    def set_slot_toml_data(self, slot, datain):
        datain = [x for x in datain if x] #remove empty list items
        print(datain)
        for key in self.data:
            for k in self.data[key]:
                if slot == k:
                    self.data[key][k] = datain
       

    def save_toml_file(self):
        with open(self.file, 'w') as f:
            toml.dump(self.data, f)
        #toml.dump(self.data, self.file)
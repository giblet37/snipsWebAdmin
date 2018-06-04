#!/usr/bin/env python2
# -*- coding:utf-8 -*-

### **************************************************************************** ###
# 
# Project: Snips Web Admin
# Created Date: Saturday, June 2nd 2018, 1:06:10 pm
# Author: Greg
# -----
# Last Modified: Mon Jun 04 2018
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
#from utils import SSHConnect
import string

class ActiveInactiveCol(Col):

    def td(self, item, attr):
        content = self.td_contents(item, self.get_attr_list(attr))
        if item.isActive == 'Active':
            return html.element(
                'td',
                content=content,
                escape_content=False,
                attrs={'class': 'serviceActive'})
        elif item.isActive == 'Inactive':
                return html.element(
                    'td',
                    content=content,
                    escape_content=False,
                    attrs={'class': 'serviceInactive'})
        elif item.isActive == 'Activating':
                return html.element(
                    'td',
                    content=content,
                    escape_content=False,
                    attrs={'class': 'serviceActivating'})
        else:
            return html.element(
                'td',
                content=content,
                escape_content=False,
                attrs={'class': 'serviceNone'})
            
class serviceItem(object):
    def __init__(self, name, version, isActive):
        self.name = name
        self.version = version
        self.isActive = isActive

class serviceItemTable(Table):
    no_items = 'No Snips services installed'
    classes = ['table']
    name = Col('Snips Service',
        # Apply this class to both the th and all tds in this column
        column_html_attrs={'class': 'my-name-class'},
        th_html_attrs={'class': 'table-active'},
    )
    version = Col('Version',
        # Apply this class to both the th and all tds in this column
        column_html_attrs={'class': 'my-name-class'},
        th_html_attrs={'class': 'table-active'},
    )
    isActive = ActiveInactiveCol('Service',
        # Apply this class to both the th and all tds in this column
        column_html_attrs={'class': 'my-name-class'},
        th_html_attrs={'class': 'table-active'},
    )


def get_snips_service_table(device={},services={}):
    
    
    listItems =[]

    for key, value in sorted(services.iteritems()):
        service = key.split(' ')
        version = ''
        if len(service) > 1:
            version = service[1]

            is_Service = value[1].split("<br>")
        
            if is_Service[0] == "loaded":
                is_active = is_Service[1]
                listItems.append(serviceItem(service[0], version ,is_active.capitalize()))
            else:
                listItems.append(serviceItem(service[0], version ,''))

    return serviceItemTable(listItems)

#!/usr/bin/env python2
# -*- coding:utf-8 -*-

### **************************************************************************** ###
# 
# Project: Snips Web Admin
# Created Date: Sunday, May 6th 2018, 9:12:44 am
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




from flask import current_app

import paramiko
from collections import OrderedDict
import commands

import logging
logger = logging.getLogger('snipsWebAdmin-Devices-Utils')


class SSHConnect():

    def getIP(self, hoststring):
        if hoststring == "localhost.local":
            hoststring = "127.0.0.1"
        return commands.getoutput("ping -c 1 {} | grep \'64 bytes from \' | awk \'{}\' | cut -d\":\" -f1".format(hoststring,"{print $4}"))
       

    #def __init__(self, *args, **kwargs):
    #    pass

    def connect(self, hoststring, command=''):
        
        ip = ''
        if hoststring.find('.') > 0:
            ip = hoststring
        else:
            ip = self.getIP("{}.local".format(hoststring))
        
        logger.info("SSH Connecting...{} - {}".format(hoststring,ip))

        try:
            sshClient = paramiko.SSHClient()
            sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            sshClient.load_system_host_keys() 
            
            sshClient.connect(ip,port=22,username=current_app.config['CLIENT_USER'],password=current_app.config['CLIENT_PASSWORD'],timeout=5)
            stdin, stdout ,stderr = sshClient.exec_command(command)
            #logger.info(stdin, stdout ,stderr)
            stdout=stdout.readlines()
            stderr=stderr.readlines()
         
            sshClient.close()
            logger.info("SSH Closed...{} - {}".format(hoststring,ip))

            return stderr, stdout
        except Exception as e: # (AuthenticationException, UnknownHostException, ConnectionErrorException):
            logger.info("SSH Connection Error: {}".format(e))
            return "Error: {}".format(e), None
        
    def connectSudo(self, device, commands=[], socket=None, socketTopic="", namespace=None):
        
        ip = ''

        if device['HOSTNAME'].find('.') > 0:
            ip = device['HOSTNAME']
        else:
            ip = self.getIP("{}.local".format(device['HOSTNAME']))
        
        logger.info("SSH Connecting...{} - {}".format(device['HOSTNAME'],ip))
        if "cannot resolve" in ip:
            return "error: {}".format(ip), None

        logger.info("Running command with SUDO")

        try:
            sshClient = paramiko.SSHClient()
            sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            sshClient.load_system_host_keys() 
            
            sshClient.connect(ip,port=22,username=device['USER'],password=device['PASSWORD'],timeout=5)

            transport = sshClient.get_transport()
            

            errorlist = []
            
            for cmds in commands:
                session = transport.open_session()
                #session.set_combine_stderr(False)
                session.get_pty()
                stdin = session.makefile('wb', -1)
                stdout = session.makefile('rb', -1)
                stderr = session.makefile('rb', -1)
                session.exec_command(cmds)
                
                #you have to check if you really need to send password here 
                stdin.write('{}\n'.format(device['PASSWORD']))
                stdin.flush()
                stdout.readline() #removes from reading in the password line thats entered
                
                if socket:
                    socket.emit(socketTopic, cmds, namespace=namespace)
                    while True:
                        line = stdout.readline()
                        #print(line)
                        if line != '':
                            text = line.rstrip() + "<br>"
                            socket.emit(socketTopic, text, namespace=namespace)
                        else:
                            break
                
                stdout=stdout.readlines()
                stderror=stderr.readlines()

                #logger.info("stdout: {}".format(stdout))
                #logger.info("stderror: {}".format(stderror))

                if stderror:
                    errorlist.append(stderror)
                session.close()

            transport.close()
            sshClient.close()
            logger.info("SSH Closed...{} - {}".format(device['HOSTNAME'],ip))
          
            return errorlist
        except Exception as e: # (AuthenticationException, UnknownHostException, ConnectionErrorException):
            logger.info("SSH Connection Error: {}".format(e))
            return "error: {}".format(e), None

    def connectDevice(self, device, commands={}):
        ip = ''

        if device['HOSTNAME'].find('.') > 0:
            ip = device['HOSTNAME']
        else:
            ip = self.getIP("{}.local".format(device['HOSTNAME']))

        logger.info("SSH Connecting...{} - {}".format(device['HOSTNAME'],ip))
        if "cannot resolve" in ip:
            return "Error: {}".format(ip), None

        try:
            returnDict = {}
            sshClient = paramiko.SSHClient()
            sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            sshClient.load_system_host_keys() 
            
            sshClient.connect(ip,port=22,username=device['USER'],password=device['PASSWORD'],timeout=5,auth_timeout=5)
            
            for key, value in commands.iteritems():
                stdin, stdout ,stderr = sshClient.exec_command(value)
                
                stdout=stdout.readlines()
                #if len(stdout)>0:
                #    print(stdout)
                #stdout=stdout.read()
                #stdout = ''.join(stdout)
                text=''
                for line in stdout:
                    if line != '':
                        text += line.rstrip() + "<br>"
                
                stderr=stderr.readlines()

                #special connection to get if services active or not
                #for building the services table
                if key == "services":
                    commandsList = {}
                    rdict = {}
                    services = text.split("<br>")
                    services = filter(None, services)
                    for s in services:
                        name = s.split(' ')
                        comm = "systemctl show -p LoadState {} | sed 's/LoadState=//g';systemctl show -p ActiveState {} | sed 's/ActiveState=//g'".format(name[0], name[0])
                        stdin, stdout ,stderr = sshClient.exec_command(comm)
                        stdout=stdout.readlines()
                        text=''
                        for line in stdout:
                            if line != '':
                                text += line.rstrip() + "<br>"
                        
                        stderr=stderr.readlines()
                        rdict[s] = [stderr,text]
                    returnDict[key] = [stderr,rdict]
                else:
                    returnDict[key] = [stderr,text]
            
            sshClient.close()
            logger.info("SSH Closed...{} - {}".format(device['HOSTNAME'],ip))
            
            return returnDict

        except paramiko.ssh_exception.AuthenticationException as ae:
            logger.info("SSH Authentication Error: {}".format(ae))
            return "Error: {}".format(ae), None
        except paramiko.ssh_exception.NoValidConnectionsError as uhe:
            logger.info("SSH NoValidConnectionsError Error: {}".format(uhe))
            return "Error: {}".format(uhe), None
        except paramiko.ssh_exception.BadAuthenticationType as cee:
            logger.info("SSH BadAuthenticationType Error: {}".format(cee))
            return "Error: {}".format(cee), None
        except paramiko.ssh_exception.SSHException as ceee:
            logger.info("SSH BadAuthenticationType Error: {}".format(ceee))
            return "Error: {}".format(ceee), None
        except Exception as e: # (AuthenticationException, UnknownHostException, ConnectionErrorException):
            logger.info("SSH Connection Error: {}".format(e))
            return "Error: {}".format(e), None
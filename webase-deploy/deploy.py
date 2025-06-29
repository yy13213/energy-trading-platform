#!/usr/bin/python3
# encoding: utf-8

import sys

# check python version first
# check before import in case of avoiding error of mysql lib not found in comm.check package
if not sys.version_info.major == 3 and sys.version_info.minor >= 6:
    print("This script requires Python 3.6 or higher!")
    print("You are using Python {}.{}.".format(sys.version_info.major, sys.version_info.minor))
    sys.exit(1)

import comm.check as commCheck
import comm.build as commBuild
import comm.global_var as gl

def do():
    if len(sys.argv)==1:
        help()
        return
    param = sys.argv[1]
    if "installAll" == param:
        gl.set_install_all()
        commCheck.do()
        commBuild.do()
    elif "startAll" == param:
        commCheck.checkPort()
        commBuild.start()
    elif "stopAll" == param:
        commBuild.end()
    elif "startNode" == param:
        commBuild.startNode()
    elif "stopNode" == param:
        commBuild.stopNode()
    elif "startWeb" == param:
        commBuild.startWeb()
    elif "stopWeb" == param:
        commBuild.stopWeb()
    elif "startManager" == param:
        commBuild.startManager()
    elif "stopManager" == param:
        commBuild.stopManager()
    elif "startFront" == param:
        commBuild.startFront()
    elif "stopFront" == param:
        commBuild.stopFront()
    elif "startSign" == param:
        commBuild.startSign()
    elif "stopSign" == param:
        commBuild.stopSign()
    elif "check"== param:
        commCheck.do()
    elif "help"== param:
        help()
    else:
        paramError()
    return

def help():
    helpMsg = '''
Usage: python deploy [Parameter]

Parameter:
    check:          check the environment
    installAll:     check the environment, deploy FISCO-BCOS and all service 
    startAll:       check service port, start all service 
    stopAll:        stop all service
    startNode:      start FISCO-BCOS nodes
    stopNode:       stop FISCO-BCOS nodes
    startWeb:       start WeBASE-Web service
    stopWeb:        stop WeBASE-Web service
    startManager:   start WeBASE-Node-Manager service
    stopManager:    stop WeBASE-Node-Manager service
    startFront:     start WeBASE-Front service
    stopFront:      stop WeBASE-Front service
    startSign:      start WeBASE-Sign service
    stopSign:       stop WeBASE-Sign service

Attention:
    1. Need to install python3.6, jdk, mysql, PyMySQL first
    2. Need to ensure a smooth network
    3. You need to install git,openssl,curl,wget,nginx,dos2unix; if it is not installed, the installation script will automatically install these components, but this may fail.
    '''
    print (helpMsg)
    return

def paramError():
    print ("")
    print ("Param error! Please check.")
    help()
    return

if __name__ == '__main__':
    do()
    pass

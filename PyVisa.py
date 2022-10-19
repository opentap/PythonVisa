"""
 Passthrough I/O to pyvisa
"""
from System import String, Int32, Int16, Byte, UInt32, ArraySegment, Double, Boolean
from System.ComponentModel import BrowsableAttribute
from System.Text import StringBuilder
import System.Threading
import OpenTap
import OpenTap.Cli
from OpenTap import IVisa, ComponentSettings
from opentap import *
import random

import pyvisa
    
class PyVisa(OpenTap.ITapPlugin, OpenTap.IVisa):
    _foundLists = {}
    _rm = None
    _connections = {}
    
    @method(Int32,[Int32]) 
    @staticmethod
    def viOpenDefaultRM(sesn):  
        PyVisa._rm = pyvisa.ResourceManager(OpenTap.ComponentSettings.GetCurrent(PyVisaSettings).Backend)
        print(PyVisa._rm)
        PyVisa._rm.visalib.issue_warning_on = {}
        return 0, PyVisa._rm.session  
        
        
    @method(Int32,[Int32, String, Int32, Int32, StringBuilder])
    @staticmethod
    def viFindRsrc(sesn, expr, vi, retCount, desc):
        devices = PyVisa._rm.visalib.list_resources(sesn, expr)
        
        if (len(devices) == 0):
            return pyvisa.constants.StatusCode.error_resource_not_found, 0, 0, "" 
        
        #TODO: this needs tested.
        # something was returned     
        # fake a findId, because we don't get it back from pyvisa
        vi = random.randrange(-2147483648, 2147483647)
        print("")
        desc = devices[0]
        retCount = len(devices)
        devices.pop(0)
        PyVisa._foundLists[sesn, [vi, devices]]            

        return pyvisa.constants.StatusCode.success, vi, retCount, desc
        
    @method(Int32,[Int32, StringBuilder])
    @staticmethod
    def viFindNext(vi, desc):
        #TODO: implement this
        return pyvisa.constants.StatusCode.error_resource_not_found, ""
        
    @method(Int32,[Int32, String, Int16, Int16])
    @staticmethod
    def viParseRsrc(sesn, desc, intfType, intfNum):
        intfType = 0
        intfNum = 0
        resourceInfo, statusCode = PyVisa._rm.visalib.parse_resource(sesn, desc)
        intfType = resourceInfo.interface_type
        intfNum = resourceInfo.interface_board_number
        
        return StatusCode.value, intfType, intfNum
        
    @method(Int32,[Int32, String, Int16, Int16, StringBuilder, StringBuilder, StringBuilder])
    @staticmethod
    def viParseRsrcEx(sesn, desc, intfType, intfNum, rsrcClass, expandedUnaliasedName, aliasIfExists):
        intfType = 0
        intfNum = 0
        resourceClass = 0
        expandedUnaliasedName = ""
        resourceInfo, statusCode = PyVisa._rm.visalib.parse_resource_extended(sesn, desc)
        intfType = resourceInfo.interface_type
        intfNum = resourceInfo.interface_board_number
        resourceClass = resourceInfo.resource_class
        expandedUnaliasedName = resourceInfo.resource_name
        aliasIfExists = ""
        return StatusCode.value, intfType, intfNum, resourceClass, expandedUnaliasedName, aliasIfExists
        
    @method(Int32,[Int32, String, Int32, Int32, Int32])
    @staticmethod
    def viOpen(sesn, viDesc, mode, timeout, vi):
        vi, StatusCode = PyVisa._rm.visalib.open(sesn, viDesc, mode, timeout)
        if (StatusCode == pyvisa.highlevel.StatusCode.success):
            PyVisa._connections[str(vi)] = {'rm': sesn, 'address': viDesc}
        return StatusCode.value, vi
        
    @method(Int32,[Int32])
    @staticmethod
    def viClose(vi):
        StatusCode = PyVisa._rm.visalib.close(vi)
        return StatusCode.value
        
    @method(Int32,[Int32, UInt32, Byte])
    @staticmethod
    def viGetAttribute1(vi, attrName, attrValue):
        try:
            attrValue, StatusCode = PyVisa._rm.visalib.get_attribute(vi, attrName)
        except pyvisa.errors.VisaIOError as err:
            if (err.error_code == pyvisa.constants.StatusCode.error_nonsupported_attribute):
                print("pyvisa warning: ignoring error_non_supported_attribute on get_attribute1. name: {0}, value: {1}".format(attrName, attrValue))
                StatusCode = pyvisa.constants.StatusCode.success
            else:
                print("viGetAttribute1: {0}, {1}".format(err.error_code, err.description))
        return StatusCode.value, attrValue

    @method(Int32,[Int32, Int32, StringBuilder])
    @staticmethod
    def viGetAttribute2(vi, attrName, attrValue):
        try:
            if (attrName == -1073807359 and str(vi) in PyVisa._connections):#VI_ATTR_RSRC_CLASS
                resourceInfo, statusCode = PyVisa._rm.visalib.parse_resource_extended(PyVisa._connections[str(vi)]['rm'], PyVisa._connections[str(vi)]['address'])
                attrValue.Append(resourceInfo.resource_class)
                return pyvisa.constants.StatusCode.success.value
            else:
                attrValue, StatusCode = PyVisa._rm.visalib.get_attribute(vi, attrName)
        except pyvisa.errors.VisaIOError as err:
            if (err.error_code == pyvisa.constants.StatusCode.error_nonsupported_attribute):
                print("pyvisa warning: ignoring error_non_supported_attribute on get_attribute2. name: {0}, value: {1}".format(attrName, attrValue))
                StatusCode = pyvisa.constants.StatusCode.success.value
            else:
                print("viGetAttribute2: {0}, {1}".format(err.error_code, err.description))
        return StatusCode.value, attrValue

    @method(Int32,[Int32, UInt32, Int32])
    @staticmethod
    def viGetAttribute3(vi, attrName, attrValue):
        try:
            attrValue, StatusCode = PyVisa._rm.visalib.get_attribute(vi, attrName)
        except pyvisa.errors.VisaIOError as err:
            if (err.error_code == pyvisa.constants.StatusCode.error_nonsupported_attribute):
                print("pyvisa warning: ignoring error_non_supported_attribute on get_attribute3. name: {0}, value: {1}".format(attrName, attrValue))
                StatusCode = pyvisa.constants.StatusCode.success
            else:
                print("viGetAttribute3: {0}, {1}".format(err.error_code, err.description))
        return StatusCode.value, attrValue
    
    @method(Int32,[Int32, UInt32, Byte])
    @staticmethod
    def viSetAttribute1(vi, attrName, attrValue):
        try:
            StatusCode = PyVisa._rm.visalib.set_attribute(vi, attrName, attrValue)
        except pyvisa.errors.VisaIOError as err:
            if (err.error_code == pyvisa.constants.StatusCode.error_nonsupported_attribute):
                print("pyvisa warning: ignoring error_non_supported_attribute on set_attribute1. name: {0}, value: {1}".format(attrName, attrValue))
                StatusCode = pyvisa.constants.StatusCode.success
            else:
                print("viSetAttribute1: {0}, {1}".format(err.error_code, err.description))
        return StatusCode

    @method(Int32,[Int32, UInt32, Int32])
    @staticmethod
    def viSetAttribute2(vi, attrName, attrValue):
        try:
            StatusCode = PyVisa._rm.visalib.set_attribute(vi, attrName, attrValue)
        except pyvisa.errors.VisaIOError as err:
            if (err.error_code == pyvisa.constants.StatusCode.error_nonsupported_attribute):
                print("pyvisa warning: ignoring error_non_supported_attribute on set_attribute2. name: {0}, value: {1}".format(attrName, attrValue))
                StatusCode = pyvisa.constants.StatusCode.success
            else:
                print("viSetAttribute2: {0}, {1}".format(err.error_code, err.description))
        return StatusCode
            
    @method(Int32,[Int32, Int32, StringBuilder])
    @staticmethod
    def viStatusDesc(vi, status, desc):
        desc, StatusCode = PyVisa._rm.visalib.status_description(vi, status)
        return StatusCode.value, desc
        
    @method(Int32,[Int32, Int32, Int16, Int32])
    @staticmethod
    def viEnableEvent(vi, eventType, mechanism, context):
        StatusCode = PyVisa._rm.visalib.enable_event(vi, eventType, mechanism, context)
        return StatusCode 
        
    @method(Int32,[Int32, Int32, Int16])
    @staticmethod
    def viDisableEvent(vi, eventType, mechanism):
        StatusCode = PyVisa._rm.visalib.disable_event(vi, eventType, mechanism)
        return StatusCode
        
    @method(Int32,[Int32, Int32, IVisa.viEventHandler, Int32])
    @staticmethod
    def viInstallHandler(vi, eventType, handler, userHandle):
        convertedUserHandle = PyVisa._rm.visalib.install_visa_handler(vi, eventType, handler, userHandle)
        return pyvisa.constants.StatusCode.success
        
    @method(Int32,[Int32, Int32, IVisa.viEventHandler, Int32])
    @staticmethod
    def viUninstallHandler(vi, eventType, handler, userHandle):
        StatusCode = PyVisa._rm.visalib.uninstall_visa_handler(vi, eventType, handler, userHandle)
        return pyvisa.constants.StatusCode.success 
        
    @method(Int32,[Int32, ArraySegment[Byte], Int32, Int32])
    @staticmethod
    def viRead(vi, buffer, count, retCount):
        bytesBuffer, StatusCode = PyVisa._rm.visalib.read(vi, count)
        
        index = 0        
        for abyte in bytesBuffer:
            buffer.Array[index + buffer.Offset] = abyte
            index += 1

        return StatusCode.value, len(bytesBuffer)
        
    @method(Int32,[Int32, ArraySegment[Byte], Int32, Int32])
    @staticmethod
    def viWrite(vi, buffer, count, retCount):
        byteBuffer = Array[Byte](count)
        index = 0
        for abyte in buffer:
            byteBuffer[index] = abyte
            index += 1
        byteString = bytes(byteBuffer)
                
        retCount, StatusCode = PyVisa._rm.visalib.write(vi, byteString)
        return StatusCode.value, retCount
            
    @method(Int32,[Int32, Int16])
    @staticmethod
    def viReadSTB(vi, status):
        status, StatusCode = PyVisa._rm.visalib.read_stb(vi)
        return StatusCode.value, status
        
    @method(Int32,[Int32])
    @staticmethod
    def viClear(vi):
        StatusCode = PyVisa._rm.visalib.clear(vi)
        return StatusCode
        
    @method(Int32,[Int32, Int32, Int32, String, StringBuilder])
    @staticmethod
    def viLock(vi, lockType, timeout, requestedKey, accessKey):
        accessKey, StatusCode = PyVisa._rm.visalib.lock(vi, lockType, timeout, requestedKey)
        return StatusCode.value, accessKey
        
    @method(Int32,[Int32])
    @staticmethod
    def viUnlock(vi):
        StatusCode = PyVisa._rm.visalib.unlock(vi)
        return StatusCode

@attribute(OpenTap.Display("PythonVisa Settings", "Customize the behavior of PythonVisa"))
class PyVisaSettings(OpenTap.ComponentSettings):
    def __init__(self):
        super().__init__()
    LoadFirst = property(Boolean, False)\
        .add_attribute(OpenTap.Display("Load PythonVisa before the standard VISA libraries on the system"))
    Backend = property(String, '@py')\
        .add_attribute(OpenTap.Display("pyvisa backend to use"))

class PyVisaProvider(OpenTap.IVisaProvider, OpenTap.ITapPlugin):
    def __init__(self):
        _self = self

    _visa = OpenTap.IVisa(PyVisa())
    Order = property(Double, 9999 if OpenTap.ComponentSettings.GetCurrent(PyVisaSettings).LoadFirst == True else 10001)
    Visa = property(OpenTap.IVisa, _visa)

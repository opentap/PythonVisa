"""
 Passthrough I/O to pyvisa
"""
from System import String, Int32, Int16, Byte, UInt32, ArraySegment
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
    _log = OpenTap.Log.CreateSource("PyVisa")

    @method(Int32,[Int32]) 
    @staticmethod
    def viOpenDefaultRM(sesn):  
        print("TRACE: viOpenDefaultRM")
        PyVisa._rm = pyvisa.ResourceManager('@py')
        PyVisa._rm.visalib.issue_warning_on = {}
        print("DEBUG: viOpenDefaultRM: session: {0}".format(PyVisa._rm.session))
        return 0, PyVisa._rm.session  
        
        
    @method(Int32,[Int32, String, Int32, Int32, StringBuilder])
    @staticmethod
    def viFindRsrc(sesn, expr, vi, retCount, desc):
        print("TRACE: viFindRsrc")
        
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
        print("TRACE: viFindNext")
        
        #TODO: implement this
        return pyvisa.constants.StatusCode.error_resource_not_found, ""
        
    @method(Int32,[Int32, String, Int16, Int16])
    @staticmethod
    def viParseRsrc(sesn, desc, intfType, intfNum):
        print("TRACE: viParseRsrc")
        
        intfType = 0
        intfNum = 0
        resourceInfo, statusCode = PyVisa._rm.visalib.parse_resource(sesn, desc)
        intfType = resourceInfo.interface_type
        intfNum = resourceInfo.interface_board_number
        
        return StatusCode.value, intfType, intfNum
        
    @method(Int32,[Int32, String, Int16, Int16, StringBuilder, StringBuilder, StringBuilder])
    @staticmethod
    def viParseRsrcEx(sesn, desc, intfType, intfNum, rsrcClass, expandedUnaliasedName, aliasIfExists):
        print("TRACE: viParseRsrcEx")
        
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
        print("TRACE: viOpen")
        
        vi, StatusCode = PyVisa._rm.visalib.open(sesn, viDesc, mode, timeout)
        if (StatusCode == pyvisa.highlevel.StatusCode.success):
            PyVisa._connections[str(vi)] = {'rm': sesn, 'address': viDesc}
        print("DEBUG: viOpen(sesn: {0}, viDesc: {1}, mode: {2}, timeout: {3}, vi: {4}): {5}".format(sesn, viDesc, mode, timeout, vi, StatusCode.value))
        return StatusCode.value, vi
        
    @method(Int32,[Int32])
    @staticmethod
    def viClose(vi):
        print("TRACE: viClose")
        
        StatusCode = PyVisa._rm.visalib.close(vi)
        return StatusCode.value
        
    @method(Int32,[Int32, UInt32, Byte])
    @staticmethod
    def viGetAttributeDelegate1(vi, attrName, attrValue):
        print("TRACE: viGetAttributeDelegate1({0}, {1})".format(vi, attrName))
        try:
            attrValue, StatusCode = PyVisa._rm.visalib.get_attribute(vi, attrName)
        except pyvisa.errors.VisaIOError as err:
            if (err.error_code == pyvisa.constants.StatusCode.error_nonsupported_attribute):
                print("pyvisa warning: ignoring error_non_supported_attribute on get_attribute1. name: {0}, value: {1}".format(attrName, attrValue))
                StatusCode = pyvisa.constants.StatusCode.success
            else:
                print("viGetAttributeDelegate1: {0}, {1}".format(err.error_code, err.description))
        return StatusCode.value, attrValue

    @method(Int32,[Int32, Int32, StringBuilder])
    @staticmethod
    def viGetAttributeDelegate2(vi, attrName, attrValue):
        print("TRACE: viGetAttributeDelegate2({0}, {1})".format(vi, attrName))
        
        try:
            if (attrName == -1073807359 and str(vi) in PyVisa._connections):#VI_ATTR_RSRC_CLASS
                resourceInfo, statusCode = PyVisa._rm.visalib.parse_resource_extended(PyVisa._connections[str(vi)]['rm'], PyVisa._connections[str(vi)]['address'])
                print("DEBUG: VI_ATTR_RSRC_CLASS: code: {0}, value: {1}".format(str(pyvisa.constants.StatusCode.success.value), resourceInfo.resource_class))
                attrValue.Append(resourceInfo.resource_class)
                return pyvisa.constants.StatusCode.success.value
            else:
                attrValue, StatusCode = PyVisa._rm.visalib.get_attribute(vi, attrName)
        except pyvisa.errors.VisaIOError as err:
            if (err.error_code == pyvisa.constants.StatusCode.error_nonsupported_attribute):
                if (attrName == -1073807359 and str(vi) in PyVisa._connections):#VI_ATTR_RSRC_CLASS
                    resourceInfo, statusCode = PyVisa._rm.visalib.parse_resource_extended(PyVisa._connections[str(vi)]['rm'], PyVisa._connections[str(vi)]['address'])
                    print("DEBUG: VI_ATTR_RSRC_CLASS: code: {0}, value: {1}".format(str(pyvisa.constants.StatusCode.success.value), resourceInfo.resource_class))
                    return pyvisa.constants.StatusCode.success.value, resourceInfo.resource_class
                else:
                    print("pyvisa warning: ignoring error_non_supported_attribute on get_attribute2. name: {0}, value: {1}".format(attrName, attrValue))
                    StatusCode = pyvisa.constants.StatusCode.success.value
            else:
                print("viGetAttributeDelegate2: {0}, {1}".format(err.error_code, err.description))
        return StatusCode.value, attrValue

    @method(Int32,[Int32, UInt32, Int32])
    @staticmethod
    def viGetAttributeDelegate3(vi, attrName, attrValue):
        print("TRACE: viGetAttributeDelegate3({0}, {1})".format(vi, attrName))

        try:
            attrValue, StatusCode = PyVisa._rm.visalib.get_attribute(vi, attrName)
        except pyvisa.errors.VisaIOError as err:
            if (err.error_code == pyvisa.constants.StatusCode.error_nonsupported_attribute):
                print("pyvisa warning: ignoring error_non_supported_attribute on get_attribute3. name: {0}, value: {1}".format(attrName, attrValue))
                StatusCode = pyvisa.constants.StatusCode.success
            else:
                print("viGetAttributeDelegate3: {0}, {1}".format(err.error_code, err.description))
        return StatusCode.value, attrValue
    
    @method(Int32,[Int32, UInt32, Byte])
    @staticmethod
    def viSetAttributeDelegate1(vi, attrName, attrValue):
        print("TRACE: viSetAttributeDelegate1({0}, {1}, {2})".format(vi, attrName, attrValue))
        
        try:
            StatusCode = PyVisa._rm.visalib.set_attribute(vi, attrName, attrValue)
        except pyvisa.errors.VisaIOError as err:
            if (err.error_code == pyvisa.constants.StatusCode.error_nonsupported_attribute):
                print("pyvisa warning: ignoring error_non_supported_attribute on set_attribute1. name: {0}, value: {1}".format(attrName, attrValue))
                StatusCode = pyvisa.constants.StatusCode.success
            else:
                print("viSetAttributeDelegate1: {0}, {1}".format(err.error_code, err.description))
        return StatusCode

    @method(Int32,[Int32, UInt32, Int32])
    @staticmethod
    def viSetAttributeDelegate2(vi, attrName, attrValue):
        print("TRACE: viSetAttributeDelegate2({0}, {1}, {2})".format(vi, attrName, attrValue))
        
        try:
            StatusCode = PyVisa._rm.visalib.set_attribute(vi, attrName, attrValue)
        except pyvisa.errors.VisaIOError as err:
            if (err.error_code == pyvisa.constants.StatusCode.error_nonsupported_attribute):
                print("pyvisa warning: ignoring error_non_supported_attribute on set_attribute2. name: {0}, value: {1}".format(attrName, attrValue))
                StatusCode = pyvisa.constants.StatusCode.success
            else:
                print("viSetAttributeDelegate2: {0}, {1}".format(err.error_code, err.description))
        return StatusCode
            
    @method(Int32,[Int32, Int32, StringBuilder])
    @staticmethod
    def viStatusDesc(vi, status, desc):
        print("TRACE: viStatusDesc")
        
        desc, StatusCode = PyVisa._rm.visalib.status_description(vi, status)
        return StatusCode.value, desc
        
    @method(Int32,[Int32, Int32, Int16, Int32])
    @staticmethod
    def viEnableEvent(vi, eventType, mechanism, context):
        print("TRACE: viEnableEvent")
        
        StatusCode = PyVisa._rm.visalib.enable_event(vi, eventType, mechanism, context)
        return StatusCode 
        
    @method(Int32,[Int32, Int32, Int16])
    @staticmethod
    def viDisableEvent(vi, eventType, mechanism):
        print("TRACE: viDisableEvent")
        
        StatusCode = PyVisa._rm.visalib.disable_event(vi, eventType, mechanism)
        return StatusCode
        
    @method(Int32,[Int32, Int32, IVisa.viEventHandler, Int32])
    @staticmethod
    def viInstallHandler(vi, eventType, handler, userHandle):
        print("TRACE: viInstallHandler")
        
        convertedUserHandle = PyVisa._rm.visalib.install_visa_handler(vi, eventType, handler, userHandle)
        return pyvisa.constants.StatusCode.success
        
    @method(Int32,[Int32, Int32, IVisa.viEventHandler, Int32])
    @staticmethod
    def viUninstallHandler(vi, eventType, handler, userHandle):
        print("TRACE: viUninstallHandler")
        
        StatusCode = PyVisa._rm.visalib.uninstall_visa_handler(vi, eventType, handler, userHandle)
        return pyvisa.constants.StatusCode.success 
        
    @method(Int32,[Int32, ArraySegment[Byte], Int32, Int32])
    @staticmethod
    def viRead(vi, buffer, count, retCount):
        print("TRACE: viRead")
                
        bytesBuffer, StatusCode = PyVisa._rm.visalib.read(vi, count)
        
        index = 0        
        for abyte in bytesBuffer:
            buffer.Array[index + buffer.Offset] = abyte
            index += 1

        return StatusCode.value, len(bytesBuffer)
        
    @method(Int32,[Int32, ArraySegment[Byte], Int32, Int32])
    @staticmethod
    def viWrite(vi, buffer, count, retCount):
        print("TRACE: viWrite")

        # I don't like this        
        byteBuffer = Array[Byte](count)
        index = 0
        for abyte in buffer:
            byteBuffer[index] = abyte
            index += 1
        byteString = bytes(byteBuffer)
        # end dislike      
                
        retCount, StatusCode = PyVisa._rm.visalib.write(vi, byteString)
        return StatusCode.value, retCount
            
    @method(Int32,[Int32, Int16])
    @staticmethod
    def viReadSTB(vi, status):
        print("TRACE: viReadSTB")
        
        status, StatusCode = PyVisa._rm.visalib.read_stb(vi)
        return StatusCode.value, status
        
    @method(Int32,[Int32])
    @staticmethod
    def viClear(vi):
        print("TRACE: viClear")
        
        StatusCode = PyVisa._rm.visalib.clear(vi)
        return StatusCode
        
    @method(Int32,[Int32, Int32, Int32, String, StringBuilder])
    @staticmethod
    def viLock(vi, lockType, timeout, requestedKey, accessKey):
        print("TRACE: viLock")
        
        accessKey, StatusCode = PyVisa._rm.visalib.lock(vi, lockType, timeout, requestedKey)
        return StatusCode.value, accessKey
        
    @method(Int32,[Int32])
    @staticmethod
    def viUnlock(vi):
        print("TRACE: viUnlock")
        
        StatusCode = PyVisa._rm.visalib.unlock(vi)
        return StatusCode

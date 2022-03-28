"""Aqara device api."""
from __future__ import annotations
# import resource
import json
import time
from abc import ABCMeta, abstractclassmethod
from types import SimpleNamespace
from typing import Any
# , Literal, Optional
# from xml.sax.xmlreader import AttributesImpl
# from turtle import up


from .openapi import AqaraOpenAPI
from .openlogging import logger
from .openmq import AqaraOpenMQ
from .aqara_enums import PATH_OPEN_API


class ValueConvertExpression(SimpleNamespace):
    """Aqara point value convert function.
    Attributes:
        desc(str): function's description
        name(str): function's name
        type(str): function's type, which may be Boolean, Integer, Float, String
        values(dict): function's value 
    
    eg:
    express = "4+int(square(value))"
    eval(express, {'value':'6'},locals()) 
    """
    def __init__(self, desc : str, name : str, type : str,express:str):
        self.desc = desc
        self.name = name
        self.type = type
        self.express = express

    desc: str
    name: str
    type: str
    express: str   

    def get_value(self, input_vaule : str):
        output_value =  eval(self.express, {'value':input_vaule})
        if type == "Boolean":
            return self.is_true(output_value) 
        elif type == "Integer":
            return int(output_value)
        elif type == "String":
            return str(output_value)
        elif type == "Float":
            return float(output_value)
        return ""

    def square(value):
        return str(float(value)*float(value))

    def is_true(value):
        return value == '1' or value == "true" or 'value' == 'True'


class ValueRange(SimpleNamespace):
    """Aqara point's value range.

    Attributes:
        type(str):value's type, which may be Boolean, Integer, Enum, Json
        min_value: min value
        max_value: max value
    """
    def __init__(self, type:str, min_value : str, max_value : str, step_scaled:str):
        self.type = type
        self.min_value = min_value
        self.max_value = max_value
        self.step_scaled = step_scaled

    values: str
    # type: str
    # max_value: str
    # min_value: str
    # step_scaled : str





class AqaraPoint(SimpleNamespace):
    """Aqara Device.

    Attributes:
          id: point id
          name: point name
          online: Online status of the point
          icon: point icon
          update_time: The update time of point status

          status: Status set of the point
          function: Instruction set of the point
          status_range: Status value range set of the point
    """
    def __init__(self, device_id, point_id,resource_id,name, icon, update_time):
        self.id = point_id
        self.did = device_id
        self.name = name
        self.icon = icon
        self.update_time = update_time
        self.resource_id = resource_id
        self.value : Any = "0"
        self.expression :ValueConvertExpression = None
        self.value_range:  ValueRange = None
        self.hass_component: str  = None   #通过这个知道是哪种组件。 需要。
        self.proto_mapping : str  = None   #json 字符串，homeassistant 内部自己解析，并创建映射的点。
        self.position_name : str = ""
        self.position_id :str = ""

        
    # id: str #id = eg: subject_id + __ + 4.1  //.85                 resource_id
    # did : str  #device id
    # name: str
    # icon: str
    # update_time: int
    # resource_id: str
    # # position_name: str #"默认房间",
    # # position_id:   str  #  ": "real2.768799734306242560",
    # # parent_position_id: str # "real1.768799734012641280"

    # value: Any




    def __eq__(self, other):
        """If point are the same one."""
        return self.id == other.id

    def is_online(self) -> bool:
        # query AqaraDeviceInfo.state
        return True
    
    def model(self):
        return ""
    
    def get_value(self) -> str:
        return self.value



class AqaraDevice(SimpleNamespace) :
    """ AqaraDeviceInfo.

        名称    	    类型	    描述
        did	            String	    设备id
        parentDid	    String	    网关id
        positionId	    String	    位置id
        createTime	    String	    入网时间
        updateTime	    String	    更新时间
        model	        String	    物模型
        modelType	    Int	        1:可挂子设备的网关;2:不可挂子设备的网关;3:子设备
        state	        Integer	    在线状态; 0-离线 1-在线
        firmwareVersion	String	    固件版本号
        deviceName	    String	    设备名称
        timeZone	    String	    时区
    """

    def __init__(self, device_info, point_res_names: list, mgr: AqaraDeviceManager):
        self.did = device_info["did"]
        self.position_id = device_info["positionId"]
        self.time_zone = device_info["timeZone"]
        self.model = device_info["model"]
        self.state = device_info["state"]
        self.firmware_version = device_info["firmwareVersion"]
        self.device_name = device_info["deviceName"]
        self.create_time = int(device_info["createTime"])
        self.point_map: dict[str, AqaraPoint] = {}
        self.position_name : str = ""

        # res_names = mgr.__query_resource_name([self.did])
        mode_resource_info = mgr.model_resource_info_map.get(self.model,{})
        for item in mode_resource_info:
            resource_id = item["resourceId"]
            id = self.did + "__" + resource_id
            names = [name_item["name"] for name_item in point_res_names if name_item["resourceId"] == resource_id]
            res_name = names[0] if len(names) > 0 else "" 
            self.point_map[id] = AqaraPoint(self.did, id, resource_id,  res_name, "", int(time.time()))

    # position_id: str #"real2.730432352746111072",
    # create_time: int
    # time_zone: str #"gmt+09:00",
    # model: str #"lumi.gateway.aqhm01",
    # state: int #1,
    # firmware_version: str  #"3.2.6",
    # device_name: str #"aqara hub",
    # did: str  #"lumi.07737309957642"
    # point_map: dict[str, AqaraPoint] = {}
    # point_resource_ids : list[str]

class AqaraDeviceListener(metaclass=ABCMeta):
    """Aqara device listener."""

    @abstractclassmethod
    def update_device(self, device: AqaraPoint):
        """Update device info.

        Args:
            device(AqaraDevice): updated device info
        """
        pass

    @abstractclassmethod
    def add_device(self, device: AqaraPoint):
        """Device Added.

        Args:
            device(AqaraDevice): Device added
        """
        pass

    @abstractclassmethod
    def remove_device(self, device_id: str):
        """Device removed.

        Args:
            device_id(str): device's id which removed
        """
        pass


class AqaraDeviceManager:
    """Aqara Device Manager.

    This Manager support device control, including getting device status,
    specifications, the latest statuses, and sending commands

    """

    # def __init__(self, api: AqaraOpenAPI, mq: AqaraOpenMQ) -> None:
    def __init__(self, api: AqaraOpenAPI) -> None:
        """Aqara device manager init."""
        self.api = api
        # self.mq = mq
        self.device_manage = AqaraHomeDeviceManage(api)

        # mq.add_message_listener(self.on_message)
        # self.point_map: dict[str, str ] = {}  #pointid,device_id
        self.device_map: dict[str, AqaraDevice ] = {}
        self.device_listeners = set()
        self.model_resource_info_map : dict[str, list]  = {}

    # def __del__(self):
    #     """Remove mqtt listener after object del."""
    #     self.mq.remove_message_listener(self.on_message)

    def on_message(self, data: str):
        logger.debug(f"mq receive-> {data}")
        msg = json.loads(data)
        eventType = msg.get("eventType","")
        if eventType == "resource_report":
             self._on_device_report( msg["data"])
       

        # protocol = msg.get("protocol", 0)
        # data = msg.get("data", {})
        # if protocol == PROTOCOL_DEVICE_REPORT:
        #     self._on_device_report(data["devId"], data["status"])
        # elif protocol == PROTOCOL_OTHER:
        #     self._on_device_other(data["devId"], data["bizCode"], data)



        # openId	    String	是	用户唯一标识
        # time	    String	是	消息产生的时间戳，单位毫秒
        # eventType	String	是	事件消息通知类型，如：绑定 解绑 在线 离线
        # msgId	    String	是	消息唯一id标识
        # data	    Object	是	具体的消息内容
        # data.time	Object	是	具体的消息产生的时间戳，单位毫秒




    def __update_device(self, point: AqaraPoint):
        for listener in self.device_listeners:
            listener.update_device(point)

    def _on_device_report(self, points: list):
        # [
        #     {
        #         "subjectId":"lumi1.xxx",
        #         "resourceId":"lumi1.xxx",
        #         "value":"lumi1.xxx",
        #         "time":"1561621051609",
        #         "statusCode":0,
        #         "triggerSource":{
        #             "type":1,
        #             "time":"1561621050",
        #             "id":"AL.xxxx"
        #         }
        #     }
        # ]


        # device = self.point_map.get(device_id, None)
        # if not device:
        #     return
        # logger.debug(f"mq _on_device_report-> {status}")
        for item in points:
            if "subjectId" in item and "resourceId" in item and "value" in item:
                device = self.device_map.get(item["subjectId"], None)
                if not device:
                    continue
                point_id = item["subjectId"] + '_' + item['resourceId']
                point = device.point_map.get(point_id, None)
                point.value = item["value"]
                point.update_time = item["time"]
                self.__update_device(point)



   
    ##############################
    # Memory Cache
    def generate_devices_and_update_value(self):
        """Update devices's point present_value."""      
        self.device_map = self.__generage_devices()

        for dev_info in self.device_map.values():
            points_value = self.__query_resource_value(dev_info.did, [])
            for key in points_value.keys():
                if key in dev_info.point_map:
                    # self.point_map[key] = dev_info.did
                    dev_info.point_map[key].value = points_value.get(key,"")
            

        # self.update_device_function_cache()

    def __generage_devices(self) -> dict[str, AqaraDevice]:
        """generate devices.""" 
        return self.__query_all_device_info()

    def __get_code(self, resp) -> int :
        if resp is not None and 'code' in resp:
            return resp.get("code", -1)
        return -1


    def __query_all_device_info(self) -> dict[str, AqaraDevice] :
        """query device ids and generate device.""" 
        body = {
            "intent": "query.device.info",
            "data": {
                "dids": [],
                "positionId": "",
                "pageNum": 1,
                "pageSize": 50
            }
        }        

        def __result_handler(data):
            for item in data:
                model = item["model"]                     
                if model not in self.model_resource_info_map:
                    res_info = self.__query_resource_info(model)
                    self.model_resource_info_map[model] = res_info
                
                did = item["did"]   
                res_names = self.__query_resource_name([did])
                device_list[did] = AqaraDevice(item, res_names, self)   
        
        device_list : dict[str, AqaraDevice] = {}
        self.api.query_all_page(body, __result_handler)
        return device_list


    def __query_resource_name(self,subject_ids: list) -> list:         
        body = {
            "intent": "query.resource.name",
            "data": {
                "subjectIds": subject_ids   #设备id数组，最大可同时查询50个。
            }
        }

        resp = self.api.post(PATH_OPEN_API,body)
        if self.__get_code(resp) != 0:
            return []

        return resp.get("result")

    def __query_resource_value(self, did: str, resource_ids:list) -> dict[str, str]:
        body = {
            "intent": "query.resource.value",
            "data": {
                "resources": [
                    {
                        "subjectId": did,
                        "resourceIds": resource_ids
                    }
                ]
            }
        }
        resp = self.api.post(PATH_OPEN_API,body)
        point_value_map: dict[str,str] = {}
        if self.__get_code(resp) == 0:
            result = resp.get("result", [])
            for item in result:
                point_id = item["subjectId"] + "_" + item["resourceId"]
                point_value_map[point_id] = item["value"]

        return point_value_map
    
    def __query_resource_info(self, model :str) -> list:
        body = {
            "intent": "query.resource.info",
            "data": {
                "model": model,
                "resourceId":""
            }
        }
        resp = self.api.post(PATH_OPEN_API,body)
        if self.__get_code(resp) != 0:
            return []

        return resp.get("result", [])


    def config_mqtt_add(self) -> dict[str,str]:
        body = {
            "intent": "config.mqtt.add",
            "data": {
                "assign":""
            }
        }
        resp = self.api.post(PATH_OPEN_API,body)
        # resp = self.api.post("",body)
        if self.__get_code(resp) != 0:
            return {}

        return resp.get("result", {})
        #  {
        #     "password": "BG2FRrJTIGCaHTP4Ga2Mlfrr",
        #     "clientId": "omqt.9617f124-a3e3-45fb-8cc5-64c2017b99d5",
        #     "subscribeTopic": "receive_omqt.9617f124-a3e3-45fb-8cc5-64c2017b99d5",
        #     "mqttHost": "aiot-mqtt-test.aqara.cn",
        #     "userName": "9478646628902215681ddba4",
        #     "mqttPort": "1883",
        #     "publishTopic": "control_omqt.9617f124-a3e3-45fb-8cc5-64c2017b99d5"
        # }
    
    def get_device_model(self, device_id:str)-> str :
        device = self.device_map.get(device_id, None)
        if device is not None:
            return device.model
        return ""

    def get_device(self, device_id:str)-> AqaraDevice | None :
        device = self.device_map.get(device_id, None)
        return device
    
    def get_point(self, point_id:str)-> AqaraPoint | None :
        ids = point_id.split('__',1)
        if len(ids) == 2:
            device = self.get_device(ids[0])
            if device is not None:
                return device.point_map.get(point_id, None)
        return None

    def update_device_position_name(self, device_id:str, position_name:str) :
        device = self.get_device(device_id)
        if device is not None:
            device.position_name = position_name

    def add_device_listener(self, listener: AqaraDeviceListener):
        """Add device listener."""
        self.device_listeners.add(listener)

    def remove_device_listener(self, listener: AqaraDeviceListener):
        """Remove device listener."""
        self.device_listeners.remove(listener)

 

    def remove_device(self, device_id: str) -> dict[str, Any]:
        """Remove device.

        Args:
          device_id(str): device id

        Returns:
            response: response body
        """
        return self.device_manage.remove_device(device_id)

    def remove_device_list(self, devIds: list[str]) -> dict[str, Any]:
        """Remove devices.

        Args:
          device_id(list): device id list

        Returns:
            response: response body
        """
        return self.device_manage.remove_device_list(devIds)

    
  

  

    def send_commands(
        self, device_id: str, commands: list[dict[str, Any]]
    ) -> dict[str, Any]:

        """Send commands.

        Send command to the device.For example:
          {"commands": [{"resourceId": "4.1.85","value": "1"}]}

        Args:
          device_id(str): device id
          commands(list):  commands list

        Returns:
            response: response body
        """
        return self.device_manage.send_commands(device_id, commands)

    ##############################


class DeviceManage(metaclass=ABCMeta):
    api: AqaraOpenAPI

    def __init__(self, api: AqaraOpenAPI):
        self.api = api



    @abstractclassmethod
    def update_device_caches(self, devIds: list[str]):
        pass


    @abstractclassmethod
    def send_commands(self, device_id: str, commands: list[str]):
        pass


class AqaraHomeDeviceManage(DeviceManage):
    def update_device_caches(self, devIds: list[str]):
        pass

    def send_commands(
        self, device_id: str, commands: dict[str, str]  
    ) :
        # commands  :           dict[point_id,value]
        resources :list = []
        for resource_id, value  in commands.items():
            item = {"resourceId":resource_id, "value": value }
            resources.append(item)

        body = {
            "intent": "write.resource.device",
            "data": [{
                    "subjectId": device_id,
                    "resources": resources
                }
            ]
        }

        self.api.post(PATH_OPEN_API,body)

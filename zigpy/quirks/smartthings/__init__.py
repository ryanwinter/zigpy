import zigpy.types as t
import logging

from zigpy.profiles import PROFILES, zha
from zigpy.zcl.clusters.general import Basic, PowerConfiguration, Identify, BinaryInput, PollControl, Ota
from zigpy.zcl.clusters.measurement import TemperatureMeasurement
from zigpy.zcl.clusters.security import IasZone
from zigpy.quirks import CustomDevice, CustomCluster

_LOGGER = logging.getLogger(__name__)

class SmartthingsPowerConfigurationCluster(CustomCluster, PowerConfiguration):
    cluster_id = PowerConfiguration.cluster_id
    BATTERY_VOLTAGE_ATTR = 0x0020
    BATTERY_PERCENTAGE_REMAINING = 0x0021
    MIN_VOLTS = 15
    MAX_VOLTS = 28
    VOLTS_TO_PERCENT = {
        28: 100,
        27: 100,
        26: 100,
        25: 90,
        24: 90,
        23: 70,
        22: 70,
        21: 50,
        20: 50,
        19: 30,
        18: 30,
        17: 15,
        16: 1,
        15: 0
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _update_attribute(self, attrid, value):
        super()._update_attribute(attrid, value)
        if attrid == self.BATTERY_VOLTAGE_ATTR:
            super()._update_attribute(
                self.BATTERY_PERCENTAGE_REMAINING,
                self._calculate_battery_percentage(value)
            )

    def _calculate_battery_percentage(self, rawValue):
        volts = rawValue
        if rawValue < self.MIN_VOLTS:
            volts = self.MIN_VOLTS
        elif rawValue > self.MAX_VOLTS:
            volts = self.MAX_VOLTS

        return self.VOLTS_TO_PERCENT.get(volts, 'unknown')


class SmartthingsRelativeHumidityCluster(CustomCluster):
    cluster_id = 0xfc45
    name = 'Smartthings Relative Humidity Measurement'
    ep_attribute = 'humidity'
    attributes = {
        # Relative Humidity Measurement Information
        0x0000: ('measured_value', t.int16s),
    }
    server_commands = {}
    client_commands = {}


class SmartthingsMultiSensor(CustomDevice):
    signature = {
        1: {
            'profile': zha.PROFILE_ID,
            'device_type': zha.DeviceType.IAS_ZONE,
            'input_clusters': [ 
                Basic.cluster_id, 
                PowerConfiguration.cluster_id, 
                Identify.cluster_id, 
                BinaryInput.cluster_id, 
                PollControl.cluster_id, 
                TemperatureMeasurement.cluster_id, 
                IasZone.cluster_id, 
                64514 
            ],
            'output_clusters': [ 
                Ota.cluster_id 
            ],
        }
    }

    replacement = {
        'endpoints': {
            1: {
                'input_clusters': [
                    Basic.cluster_id, 
                    SmartthingsPowerConfigurationCluster                   
                    Identify.cluster_id, 
                    BinaryInput.cluster_id, 
                    PollControl.cluster_id, 
                    TemperatureMeasurement.cluster_id, 
                    IasZone.cluster_id, 
                    0xFC02
                ],
                'output_clusters': [
                    Ota.cluster_id
                ],
            }
        }
    }


class SmartthingsTemperatureHumiditySensor(CustomDevice):
    signature = {
        # <SimpleDescriptor endpoint=1 profile=260 device_type=770 device_version=0 input_clusters=[0, 1, 3, 32, 1026, 2821, 64581] output_clusters=[3, 25]>
        1: {
            'profile_id': 0x0104,
            'device_type': 0x0302,
            'input_clusters': [0, 1, 3, 32, 1026, 2821, 64581],
            'output_clusters': [3, 25],
        }
    }

    replacement = {
        'endpoints': {
            1: {
                'input_clusters': [0x0000, 0x0001, 0x0003, 0x0402, 0x0B05,
                                   SmartthingsRelativeHumidityCluster],
            }
        }
    }

import logging
import zigpy.types as t
from zigpy.quirks import CustomDevice, CustomCluster
from zigpy.zcl.clusters.general import ( PowerConfiguration )


class SmartthingsPowerCluster(CustomCluster, PowerConfiguration):
    """Provides battery % remaining based on voltage"""
    minVolts = 15
    maxVolts = 28
    values = {
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

    def _update_attribute(self, attrid, value):
        super()._update_attribute(attrid, value)

        attr_name = self.attributes.get(attrid, [attrid])[0]
        _LOGGER.debug("smartthings update attribute %s", attr_name)
        if attr_name == 'battery_voltage':
            _LOGGER.debug("Found battery voltage %s %s", value)

            value = min(value, self.maxVolts)
            value = max(value, self.minVolts)

            bpr = self.values.get(value, 'unknown')
            bpr_id = self._attridx.get('battery_percentage_remaining')

            super()._update_attribute(bpr_id, bpr)


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
            'profile': 0x104,
            'device_type': 0x402,
            'input_clusters': [ 0, 1, 3, 15, 32, 1026, 1280, 64514 ],
            'output_clusters': [ 25 ],
        }
    }

    replacement = {
        'endpoints': {
            1: {
                'input_clusters': [0x0000, SmartthingsPowerCluster, 0x0003, 0x000F, 0x0020, 0x0402, 0x0500, 0xFC02 ]'
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

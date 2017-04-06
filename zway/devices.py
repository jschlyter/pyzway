"""Python module for ZWay Devices"""

import logging
from zway.session import ZWaySession


_LOGGER = logging.getLogger(__name__)


class GenericDevice(object):
    def __init__(self, data: dict, zsession: ZWaySession):
        self._zsession = zsession
        self.update_attrs(data)

    def update(self) -> None:
        data = self._zsession.get("/devices/" + self.id).json().get('data')
        self.update_attrs(data)

    def update_attrs(self, data: dict) -> None:
        self._data = data
        self.id = self._data['id']
        self.title = self._data['metrics'].get('title')
        self.visible = self._data['visibility']

    def json(self):
        return self._data

    def is_tagged(self, tag: str=None) -> bool:
        if tag is not None:
            return tag in self._data.get('tags', [])
        else
            return True


class GenericBinaryDevice(GenericDevice):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def update_attrs(self, data: dict):
        super().update_attrs(data)
        if data['metrics']['level'] == 'on':
            self._state = True
        elif data['metrics']['level'] == 'off':
            self._state = False
        else:
            self._state = None

    @property
    def state(self) -> bool:
        return self._state

    @state.setter
    def state(self, value: bool) -> None:
        if value:
            command = "on"
        else:
            command = "off"
        self._zsession.get("/devices/{}/command/{}".format(self.id, command))


class GenericMultiLevelDevice(GenericDevice):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def update_attrs(self, data: dict) -> None:
        super().update_attrs(data)
        self._level = data['metrics']['level']

    @property
    def level(self) -> int:
        return self._level

    @level.setter
    def level(self, value: int) -> None:
        self._zsession.get("/devices/{}/command/exact?level={}".format(self.id, value))


class SwitchBinary(GenericBinaryDevice):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SwitchMultilevel(GenericMultiLevelDevice):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SwitchRGBW(SwitchBinary):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def update_attrs(self, data: dict) -> None:
        super().update_attrs(data)
        self._red = data['metrics']['color']['r']
        self._green = data['metrics']['color']['g']
        self._blue = data['metrics']['color']['b']

    @property
    def rgb(self) -> None:
        return (self._red, self._green, self._blue)

    @rgb.setter
    def rgb(self, color: (int,int,int)) -> None:
        (red, green, blue) = color
        self._zsession.get("/devices/{}/command/exact?red={}&green={}&blue={}".format(self.id, red, green, blue))


class SensorBinary(GenericBinaryDevice):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SensorMultilevel(GenericMultiLevelDevice):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def update_attrs(self, data: dict) -> None:
        super().update_attrs(data)
        self._unit = data['metrics']['scaleTitle']

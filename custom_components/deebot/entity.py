"""Deebot entity module."""
from typing import Optional

from deebot_client.vacuum_bot import VacuumBot
from homeassistant.helpers.entity import DeviceInfo, Entity, EntityDescription

from . import DOMAIN


class DeebotEntity(Entity):  # type: ignore # lgtm [py/missing-equals]
    """Deebot entity."""

    _attr_should_poll = False

    def __init__(
        self,
        vacuum_bot: VacuumBot,
        entity_description: Optional[EntityDescription] = None,
    ):
        """Initialize the Sensor."""
        super().__init__()
        if entity_description:
            self.entity_description = entity_description
        elif not hasattr(self, "entity_description"):
            raise ValueError(
                '"entity_description" must be either set as class variable or passed on init!'
            )

        self._vacuum_bot: VacuumBot = vacuum_bot

        device_info = self._vacuum_bot.device_info
        self._attr_unique_id = device_info.did

        if self.entity_description.key:
            self._attr_unique_id += f"_{self.entity_description.key}"

        if self.entity_description.name:
            # Name provided, using the provided one
            return

        if device_info.nick is not None:
            device_name: str = device_info.nick
        else:
            # In case there is no nickname defined, use the device id
            device_name = device_info.did

        self._attr_name = f"{device_name}_{self.entity_description.key}"

    @property
    def device_info(self) -> Optional[DeviceInfo]:
        """Return device specific attributes."""
        device = self._vacuum_bot.device_info
        info = {
            "default_name": "Deebot vacuum",
            "identifiers": {(DOMAIN, device.did)},
            "manufacturer": "Ecovacs",
            "sw_version": self._vacuum_bot.fw_version,
        }

        if "nick" in device:
            info["name"] = device["nick"]

        if "deviceName" in device:
            info["model"] = device["deviceName"]

        return info

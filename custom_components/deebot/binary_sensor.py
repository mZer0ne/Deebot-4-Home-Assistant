"""Binary sensor module."""
import logging
from typing import Optional

from deebot_client.events import WaterInfoEvent
from deebot_client.events.event_bus import EventListener
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ENTITY_CATEGORY_DIAGNOSTIC
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import DeebotEntity
from .hub import DeebotHub

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add entities for passed config_entry in HA."""
    hub: DeebotHub = hass.data[DOMAIN][config_entry.entry_id]

    new_devices = []
    for vacbot in hub.vacuum_bots:
        new_devices.append(DeebotMopAttachedBinarySensor(vacbot))

    if new_devices:
        async_add_entities(new_devices)


class DeebotMopAttachedBinarySensor(DeebotEntity, BinarySensorEntity):  # type: ignore
    """Deebot mop attached binary sensor."""

    entity_description = BinarySensorEntityDescription(
        key="mop_attached",
        entity_registry_enabled_default=False,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    )

    @property
    def icon(self) -> Optional[str]:
        """Return the icon to use in the frontend, if any."""
        return "mdi:water" if self.is_on else "mdi:water-off"

    async def async_added_to_hass(self) -> None:
        """Set up the event listeners now that hass is ready."""
        await super().async_added_to_hass()

        async def on_event(event: WaterInfoEvent) -> None:
            self._attr_is_on = event.mop_attached
            self.async_write_ha_state()

        listener: EventListener = self._vacuum_bot.events.subscribe(
            WaterInfoEvent, on_event
        )
        self.async_on_remove(listener.unsubscribe)

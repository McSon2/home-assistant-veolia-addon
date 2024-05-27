import logging
from homeassistant.helpers.typing import ConfigType, HomeAssistantType

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistantType, config: ConfigType) -> bool:
    return True

async def async_setup_entry(hass: HomeAssistantType, entry) -> bool:
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True

async def async_unload_entry(hass: HomeAssistantType, entry) -> bool:
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    return True

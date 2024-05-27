import logging
from datetime import timedelta

from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import UnitOfVolume
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .veolia_client import VeoliaClient  # Assurez-vous que la casse est correcte

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities):
    email = config_entry.data["username"]
    password = config_entry.data["password"]
    abo_id = config_entry.data.get("abo_id")

    session = async_get_clientsession(hass)
    client = VeoliaClient(email, password, session, abo_id)
    coordinator = VeoliaDataUpdateCoordinator(hass, client=client)

    await coordinator.async_refresh()
    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    async_add_entities([VeoliaWaterSensor(coordinator)], True)

class VeoliaWaterSensor(SensorEntity):
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_name = "Veolia Water Consumption"
        self._attr_device_class = "water"
        self._attr_state_class = "total_increasing"
        self._attr_unit_of_measurement = UnitOfVolume.CUBIC_METERS

    @property
    def state(self):
        return self.coordinator.data.get("last_index")

    @property
    def extra_state_attributes(self):
        return self.coordinator.data

    async def async_update(self):
        await self.coordinator.async_request_refresh()

class VeoliaDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, client):
        self.client = client
        super().__init__(
            hass,
            _LOGGER,
            name="Veolia water consumption",
            update_interval=timedelta(hours=1),
        )

    async def _async_update_data(self):
        try:
            return await self.hass.async_add_executor_job(self.client.update_all)
        except Exception as e:
            raise UpdateFailed(f"Error fetching data: {e}")

import logging
from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import UnitOfVolume
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from datetime import timedelta

from .const import DOMAIN
from .veolia_client import VeoliaClient

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    email = config_entry.data["email"]
    password = config_entry.data["password"]
    abo_id = config_entry.data.get("abo_id")

    client = VeoliaClient(email, password, abo_id)
    coordinator = VeoliaDataUpdateCoordinator(hass, client=client)

    await coordinator.async_config_entry_first_refresh()
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
            return self.client.update_all()
        except Exception as e:
            raise UpdateFailed(f"Error fetching data: {e}")

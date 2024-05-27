"""Sensor platform for Veolia."""

import logging
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from .const import DAILY, DOMAIN, HISTORY, MONTHLY
from .debug import decoratorexceptionDebug
from .entity import VeoliaEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    sensors = [
        VeoliaDailyUsageSensor(coordinator, entry),
        VeoliaMonthlyUsageSensor(coordinator, entry),
        VeoliaLastIndexSensor(coordinator, entry),
    ]
    async_add_devices(sensors)


class VeoliaLastIndexSensor(VeoliaEntity):
    """Monitors the last index."""

    @property
    def name(self):
        """Return the name of the sensor."""
        return "veolia_last_index"

    @property
    def state_class(self):
        """Return the state_class of the sensor."""
        return SensorStateClass.TOTAL_INCREASING

    @property
    def device_class(self):
        """Return the device_class of the sensor."""
        return SensorDeviceClass.WATER

    @property
    def unit_of_measurement(self):
        """Return the unit_of_measurement of the sensor."""
        return "m³"

    @property
    @decoratorexceptionDebug
    def state(self):
        """Return the state of the sensor."""
        state = self.coordinator.data["last_index"]
        if state > 0:
            return state
        return None

    @property
    @decoratorexceptionDebug
    def extra_state_attributes(self):
        """Return the extra state attributes."""
        return self._base_extra_state_attributes()


class VeoliaDailyUsageSensor(VeoliaEntity):
    """Monitors the daily water usage."""

    @property
    def name(self):
        """Return the name of the sensor."""
        return "veolia_daily_consumption"

    @property
    def state_class(self):
        """Return the state_class of the sensor."""
        return SensorStateClass.TOTAL_INCREASING

    @property
    def device_class(self):
        """Return the device_class of the sensor."""
        return SensorDeviceClass.WATER

    @property
    def unit_of_measurement(self):
        """Return the unit_of_measurement of the sensor."""
        return "m³"

    @property
    @decoratorexceptionDebug
    def state(self):
        """Return the state of the sensor."""
        state = self.coordinator.data[DAILY][HISTORY][0][1]
        if state > 0:
            return state
        return None

    @property
    @decoratorexceptionDebug
    def extra_state_attributes(self):
        """Return the extra state attributes."""
        attrs = self._base_extra_state_attributes() | {
            "historyConsumption": self.coordinator.data[DAILY][HISTORY],
        }
        return attrs


class VeoliaMonthlyUsageSensor(VeoliaEntity):
    """Monitors the monthly water usage."""

    @property
    def name(self):
        """Return the name of the sensor."""
        return "veolia_monthly_consumption"

    @property
    def state_class(self):
        """Return the state_class of the sensor."""
        return SensorStateClass.TOTAL_INCREASING

    @property
    def device_class(self):
        """Return the device_class of the sensor."""
        return SensorDeviceClass.WATER

    @property
    def unit_of_measurement(self):
        """Return the unit_of_measurement of the sensor."""
        return "m³"

    @property
    def state(self):
        """Return the state of the sensor."""
        state = self.coordinator.data[MONTHLY][HISTORY][0][1]
        if state > 0:
            return state
        return None

    @property
    @decoratorexceptionDebug
    def extra_state_attributes(self):
        """Return the extra state attributes."""
        attrs = self._base_extra_state_attributes() | {
            "historyConsumption": self.coordinator.data[MONTHLY][HISTORY],
        }
        return attrs

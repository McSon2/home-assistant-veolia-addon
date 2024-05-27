import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

@config_entries.HANDLERS.register(DOMAIN)
class VeoliaWaterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            email = user_input.get("email")
            password = user_input.get("password")
            abo_id = user_input.get("abo_id")

            return self.async_create_entry(title="Veolia Water", data=user_input)

        data_schema = vol.Schema({
            vol.Required("email"): str,
            vol.Required("password"): str,
            vol.Optional("abo_id"): str,
        })
        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return VeoliaWaterOptionsFlowHandler(config_entry)

class VeoliaWaterOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data_schema = vol.Schema({
            vol.Required("email", default=self.config_entry.data.get("email")): str,
            vol.Required("password", default=self.config_entry.data.get("password")): str,
            vol.Optional("abo_id", default=self.config_entry.data.get("abo_id")): str,
        })
        return self.async_show_form(
            step_id="init",
            data_schema=data_schema
        )

"""Config flow for Tibber Future Prices."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN

class TibberFuturePricesConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tibber Future Prices."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""

        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            return self.async_create_entry(title="Tibber Future Prices", data={})

        return self.async_show_form(step_id="user")

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""

        return config_entries.OptionsFlow()

import voluptuous as vol
from homeassistant import config_entries
from collections import OrderedDict
from sampleclient.client import Client
from .const import DOMAIN

@config_entries.HANDLERS.register(DOMAIN)
class GarbageCollectionFlowHandler(config_entries.ConfigFlow):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self):
        """Initialize."""
        self._errors = {}

    async def async_step_user(
        self, user_input={}
    ):  # pylint: disable=dangerous-default-value
        """Handle a flow initialized by the user."""
        self._errors = {}
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        if self.hass.data.get(DOMAIN):
            return self.async_abort(reason="single_instance_allowed")
        if user_input is not None:
            if "frequency" in user_input:
                return self.async_create_entry(title="", data=user_input)
            else:
                self._errors["base"] = "auth"
            return await self._show_config_form(user_input)
        return await self._show_config_form(user_input)

    async def _show_config_form(self, user_input):
        """Show the configuration form to edit location data."""
        # Defaults
        frequency = ""

        if user_input is not None:
            if "frequency" in user_input:
                frequency = user_input["frequency"]

        data_schema = OrderedDict()
        data_schema[vol.Required("frequency", default=frequency)] = str
        return self.async_show_form(
            step_id="user", data_schema=vol.Schema(data_schema), errors=self._errors
        )

    async def async_step_import(self, user_input):  # pylint: disable=unused-argument
        """Import a config entry.
        Special type of import, we're not actually going to store any data.
        Instead, we're going to rely on the values that are in config file.
        """
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        return self.async_create_entry(title="configuration.yaml", data={})

    async def _test_credentials(self, username, password):
        """Return true if credentials is valid."""
        try:
            client = Client(username, password)
            client.get_data()
            return True
        except Exception:  # pylint: disable=broad-except
            pass
        return False

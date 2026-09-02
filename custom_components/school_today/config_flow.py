from homeassistant import config_entries
import voluptuous as vol


DOMAIN = "school_today"


class SchoolTodayConfigFlow(
    config_entries.ConfigFlow,
    domain=DOMAIN
):
    """Config flow for School Today."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""

        if user_input is not None:
            return self.async_create_entry(
                title="School Today",
                data=user_input,
            )

        schema = vol.Schema({
            vol.Required("api_url"): str
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema
        )
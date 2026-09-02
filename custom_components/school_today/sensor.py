from homeassistant.components.sensor import SensorEntity
from homeassistant.const import UnitOfCount
from homeassistant.helpers.aiohttp_client import async_get_clientsession


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up School Today sensor."""

    api_url = entry.data["api_url"]

    async_add_entities([
        SchoolTodayMenuSensor(api_url)
    ])


class SchoolTodayMenuSensor(SensorEntity):
    """School Today menu sensor."""

    _attr_name = "School Today Menu"
    _attr_native_unit_of_measurement = UnitOfCount

    def __init__(self, api_url):
        self.api_url = api_url
        self._attr_native_value = 0
        self._attr_should_poll = True

    async def async_added_to_hass(self):
        """Called when the entity is added to Home Assistant."""

        await super().async_added_to_hass()

        self.session = async_get_clientsession(self.hass)

    async def async_update(self):
        """Update sensor."""

        async with self.session.get(
            f"{self.api_url}/menu"
        ) as response:
            data = await response.json()

        self._attr_native_value = len(data)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant


DOMAIN = "school_today"


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up School Today."""

    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Set up School Today from a config entry."""

    await hass.config_entries.async_forward_entry_setups(
        entry,
        ["sensor"],
    )

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Unload School Today config entry."""

    return await hass.config_entries.async_unload_platforms(
        entry,
        ["sensor"],
    )
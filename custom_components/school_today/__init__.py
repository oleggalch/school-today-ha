import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.exceptions import HomeAssistantError


DOMAIN = "school_today"

_LOGGER = logging.getLogger(__name__)


async def async_setup(
    hass: HomeAssistant,
    config: dict,
) -> bool:
    """Set up School Today."""

    async def handle_get_menu(call: ServiceCall) -> ServiceResponse:
        """Handle get menu service."""

        date = call.data.get("date")
        meal = call.data.get("meal")

        _LOGGER.warning(
            "School Today input: date=%r (%s), meal=%r (%s)",
            date,
            type(date).__name__,
            meal,
            type(meal).__name__,
        )

        sensor = hass.states.get("sensor.school_today_menu")

        if sensor is None:
            raise HomeAssistantError(
                "School Today sensor not found"
            )

        menu = sensor.attributes.get("menu", [])

        _LOGGER.warning(
            "School Today menu: %d days",
            len(menu),
        )

        result = []

        for day in menu:
            if day.get("date") != date:
                continue

            for meal_data in day.get("meals", []):
                if meal_data.get("name") != meal:
                    continue

                for dish in meal_data.get("dishes", []):
                    result.append(dish.get("name"))

        response = ", ".join(result)

        _LOGGER.warning(
            "School Today result: %s",
            response,
        )

        return {
            "response": response,
            "date": date,
            "meal": meal,
        }

    if not hass.services.has_service(DOMAIN, "get_menu"):
        hass.services.async_register(
            DOMAIN,
            "get_menu",
            handle_get_menu,
            supports_response=SupportsResponse.ONLY,
        )

    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Set up School Today config entry."""

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

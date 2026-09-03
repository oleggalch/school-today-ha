import logging

import voluptuous as vol

from homeassistant.components import llm
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.llm import LLMContext, ToolInput
from homeassistant.util.json import JsonObjectType


DOMAIN = "school_today"

_LOGGER = logging.getLogger(__name__)


class SchoolTodayMenuTool(llm.Tool):
    """Tool for getting school menu."""

    name = "SchoolTodayMenu"

    description = (
        "Получить меню школы на указанную дату и приём пищи. "
        "Используй этот инструмент, когда пользователь спрашивает, "
        "что будет в школе на завтрак или обед. "
        "Дата должна быть в формате YYYY-MM-DD. "
        "Приём пищи: завтрак или обед."
    )

    parameters = vol.Schema({
        vol.Optional(
            "date",
            description="Дата меню в формате YYYY-MM-DD.",
        ): str,
        vol.Required(
            "meal",
            description="Приём пищи: завтрак или обед.",
        ): str,
    })

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: ToolInput,
        llm_context: LLMContext,
    ) -> JsonObjectType:
        """Call the school menu tool."""

        date = tool_input.tool_args.get("date")
        meal = tool_input.tool_args.get("meal")

        if not date:
            from datetime import datetime

            date = datetime.now().date().isoformat()

        meal_lower = meal.lower().strip()

        meal_map = {
            "обед": "Обід",
            "обіду": "Обід",
            "обід": "Обід",
            "завтрак": "Сніданок",
            "сніданок": "Сніданок",
        }

        meal_name = meal_map.get(meal_lower, meal)

        _LOGGER.warning(
            "School Today LLM tool: date=%r, meal=%r",
            date,
            meal_name,
        )

        sensor = hass.states.get("sensor.school_today_menu")

        if sensor is None:
            return {
                "error": "Меню школы сейчас недоступно."
            }

        menu = sensor.attributes.get("menu", [])

        for day in menu:
            if day.get("date") != date:
                continue

            for meal_data in day.get("meals", []):
                if meal_data.get("name") != meal_name:
                    continue

                dishes = [
                    dish.get("name")
                    for dish in meal_data.get("dishes", [])
                    if dish.get("name")
                ]

                if not dishes:
                    return {
                        "date": date,
                        "meal": meal_name,
                        "menu": "На этот приём пищи блюд нет.",
                    }

                return {
                    "date": date,
                    "meal": meal_name,
                    "menu": ", ".join(dishes),
                }

        return {
            "date": date,
            "meal": meal_name,
            "menu": "Меню на указанную дату или приём пищи не найдено.",
        }


@callback
def async_get_tools(
    hass: HomeAssistant,
    llm_context: LLMContext,
    api_id: str,
) -> llm.LLMTools | None:
    """Return School Today tools."""

    return llm.LLMTools(
        tools=[SchoolTodayMenuTool()],
        prompt=(
            "Если пользователь спрашивает о школьном меню, "
            "используй SchoolTodayMenu. "
            "Не придумывай блюда самостоятельно."
        ),
    )

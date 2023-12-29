import voluptuous as vol
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv, event
from homeassistant.components.climate.const import ATTR_CURRENT_TEMPERATURE
import logging

_LOGGER = logging.getLogger(__name__)

DOMAIN = "temperature-sync"
CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required("pairs"): vol.All(cv.ensure_list, [{
            vol.Required("sensor"): cv.entity_id,
            vol.Required("climate"): cv.entity_id,
        }]),
    })
}, extra=vol.ALLOW_EXTRA)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Temperature Sync component."""
    sensor_to_climate_map = {pair["sensor"]: pair["climate"] for pair in config[DOMAIN]["pairs"]}
    climate_to_sensor_map = {pair["climate"]: pair["sensor"] for pair in config[DOMAIN]["pairs"]}

    async def handle_temperature_change(event):
        """Handle the temperature change."""
        entity_id = event.data.get('entity_id')
        new_state = event.data.get('new_state')

        if new_state is None or new_state.state in ['unavailable', 'unknown']:
            return

        try:
            new_temperature = float(new_state.state)
        except ValueError:
            _LOGGER.error("State of %s is not a valid temperature: %s", entity_id, new_state.state)
            return

        climate_entity_id = sensor_to_climate_map.get(entity_id)
        if climate_entity_id:
            climate_state = hass.states.get(climate_entity_id)
            if climate_state:
                attributes = dict(climate_state.attributes)
                attributes[ATTR_CURRENT_TEMPERATURE] = new_temperature
                # Using async_set instead of hass.states.set
                hass.states.async_set(climate_entity_id, climate_state.state, attributes)

    async def handle_climate_change(event):
        """Handle the climate change, specifically looking for lost current_temperature."""
        entity_id = event.data.get('entity_id')
        new_state = event.data.get('new_state')

        if entity_id not in climate_to_sensor_map:
            return

        sensor_entity_id = climate_to_sensor_map[entity_id]
        sensor_state = hass.states.get(sensor_entity_id)

        if sensor_state is None or sensor_state.state in ['unavailable', 'unknown']:
            return

        try:
            new_temperature = float(sensor_state.state)
        except ValueError:
            _LOGGER.error("State of %s is not a valid temperature: %s", sensor_entity_id, sensor_state.state)
            return

        # Only proceed if current_temperature is missing or needs update
        if new_state.attributes.get(ATTR_CURRENT_TEMPERATURE) is None:
            attributes = dict(new_state.attributes)
            attributes[ATTR_CURRENT_TEMPERATURE] = new_temperature
            hass.states.async_set(entity_id, new_state.state, attributes)

    # Track state changes for the specified sensors and climate entities
    for sensor_entity_id, climate_entity_id in sensor_to_climate_map.items():
        event.async_track_state_change_event(hass, [sensor_entity_id], handle_temperature_change)
        event.async_track_state_change_event(hass, [climate_entity_id], handle_climate_change)

    return True

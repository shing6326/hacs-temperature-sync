"""Set up the Temperature Sync component."""
import voluptuous as vol
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv, entity_platform
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

def setup(hass: HomeAssistant, config: dict):
    """Set up the Temperature Sync component."""
    def handle_temperature_change(event):
        """Handle the temperature change."""
        entity_id = event.data.get('entity_id')
        new_state = event.data.get('new_state')

        if new_state is None or entity_id is None:
            return

        # Only proceed if the entity is one of the temperature sensors we're interested in
        if entity_id not in [pair["sensor"] for pair in pairs]:
            return

        # Check if the sensor value is ready or not
        if new_state.state in ['unavailable', 'unknown']:
            return

        try:
            new_temperature = float(new_state.state)
        except ValueError:
            _LOGGER.error("State of %s is not a valid temperature: %s", entity_id, new_state.state)

        # Iterate through each pair to find the corresponding climate entity
        for pair in pairs:
            if pair["sensor"] == entity_id:
                climate_entity_id = pair["climate"]
                climate_state = hass.states.get(climate_entity_id)

                if climate_state is None:
                    continue

                # Get the current temperature attribute of the climate entity
                current_climate_temp = climate_state.attributes.get(ATTR_CURRENT_TEMPERATURE)

                # Determine if a sync is needed (if the attribute is missing or appears reset)
                needs_sync = current_climate_temp is None or current_climate_temp != new_temperature

                if needs_sync:
                    # Copy existing attributes and update the current_temperature
                    attributes = dict(climate_state.attributes)
                    attributes[ATTR_CURRENT_TEMPERATURE] = new_temperature

                    # Update the climate entity's temperature
                    hass.states.set(climate_entity_id, climate_state.state, attributes)

    pairs = config[DOMAIN]["pairs"]

    # Listen for changes in each temperature sensor
    for pair in pairs:
        sensor_entity_id = pair["sensor"]

        # Create a targeted event listener for each sensor
        hass.bus.listen('state_changed', handle_temperature_change)

    return True

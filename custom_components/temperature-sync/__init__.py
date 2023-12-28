"""Set up the Temperature Sync component."""
import voluptuous as vol
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv, entity_platform
from homeassistant.components.climate.const import ATTR_CURRENT_TEMPERATURE

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
        # Extract the entity_id of the sensor that triggered the event
        entity_id = event.data.get('entity_id')
        new_state = event.data.get('new_state')

        if new_state is None or entity_id is None or new_state.state == 'unavailable':
        # Exit silently if there's no new state, no entity ID, or the state is 'unavailable'
            return

        # Check if new_state is a non-numeric value
        try:
            # Attempt to convert the state to a float
            new_temperature = float(new_state.state)
        except ValueError:
            # If conversion fails, log an error and exit the function
            _LOGGER.error("State of %s is not a valid temperature: %s", entity_id, new_state.state)
            return

        # Find the corresponding climate entity
        for pair in pairs:
            if pair["sensor"] == entity_id:
                climate_entity_id = pair["climate"]
                climate_state = hass.states.get(climate_entity_id)

                if climate_state is None:
                    # If the climate entity does not exist, skip
                    continue

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

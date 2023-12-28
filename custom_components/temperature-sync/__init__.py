"""Set up the Temperature Sync component."""
import voluptuous as vol
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv, entity_platform
from homeassistant.const import ATTR_TEMPERATURE

DOMAIN = "temperature_sync"
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
        if new_state is None:
            return

        # Find the corresponding climate entity
        for pair in pairs:
            if pair["sensor"] == entity_id:
                climate_entity_id = pair["climate"]
                # Update the climate entity's temperature
                hass.states.set(climate_entity_id, new_state.state, attributes={
                    ATTR_CURRENT_TEMPERATURE: new_state.state
                })

    pairs = config[DOMAIN]["pairs"]
    for pair in pairs:
        # Listen for changes in the temperature sensor
        hass.bus.listen('state_changed', handle_temperature_change)

    return True

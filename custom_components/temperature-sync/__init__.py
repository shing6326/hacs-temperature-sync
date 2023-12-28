"""Set up the Temperature Sync component."""
import voluptuous as vol

from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv, discovery

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
    hass.data[DOMAIN] = {}

    # Read configuration
    pairs = config[DOMAIN]["pairs"]
    for pair in pairs:
        hass.data[DOMAIN][pair["sensor"]] = pair["climate"]

    hass.helpers.discovery.load_platform('climate', DOMAIN, {}, config)
    return True

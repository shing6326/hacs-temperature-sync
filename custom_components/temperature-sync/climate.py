"""Platform for climate integration."""
from homeassistant.components.climate import ClimateEntity
from homeassistant.const import TEMP_CELSIUS

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the climate platform."""
    # Add all climate entities
    for sensor, climate in hass.data["temperature_sync"].items():
        add_entities([SyncClimate(hass, sensor, climate)])

class SyncClimate(ClimateEntity):
    """Representation of a synced Climate entity."""

    def __init__(self, hass, sensor_entity, climate_entity):
        """Initialize the climate."""
        self.hass = hass
        self.sensor_entity = sensor_entity
        self.climate_entity = climate_entity
        self._name = f"Synced {climate_entity}"

    @property
    def name(self):
        """Return the name of the climate device."""
        return self._name

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def current_temperature(self):
        """Return the current temperature from the sensor."""
        return self.hass.states.get(self.sensor_entity).state

    # Implement other required methods and properties

    def update(self):
        """Update the climate conditions."""
        climate_state = self.hass.states.get(self.climate_entity)
        # Here you would add the logic to update the climate's temperature

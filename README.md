# Synchronize temperature sensors to climate

This is a home assistant integration that provides the temperature sensors value synchronization to the current_temperature sensor of climate entities

### Installation

Copy this folder to `<config_dir>/custom_components/temperature_sync/`.


Add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry for the Temperature Sync component
temperature-sync:
  pairs:
    - sensor: sensor.living_room_temperature  # Replace with your temperature sensor entity ID
      climate: climate.living_room_thermostat  # Replace with your climate entity ID
    - sensor: sensor.bedroom_temperature  # Another pair of sensor and climate
      climate: climate.bedroom_thermostat
```

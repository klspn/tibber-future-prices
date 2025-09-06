# Tibber Future Prices (Home Assistant Custom Component)
This is a custom component for Home Assistant that provides a sensor to fetch future hourly electricity prices from the Tibber API. The primary purpose of this component is to expose price data for today and tomorrow in a format ideal for creating detailed and interactive graphs with cards like the ApexCharts-Card.

(Example image of what a chart could look like)

Features
Future Prices Sensor: Creates a single sensor entity per Tibber home.

Hourly Data as Attributes: The hourly prices for the current day and the next day are stored in the today and tomorrow attributes.

Current Price as State: The sensor's state always reflects the electricity price for the current hour.

Automatic Updates: Data is automatically fetched from the Tibber API at regular intervals.

Robust Error Handling: The integration is resilient to temporary API failures, retaining the last known data to prevent empty charts.

Easy Setup: Configuration is handled conveniently through the Home Assistant UI (Config Flow).

Prerequisites
A working instance of Home Assistant.

The official Tibber integration must be installed, configured, and operational.

HACS (Home Assistant Community Store) is recommended for the easiest installation.

For the example below, the ApexCharts-Card is required, which can also be installed via HACS.

Installation
Method 1: HACS (Recommended)
As this repository is not in the default HACS store, you need to add it as a custom repository:

In Home Assistant, go to HACS > Integrations.

Click the three-dots menu (⋮) in the top right corner and select Custom repositories.

In the "Repository" field, paste the URL of this GitHub repository.

For the "Category", select Integration.

Click Add.

The "Tibber Future Prices" integration should now appear in HACS. Click on it and then Download.

Restart Home Assistant.

Method 2: Manual Installation
In the config directory of your Home Assistant instance, create the folder path /custom_components/tibber_future_prices/.

Copy all files from this repository (__init__.py, sensor.py, manifest.json, config_flow.py, const.py) into the newly created directory.

Restart Home Assistant.

Configuration
After installation, the setup is handled via the UI:

Go to Settings > Devices & Services.

Click the + Add Integration button in the bottom right.

Search for "Tibber Future Prices" and click on it.

A dialog box will appear. Simply click Submit.

The integration will automatically find your configured Tibber home and create the corresponding sensor entity. No further configuration is needed.

Sensor Details
After configuration, a new entity will be created:

Entity: sensor.tibber_future_prices_<your_home_name>

State: The electricity price for the current hour (e.g., 0.28).

Attributes:

today: A list of hourly prices for the current day. Each entry has the format:

JSON

{ "startsAt": "2025-09-07T14:00:00+02:00", "total": 0.28 }
tomorrow: A list of hourly prices for the next day (usually populated in the early afternoon of the preceding day).

Usage Example: ApexCharts-Card
This is a complete configuration for a Lovelace card that displays the prices for today and tomorrow (48 hours), scales the axes, color-codes the bars based on price, and correctly formats all values to two decimal places.

Add a new "Manual Card" to your dashboard and paste this code.

YAML

type: custom:apexcharts-card
header:
  show: true
  title: Electricity Prices Today & Tomorrow
  show_states: true
  colorize_states: true
graph_span: 48h
span:
  start: day
now:
  show: true
  label: Now
apex_config:
  yaxis:
    min: 0.15
    decimalsInFloat: 2
  plotOptions:
    bar:
      colors:
        ranges:
          - from: 0.15
            to: 0.30
            color: '#4caf50'
          - from: 0.30
            to: 0.35
            color: '#8bc34a'
          - from: 0.35
            to: 0.40
            color: '#ffeb3b'
          - from: 0.40
            to: 0.45
            color: '#ff9800'
          - from: 0.45
            to: 1
            color: '#f44336'
series:
  - entity: sensor.tibber_future_prices_mendener_strasse_14 # <-- Replace with your entity ID
    type: column
    name: Price
    float_precision: 2
    data_generator: |
      const today = entity.attributes.today || [];
      const tomorrow = entity.attributes.tomorrow || [];
      const combined = [...today, ...tomorrow];
      if (combined.length > 0) {
        return combined.map((item) => {
          return [new Date(item.startsAt).getTime(), parseFloat(item.total.toFixed(2))];
        });
      }
      return [];
Contributing
Contributions are welcome! If you have suggestions for improvements or find a bug, please feel free to open an issue or submit a pull request.

License
This project is licensed under the MIT License. See the LICENSE file for details.

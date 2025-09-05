import logging
from datetime import timedelta

import homeassistant.util.dt as dt_util
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(minutes=15)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Tibber future price sensor from a config entry."""
    tibber_connection = hass.data.get("tibber")
    if tibber_connection is None:
        _LOGGER.error("Tibber integration not found or not configured.")
        return

    homes = tibber_connection.get_homes(only_active=True)
    if not homes:
        _LOGGER.error("No active Tibber homes found.")
        return

    entities = []
    for home in homes:
        coordinator = TibberPriceUpdateCoordinator(hass, home)
        await coordinator.async_config_entry_first_refresh()
        home_name = home.info.get("viewer", {}).get("home", {}).get("appNickname") or f"Home {home.home_id[-4:]}"
        entities.append(TibberFuturePriceSensor(coordinator, home_name))

    async_add_entities(entities)


class TibberPriceUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Tibber price data."""
    def __init__(self, hass, tibber_home):
        self.tibber_home = tibber_home
        super().__init__(
            hass, _LOGGER, name=f"Tibber Future Prices {tibber_home.home_id}", update_interval=SCAN_INTERVAL
        )

    async def _async_update_data(self):
        """Fetch data from Tibber."""
        await self.tibber_home.update_info_and_price_info()
        
        if not self.tibber_home.price_total:
            _LOGGER.warning("No price data received from Tibber. Keeping previous data if available.")
            raise UpdateFailed("No price data received from Tibber API")

        now = dt_util.now()
        prices_today = []
        prices_tomorrow = []

        for key, price_info in self.tibber_home.price_total.items():
            price_time = dt_util.as_local(dt_util.parse_datetime(key))
            # HIER DIE ÄNDERUNG: Runde auf 2 Nachkommastellen
            price_data = {"startsAt": price_time.isoformat(), "total": round(price_info, 2)}
            if price_time.date() == now.date():
                prices_today.append(price_data)
            elif price_time.date() == (now + timedelta(days=1)).date():
                prices_tomorrow.append(price_data)
        
        return {"today": prices_today, "tomorrow": prices_tomorrow, "currency": self.tibber_home.currency}


class TibberFuturePriceSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Tibber Future Price sensor."""
    _attr_icon = "mdi:chart-line"
    _attr_has_entity_name = True 

    def __init__(self, coordinator, home_name: str):
        super().__init__(coordinator)
        self._home_name = home_name
        self._attr_name = f"Future Prices {self._home_name}"
        self._attr_unique_id = f"tibber_future_prices_{home_name.lower().replace(' ', '_')}"
        self._update_attrs()

    @property
    def native_value(self):
        """Return the state of the sensor (current price)."""
        now = dt_util.now()
        if self.coordinator.data and self.coordinator.data.get("today"):
            for price in self.coordinator.data["today"]:
                price_time = dt_util.parse_datetime(price["startsAt"])
                if price_time.hour == now.hour:
                    return price["total"] # Bereits gerundet
        return None

    def _update_attrs(self) -> None:
        """Update attributes from coordinator data."""
        if self.coordinator.data:
            self._attr_extra_state_attributes = {
                "today": self.coordinator.data.get("today", []),
                "tomorrow": self.coordinator.data.get("tomorrow", []),
            }
            self._attr_native_unit_of_measurement = self.coordinator.data.get("currency")

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await super().async_added_to_hass()
        self.async_on_remove(
            self.coordinator.async_add_listener(self._update_attrs)
        )

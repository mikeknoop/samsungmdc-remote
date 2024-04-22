"""Media Player class for Samsung MDC display."""

import asyncio
import logging
from collections.abc import Iterable

from typing import (
    Any,
)

from samsung_mdc import MDC
from samsung_mdc.commands import INPUT_SOURCE, MUTE, POWER
from samsung_mdc.exceptions import (
    MDCTimeoutError,
    MDCResponseError,
    NAKError,
)

from homeassistant import config_entries
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.components.remote import RemoteEntity, RemoteEntityFeature, RemoteEntityDescription
from homeassistant.const import (
    CONF_IP_ADDRESS,
    CONF_NAME,
    CONF_TYPE,
    CONF_UNIQUE_ID,
    # STATE_OFF,
    # STATE_ON,
    # STATE_UNAVAILABLE,
)
from homeassistant.core import HomeAssistant

from .const import (
    CONF_DISPLAY_ID,
    DOMAIN
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    """Set up media player from a config entry created in the integrations UI."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    name = config[CONF_NAME]
    serial = config[CONF_UNIQUE_ID]
    model_type = config[CONF_TYPE]
    display_id = config[CONF_DISPLAY_ID]

    entity_id = generate_entity_id("remote.{}", f"samsung_mdc_{serial}", None, hass)

    mdc = MDC(config[CONF_IP_ADDRESS])
    remote = SamsungMDCDisplayRemote(mdc, name, serial, model_type, display_id, entity_id)

    async_add_entities([remote])

# class RemoteDescription(RemoteEntityDescription):
#     key = "samsung_mdc_remote"
#     name = "samsung_mdc_remote"

class SamsungMDCDisplayRemote(RemoteEntity):

    def __init__(
        self, mdc: MDC, conf_name: str, serial: str, model_type: str, display_id: int, entity_id: str
    ) -> None:
        """Initialize a new instance of SamsungMDCDisplayRemote class."""
        super().__init__()
        self.entity_id = entity_id
        self.conf_name = conf_name
        self.mdc = mdc
        self.serial = serial
        self.model_type = model_type
        self.display_id = display_id

    async def async_send_command(self, command: Iterable[str], **kwargs: Any) -> None:
        """
        Format of command string is: `command_name,value`
        Example: `volume,100`
        Example: `manual_lamp,25`
        """
        _LOGGER.warning(repr(command))
        for cmd in command:
            args = cmd.split(',')
            cmd_name = args.pop(0)
            func = getattr(self.mdc, cmd_name)
            await func(self.display_id, [int(a) if a.isnumeric() else a for a in args])
            await self.mdc.close() # force reconnect on next command
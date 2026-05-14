import asyncio
import logging

import tmodbus

THERMIA_HOST = "172.16.2.178"
THERMIA_PORT = 502
THERMIA_UNIT_ID = 1

logger = logging.getLogger(__name__)


def _decode_signed_16bit(val: int) -> int:
    return val - 0x10000 if val >= 0x8000 else val


async def _read_outdoor_temp_async() -> float:
    client = tmodbus.create_async_tcp_client(
        THERMIA_HOST, port=THERMIA_PORT, unit_id=THERMIA_UNIT_ID
    )
    async with client:
        raw = await client.read_input_registers(start_address=13, quantity=1)
    return _decode_signed_16bit(raw[0]) / 100.0


def get_outdoor_temp() -> float | None:
    try:
        return asyncio.run(_read_outdoor_temp_async())
    except Exception as e:
        logger.error("Failed to read thermia outdoor temp: %s", e)
        return None

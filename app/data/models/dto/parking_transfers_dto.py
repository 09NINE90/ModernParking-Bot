from typing import NamedTuple


class ParkingTransfer(NamedTuple):
    spot_id: int
    recipient_tg_id: int
    owner_tg_id: int
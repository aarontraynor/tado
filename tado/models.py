from datetime import datetime

from pydantic import BaseModel


class TadoState(BaseModel):
    mobile_devices: list = []
    home_state: dict = {}
    previous_device_states: dict = {}
    last_login: datetime = datetime.now()


class TadoCredentials(BaseModel):
    username: str
    password: str

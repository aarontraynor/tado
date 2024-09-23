import logging
import traceback
from argparse import ArgumentParser
from datetime import datetime, timedelta
from uuid import uuid4

from models import TadoCredentials, TadoState
from PyTado.interface import Tado
from retry import retry

logger = logging.getLogger(__name__)


def setup_args(arg_parser: ArgumentParser) -> None:
    arg_parser.add_argument(
        "-u", "--username", help="Your Tado username (normally your email address)"
    )
    arg_parser.add_argument("-p", "--password", help="Your Tado password")


def get_tado_credentials(arg_parser: ArgumentParser) -> TadoCredentials:
    setup_args(arg_parser=arg_parser)

    args = arg_parser.parse_args()

    return TadoCredentials(
        username=args.username,
        password=args.password,
    )


@retry(delay=1, backoff=1, max_delay=10)
def login(credentials: TadoCredentials) -> Tado:
    return Tado(credentials.username, credentials.password)


@retry(delay=1, backoff=1, max_delay=10)
def set_home(tado_instance: Tado) -> None:
    tado_instance.set_home()


@retry(delay=1, backoff=1, max_delay=10)
def set_away(tado_instance: Tado) -> None:
    tado_instance.set_away()


def refresh_auth(
    state: TadoState,
    credentials: TadoCredentials,
    current_instance: Tado,
) -> Tado:
    if state.last_login + timedelta(hours=1) < datetime.now():
        return login(credentials=credentials)
    else:
        return current_instance


@retry(delay=1, backoff=1, max_delay=10)
def get_mobile_devices(tado: Tado) -> list:
    return tado.get_mobile_devices()


@retry(delay=1, backoff=1, max_delay=10)
def get_home_state(tado: Tado) -> dict:
    return tado.get_home_state()


def is_device_at_home(tado_state: TadoState, device: dict) -> bool:
    device_id = device["id"]

    if not device["location"]:
        if device_id not in tado_state.devices_with_no_location.keys():
            logger.warning(f"No location info for device {device['name']}")

        tado_state.devices_with_no_location[device_id] = device
        return False
    else:
        tado_state.devices_with_no_location.pop(device_id, None)

    tracking_enabled = device["settings"]["geoTrackingEnabled"]
    at_home = device["location"]["atHome"] if tracking_enabled else False
    location_stale = device["location"]["stale"] if tracking_enabled else False

    return all([at_home, tracking_enabled, not location_stale])


def update_previous_device_state(
    tado_state: TadoState,
    device: dict,
) -> None:
    device_id = device["id"]
    tado_state.previous_device_states[device_id] = device


def is_home_occupied(tado_state: TadoState) -> bool:
    devices_at_home = []
    print(f"Device count: {len(tado_state.mobile_devices)}")
    for device in tado_state.mobile_devices:
        try:
            if is_device_at_home(tado_state=tado_state, device=device):
                devices_at_home.append(device)

            update_previous_device_state(
                tado_state=tado_state,
                device=device,
            )
        except KeyError:
            logger.exception("Error while getting device info.")

    return len(devices_at_home) > 0


def update_home_state_if_required(
    tado_instance: Tado, is_home_occupied: bool, current_home_status: str
) -> None:
    if is_home_occupied and current_home_status == "AWAY":
        set_home(tado_instance=tado_instance)
    elif not is_home_occupied and current_home_status == "HOME":
        set_away(tado_instance=tado_instance)


def write_exception_to_file():
    try:
        timestamp = datetime.now().isoformat()
        random_string = uuid4().hex

        filename = f"./error_logs/{timestamp}__{random_string}.txt"

        with open(filename, "w+") as log_file:
            log_file.write(f"ERROR LOG: {traceback.format_exc()}")
            logger.warning(f"Error logged to file: {filename}")
    except Exception:
        logger.exception("An exception occurred while trying to write an exception to a file.")

import logging
from argparse import ArgumentParser

from models import TadoState
from tado import (
    get_home_state,
    get_mobile_devices,
    get_tado_credentials,
    is_home_occupied,
    login,
    refresh_auth,
    update_home_state_if_required,
    write_exception_to_file,
)

logger = logging.getLogger(__name__)

arg_parser = ArgumentParser()
tado_credentials = get_tado_credentials(arg_parser=arg_parser)
tado = login(credentials=tado_credentials)

tado_state = TadoState()

while True:
    try:
        tado = refresh_auth(
            state=tado_state,
            credentials=tado_credentials,
            current_instance=tado,
        )

        tado_state.mobile_devices = get_mobile_devices(tado=tado)
        tado_state.home_state = get_home_state(tado=tado)

        current_home_status = tado_state.home_state["presence"]

        is_someone_at_home = is_home_occupied(tado_state=tado_state)

        update_home_state_if_required(
            tado_instance=tado,
            is_home_occupied=is_someone_at_home,
            current_home_status=current_home_status,
        )
    except Exception:
        logger.exception("An error occurred during the main loop execution.")
        write_exception_to_file()

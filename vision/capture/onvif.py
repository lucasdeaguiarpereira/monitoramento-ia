"""Consulta informações básicas de uma câmera via ONVIF."""

from __future__ import annotations

import logging
import os
import sys
from collections.abc import Mapping
from pathlib import Path

LOGGER = logging.getLogger(__name__)
DEFAULT_HOST = "192.168.15.2"
DEFAULT_PORT = 8000


def get_configuration() -> tuple[str, int, str, str]:
    """Obtém e valida a configuração ONVIF das variáveis de ambiente."""
    host = os.getenv("REOLINK_ONVIF_HOST") or DEFAULT_HOST
    port_value = os.getenv("REOLINK_ONVIF_PORT") or str(DEFAULT_PORT)
    username = os.getenv("REOLINK_USER")
    password = os.getenv("REOLINK_PASSWORD")

    if not username or not password:
        raise ValueError(
            "Defina as variáveis REOLINK_USER e REOLINK_PASSWORD."
        )

    try:
        port = int(port_value)
    except ValueError as error:
        raise ValueError(
            "REOLINK_ONVIF_PORT deve conter uma porta numérica válida."
        ) from error

    if not 1 <= port <= 65535:
        raise ValueError("REOLINK_ONVIF_PORT deve estar entre 1 e 65535.")

    return host, port, username, password


def get_value(response: object, field: str) -> object | None:
    """Obtém um campo de uma resposta ONVIF ou retorna None."""
    if isinstance(response, Mapping):
        return response.get(field)
    return getattr(response, field, None)


def query_camera(host: str, port: int, username: str, password: str) -> None:
    """Consulta informações e capacidades anunciadas pela câmera."""
    from onvif import ONVIFClient

    try:
        client = ONVIFClient(host, port, username, password)
        device_service = client.devicemgmt()
        LOGGER.info("Conexão ONVIF estabelecida.")

        device_information = device_service.GetDeviceInformation()
        LOGGER.info(
            "Manufacturer: %s",
            get_value(device_information, "Manufacturer") or "não informado",
        )
        LOGGER.info(
            "Model: %s",
            get_value(device_information, "Model") or "não informado",
        )
        LOGGER.info(
            "FirmwareVersion: %s",
            get_value(device_information, "FirmwareVersion")
            or "não informado",
        )
        LOGGER.info(
            "SerialNumber: %s",
            get_value(device_information, "SerialNumber") or "não informado",
        )
        LOGGER.info(
            "HardwareId: %s",
            get_value(device_information, "HardwareId") or "não informado",
        )

        capabilities = device_service.GetCapabilities(Category="All")
        LOGGER.info("Capabilities:")
        for capability_name in (
            "Device",
            "Media",
            "Events",
            "Imaging",
            "PTZ",
            "Analytics",
        ):
            status = (
                "disponível"
                if get_value(capabilities, capability_name) is not None
                else "indisponível"
            )
            LOGGER.info("- %s: %s", capability_name, status)
    finally:
        LOGGER.info("Conexão ONVIF encerrada.")


def main() -> int:
    """Executa o teste funcional de consultas ONVIF."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    try:
        query_camera(*get_configuration())
    except Exception as error:
        LOGGER.error(
            "Falha na comunicação ONVIF (%s): %s",
            type(error).__name__,
            error,
        )
        return 1

    return 0


if __name__ == "__main__":
    script_directory = str(Path(__file__).resolve().parent)
    if script_directory in sys.path:
        sys.path.remove(script_directory)
    raise SystemExit(main())

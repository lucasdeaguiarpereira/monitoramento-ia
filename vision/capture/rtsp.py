"""Captura frames de um stream RTSP."""

from __future__ import annotations

import argparse
import logging
import os
import time
from datetime import datetime
from pathlib import Path

import cv2

LOGGER = logging.getLogger(__name__)
DEFAULT_OUTPUT_DIRECTORY = (
    Path(__file__).resolve().parents[2] / "samples" / "images"
)


class RTSPCaptureError(RuntimeError):
    """Indica uma falha durante a captura RTSP."""


class RTSPFrameCapture:
    """Captura e salva um frame de um stream RTSP."""

    def __init__(self, url: str, output_directory: Path) -> None:
        """Inicializa a captura com a URL RTSP e o diretório de saída."""
        if not url.lower().startswith(("rtsp://", "rtsps://")):
            raise ValueError("É necessário informar uma URL RTSP válida.")

        self._url = url
        self._output_directory = output_directory

    def capture(self) -> Path:
        """Lê exatamente um frame, salva-o como JPEG e retorna seu caminho."""
        self._output_directory.mkdir(parents=True, exist_ok=True)
        output_path = self._build_output_path()
        stream = cv2.VideoCapture(self._url)

        try:
            if not stream.isOpened():
                raise RTSPCaptureError("Não foi possível abrir o stream RTSP.")

            LOGGER.info("Conexão RTSP estabelecida; lendo um frame.")
            frame_read, frame = stream.read()
            if not frame_read or frame is None:
                raise RTSPCaptureError(
                    "Não foi possível ler um frame do stream RTSP."
                )

            if not cv2.imwrite(str(output_path), frame):
                raise RTSPCaptureError(
                    f"Não foi possível salvar o arquivo JPEG em {output_path}."
                )

            LOGGER.info("Frame salvo em %s.", output_path)
            return output_path
        finally:
            stream.release()
            LOGGER.info("Conexão RTSP encerrada.")

    def _build_output_path(self) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        return self._output_directory / f"rtsp_frame_{timestamp}.jpg"


def read_stream(url: str) -> None:
    """Lê continuamente um stream RTSP e registra o FPS real."""
    if not url.lower().startswith(("rtsp://", "rtsps://")):
        raise ValueError("É necessário informar uma URL RTSP válida.")

    stream = cv2.VideoCapture(url)

    try:
        if not stream.isOpened():
            raise RTSPCaptureError("Não foi possível abrir o stream RTSP.")

        LOGGER.info("Conexão RTSP estabelecida.")
        interval_started_at = time.monotonic()
        interval_frames = 0
        total_frames = 0

        while True:
            frame_read, frame = stream.read()
            if not frame_read or frame is None:
                raise RTSPCaptureError(
                    "Não foi possível ler um frame do stream RTSP."
                )

            interval_frames += 1
            total_frames += 1
            current_time = time.monotonic()
            elapsed_time = current_time - interval_started_at

            if elapsed_time >= 5.0:
                real_fps = interval_frames / elapsed_time
                LOGGER.info(
                    "Stream ativo | FPS real: %.1f | Frames recebidos: %d",
                    real_fps,
                    total_frames,
                )
                interval_started_at = current_time
                interval_frames = 0
    except KeyboardInterrupt:
        LOGGER.info("Encerramento solicitado pelo usuário.")
    finally:
        stream.release()
        LOGGER.info("Conexão RTSP encerrada.")


def parse_arguments() -> argparse.Namespace:
    """Processa os argumentos da linha de comando."""
    parser = argparse.ArgumentParser(
        description="Captura um frame ou lê continuamente um stream RTSP."
    )
    parser.add_argument(
        "url",
        nargs="?",
        help="URL RTSP alternativa à variável REOLINK_RTSP_URL.",
    )
    parser.add_argument(
        "--stream",
        action="store_true",
        help="Mantém a leitura contínua do stream até receber Ctrl+C.",
    )
    parser.add_argument(
        "--output-directory",
        type=Path,
        default=DEFAULT_OUTPUT_DIRECTORY,
        help="Diretório de destino (padrão: samples/images).",
    )
    return parser.parse_args()


def main() -> int:
    """Executa a captura única ou a leitura contínua via RTSP."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    arguments = parse_arguments()
    url = os.getenv("REOLINK_RTSP_URL") or arguments.url

    if not url:
        LOGGER.error(
            "Informe a variável REOLINK_RTSP_URL ou o argumento posicional url."
        )
        return 1

    try:
        if arguments.stream:
            read_stream(url)
        else:
            RTSPFrameCapture(url, arguments.output_directory).capture()
    except (RTSPCaptureError, ValueError) as error:
        LOGGER.error("Falha ao capturar o frame: %s", error)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

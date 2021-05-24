from vacunacion_regional.entrypoints.cli import cli_entrypoint
import vacunacion_regional.entrypoints.api as api

__all__ = ["api"]

if __name__ == "__main__":
    cli_entrypoint()

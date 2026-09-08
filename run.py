from app.main import main
from app.utils.logging_config import setup_logging


if __name__ == "__main__":

    logger = setup_logging()

    try:

        main()

    except KeyboardInterrupt:

        logger.warning(
            "Audit cancelled by user."
        )

        raise SystemExit(1)

    except Exception:

        logger.exception(
            "Azure Resource Audit failed."
        )

        raise SystemExit(1)
from concurrent.futures import ThreadPoolExecutor, as_completed

import urllib3

from .config import load_configuration
from .logger import logger
from .processor import EngineProcessor


def main():
    # Disable SSL warnings (use cautiously in production)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    cfg = load_configuration()
    engines = cfg.get("ENGINES", [])
    influx_v1 = cfg.get("INFLUXDB_V1")
    influx_v2 = cfg.get("INFLUXDB_V2")

    if not engines:
        logger.error("No engines defined in configuration.")
        return
    if not influx_v1 and not influx_v2:
        logger.error("No InfluxDB configuration found.")
        return

    with ThreadPoolExecutor(max_workers=len(engines)) as exec:
        futures = [
            exec.submit(EngineProcessor(e, influx_v1, influx_v2).process)
            for e in engines
        ]
        for f in as_completed(futures):
            try:
                f.result()
            except Exception as e:
                logger.error(f"Engine processing failed: {e}")


if __name__ == "__main__":
    main()

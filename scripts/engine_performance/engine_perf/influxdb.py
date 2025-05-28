from datetime import timezone

import requests
from influxdb_client import InfluxDBClient

from .logger import logger


def get_last_timestamp_v2(slice_ref, engine_name, cfg):
    try:
        query = f"""
        from(bucket: "{cfg['BUCKET']}")
          |> range(start: -7d)
          |> filter(fn: (r) => r._measurement == "{slice_ref}" and r.engine == "{engine_name}")
          |> sort(columns: ["_time"], desc: true)
          |> limit(n:1)
        """
        client = InfluxDBClient(url=cfg["URL"], token=cfg["TOKEN"], org=cfg["ORG"])
        tables = client.query_api().query(query)
        for t in tables:
            for r in t.records:
                return r.get_time().astimezone(timezone.utc).isoformat()
    except Exception as e:
        logger.error(f"InfluxDB v2 query failed: {e}")
    return None


def get_last_timestamp_v1(slice_ref, engine_name, cfg):
    try:
        query = f'SELECT * FROM "{slice_ref}" WHERE "engine" = \'{engine_name}\' ORDER BY time DESC LIMIT 1'
        params = {"db": cfg["DB"], "q": query}
        if "USER" in cfg:
            params["u"] = cfg["USER"]
        if "PASSWORD" in cfg:
            params["p"] = cfg["PASSWORD"]
        url = f"{cfg['URL'].rstrip('/')}/query"
        resp = requests.get(url, params=params)

        if resp.status_code == 200:
            results = resp.json().get("results", [])
            if results:
                series = results[0].get("series", [])
                if series:
                    values = series[0].get("values", [])
                    if values:
                        return values[0][0]
    except Exception as e:
        logger.error(f"InfluxDB v1 query failed: {e}")
    return None


def write_to_influxdb_v2(cfg, lines, slice_type, engine_name):
    if not lines:
        logger.info("No data to write to InfluxDB.")
        return
    try:
        url = f"{cfg['URL'].rstrip('/')}/api/v2/write"
        headers = {
            "Authorization": f"Token {cfg['TOKEN']}",
            "Content-Type": "text/plain",
        }
        params = {"org": cfg["ORG"], "bucket": cfg["BUCKET"], "precision": "ns"}
        resp = requests.post(url, params=params, data="\n".join(lines), headers=headers)
        resp.raise_for_status()
        logger.info(
            f"Engine '{engine_name}' — slice '{slice_type}' : Successfully wrote {len(lines)} points to InfluxDB v2."
        )
    except Exception as e:
        logger.error(f"Failed to write to InfluxDB v2: {e}")


def write_to_influxdb_v1(cfg, lines, slice_type, engine_name):
    if not lines:
        logger.info("No data to write to InfluxDB.")
        return
    try:
        url = f"{cfg['URL'].rstrip('/')}/write"
        params = {"db": cfg["DB"], "precision": "ns"}
        if "USER" in cfg:
            params["u"] = cfg["USER"]
        if "PASSWORD" in cfg:
            params["p"] = cfg["PASSWORD"]
        resp = requests.post(
            url,
            params=params,
            data="\n".join(lines).encode("utf-8"),
            headers={"Content-Type": "text/plain"},
        )
        resp.raise_for_status()
        logger.info(
            f"Engine '{engine_name}' — slice '{slice_type}' : Successfully wrote {len(lines)} points to InfluxDB v1."
        )
    except Exception as e:
        logger.error(f"Failed to write to InfluxDB v1: {e}")

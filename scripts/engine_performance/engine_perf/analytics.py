import requests

from .logger import logger


def fetch_analytics_data(session, base_url):
    try:
        response = session.get(f"{base_url}/resources/json/delphix/analytics")
        response.raise_for_status()
        return [
            {"ref": item.get("reference"), "type": item.get("statisticType")}
            for item in response.json().get("result", [])
            if item.get("reference")
        ]
    except requests.RequestException as e:
        logger.error(f"Failed to fetch analytics data: {e}")
        return []


def retrieve_slice_data(
    session, base_url, slice_type, slice_reference, start_iso, end_iso, engine
):
    url = f"{base_url}/resources/json/delphix/analytics/{slice_reference}/getData?start='{start_iso}'&end='{end_iso}'&resolution=1"
    logger.info(
        f"Engine '{engine}' — slice '{slice_type}' - ref '{slice_reference}' : Calling Delphix API from {start_iso} to {end_iso} via Delphix API."
    )

    try:
        response = session.get(url)
        response.raise_for_status()
        json_data = response.json()

        if json_data.get("type") == "ErrorResult":
            logger.error(
                f"Delphix API returned error for slice {slice_reference}: {json_data.get('error')}"
            )
            return None

        return json_data
    except requests.RequestException as e:
        logger.error(f"Failed to fetch slice data: {e}")
        return None


def convert_to_line_protocol(data, hostname, engine_name):
    from datetime import datetime

    lines = []
    for stream in data.get("result", {}).get("datapointStreams", []):
        measurement = stream.get("type", "unknown_measurement")
        for point in stream.get("datapoints", []):
            timestamp_str = point.get("timestamp")
            if not timestamp_str:
                continue
            try:
                dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                timestamp = int(dt.timestamp() * 1e9)
            except ValueError:
                continue

            fields = []
            for k, v in point.items():
                if k in ["type", "timestamp"]:
                    continue
                if isinstance(v, int):
                    fields.append(f"{k}={v}i")
                elif isinstance(v, float):
                    fields.append(f"{k}={v}")
                elif isinstance(v, str):
                    fields.append(f'{k}="{v}"')
                elif isinstance(v, bool):
                    fields.append(f"{k}={'true' if v else 'false'}")
            if fields:
                lines.append(
                    f"{measurement},host={hostname},engine={engine_name} {','.join(fields)} {timestamp}"
                )
    return lines

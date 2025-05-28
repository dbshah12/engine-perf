import socket
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone

from dateutil import parser

from .analytics import (convert_to_line_protocol, fetch_analytics_data,
                        retrieve_slice_data)
from .influxdb import (get_last_timestamp_v1, get_last_timestamp_v2,
                       write_to_influxdb_v1, write_to_influxdb_v2)
from .logger import logger
from .session import initialize_api_session


class EngineProcessor:

    slice_type_to_datapoint_type = {
        "CPU_UTIL": "CpuUtilDatapointStream",
        "DISK_OPS": "DiskOpsDatapointStream",
        "iSCSI_OPS": "IScsiOpsDatapointStream",
        "NETWORK_INTERFACE_UTIL": "NetworkInterfaceUtilDatapointStream",
        "NFS_OPS": "NfsOpsDatapointStream",
        "TCP_STATS": "TCPStatsDatapointStream",
    }

    def __init__(self, engine, influxdb_v1, influxdb_v2):
        self.engine = engine
        self.influxdb_v1 = influxdb_v1
        self.influxdb_v2 = influxdb_v2
        self.hostname = socket.gethostname()
        self.lock = threading.Lock()

    def process(self):
        name = self.engine.get("NAME")
        url = self.engine.get("BASE_URL")
        user = self.engine.get("USERNAME")
        pwd = self.engine.get("PASSWORD")

        if not all([name, url, user, pwd]):
            logger.warning(f"Missing config for engine: {self.engine}")
            return

        logger.info(f"Processing engine: {name}")
        session = initialize_api_session(url, user, pwd)
        if not session:
            return

        slices = fetch_analytics_data(session, url)
        if not slices:
            logger.info(f"No slice references for engine: {name}")
            return

        with ThreadPoolExecutor(max_workers=len(slices)) as exec:
            futures = [
                exec.submit(self._process_slice, session, url, s) for s in slices
            ]
            for f in as_completed(futures):
                try:
                    f.result()
                except Exception as e:
                    logger.error(f"Error processing slice: {e}")

    def _process_slice(self, session, base_url, slice):
        slice_ref = slice["ref"]
        raw_slice_type = slice["type"]
        now = datetime.now(timezone.utc).replace(microsecond=0)
        start_dt = (now - timedelta(days=7))

        # Retrieve last timestamp (if any)
        with self.lock:
            slice_type = self.slice_type_to_datapoint_type.get(raw_slice_type)
            last_timestamp = None
            if self.influxdb_v2:
                last_timestamp = get_last_timestamp_v2(slice_type, self.engine["NAME"], self.influxdb_v2)
            elif self.influxdb_v1:
                last_timestamp = get_last_timestamp_v1(slice_type, self.engine["NAME"], self.influxdb_v1)

        # If last_timestamp is available, override start_dt
        if last_timestamp:
            start_dt = parser.isoparse(last_timestamp).replace(microsecond=0)

        # Format timestamps
        start_iso = start_dt.isoformat()
        end_iso = now.isoformat()

        # Retrieve data
        data = retrieve_slice_data(
            session,
            base_url,
            slice_type,
            slice_ref,
            start_iso,
            end_iso,
            self.engine["NAME"],
        )
        if not data:
            return
        lines = convert_to_line_protocol(data, self.hostname, self.engine["NAME"])
        if not lines:
            return

        with self.lock:
            if self.influxdb_v2:
                write_to_influxdb_v2(
                    self.influxdb_v2, lines, slice_type, self.engine["NAME"]
                )
            elif self.influxdb_v1:
                write_to_influxdb_v1(
                    self.influxdb_v1, lines, slice_type, self.engine["NAME"]
                )

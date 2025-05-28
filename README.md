# engine-perf
Engine Performance of Delphix Engine with Telegraph, InfluxDb v2 &amp; Grafana

# How to run
- Clone the repo
- Install docker-compose in your system
- `docker compose build`
- `docker compose up -d`

# Credentials
- The default `username/password` for InfluxDB and Grafana is `admin/Delphix@123`.
- However, you can change these credentials in the `docker-compose.yml` file.
- Make sure to update the same credentials in:
  - `telegraf.conf`
  - `scripts/engine_performance/config.json`
  - These files reference the credentials inside the Docker containers.

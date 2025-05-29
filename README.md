# 🚀 Introduction
Engine Performance Analytics Tool is multi-threaded Python-based project that:​
- Fetches performance metrics from Delphix Engines every 1 minute.​
- Stores the data in InfluxDB, a high-performance time-series database.​
- Integrated this script with Telegraf, allowing it to run automatically at 1-minute intervals.​
- Using Grafana, which integrates seamlessly with InfluxDB, we built a configurable dashboard:​
  - Includes default graphs.​
  - Allows users to add custom queries for specific metrics.​
- This approach decouples time-series data from other databases, reducing system load and improving performance visualization.

# 🛠️ Technology Stack
- Telegraf – Data collection agent
- InfluxDB – Time-series database
- Grafana – Visualization and alerting platform
- Python – Scripting to fetch data from Delphix Engines
- Docker – Build and deploy the entire stack as containers

# ▶️ How to Run
- Clone the repository
- Ensure `docker-compose` is installed on your system
- Update the `scripts/engine_performance/config.json` file to include the Delphix engines and their credentials for which you want to fetch data.
- Run the following commands:
```
docker compose build  
docker compose up -d
```
This will spin up all required containers (InfluxDB, Telegraf, Grafana) on a shared Docker network.



# 🔐 Default Credentials
- The default `username/password` for InfluxDB and Grafana is `admin/Delphix@123`.
- However, you can change these credentials in the `docker-compose.yml` file.
- Make sure to update the same credentials in:
  - `telegraf.conf`
  - `scripts/engine_performance/config.json`
  - These files reference the credentials inside the Docker containers.

# 🌐 Default Access URLs
- InfluxDB: `http://<host-ip>:8086`
- Grafana: `http://<host-ip>:3000`

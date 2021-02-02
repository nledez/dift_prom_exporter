Launch it
=========

```
cp drift_prom_exporter.yml.sample drift_prom_exporter.yml
docker container run --volume "`pwd`/drift_prom_exporter.yml:/drift_prom_exporter.yml" --env "CONFIG=/drift_prom_exporter.yml" --publish 8000:8000 nledez/drift_prom_exporter:latest
```


Launch it
=========

```
curl http://127.0.0.1:8000
```


Example
=======

```
curl http://127.0.0.1:8000 | grep -i drift
# HELP token_drift_seconds Seconds remind before token expiration
# TYPE token_drift_seconds gauge
token_drift_seconds{token="vaultbot"} 2.548082e+06
token_drift_seconds{token="apps"} 2.49488e+06
token_drift_seconds{token="prometheus"} 2.571535e+06
token_drift_seconds{token="transit-boundary"} -1.0
token_drift_seconds{token="token-lookup"} 2.746223e+06
# HELP token_drift_days Days remind before token expiration
# TYPE token_drift_days gauge
token_drift_days{token="vaultbot"} 29.0
token_drift_days{token="apps"} 28.0
token_drift_days{token="prometheus"} 29.0
token_drift_days{token="transit-boundary"} -1.0
token_drift_days{token="token-lookup"} 31.0
```


Prometheus configuration
========================

Add this to your Prometheus configuration:

```
scrape_configs:
  - job_name: drift_prom_exporter
    scheme: http
    static_configs:
      - targets: ["127.0.0.1:8000"]
    scrape_interval: 60s
    params:
      format: ["prometheus"]
```

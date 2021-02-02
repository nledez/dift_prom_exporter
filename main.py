from prometheus_client import start_http_server, Gauge
import random
import time
import hvac
import os
import sys
import yaml

from datetime import datetime
from hvac.exceptions import Unauthorized


def load(config_path):
    if not os.path.exists(config_path):
        print('Missing {} file. Please create it.'.format(config_path))
        sys.exit(1)
    else:
        with open(config_path, 'r') as stream:
            try:
                return yaml.load(stream, Loader=yaml.FullLoader)
            except yaml.YAMLError as exc:
                print(exc)
                sys.exit(1)


def collect_token_drift():
    config_path = os.environ.get('CONFIG', False)
    if not config_path:
        config_path = sys.argv[1]
    config = load(config_path)
    data = {}

    for name, token in config['tokens'].items():
        data[name] = {}
        data[name]['s'] = -1
        data[name]['d'] = -1
        try:
            expire_datetime = lookup_token(config, token)['data']['expire_time']
            expire = datetime.strptime(expire_datetime[0:19], '%Y-%m-%dT%H:%M:%S')
            now = datetime.now()
            drift = expire - now
            data[name]['s'] = int(drift.total_seconds())
            data[name]['d'] = int(drift.days)
        except hvac.exceptions.Unauthorized:
            pass

    return data


def lookup_token(config, token):
    client = hvac.Client(
        url=config['vault']['server'],
        token=token,
        verify=config['vault']['verify'],
    )
    if client.is_authenticated():
        return client.lookup_token()
    else:
        raise Unauthorized("May be expired token")


def init_metrics(metrics):
    metrics['gts'] = Gauge('token_drift_seconds',
                          'Seconds remind before token expiration',
                          ['token'])
    metrics['gtd'] = Gauge('token_drift_days',
                          'Days remind before token expiration',
                          ['token'])
    # metrics['gc'] = Gauge('certificate_drift', 'Seconds remind before certificate expiration')


def update_metrics(metrics, data):
    for name, values in data.items():
        metrics['gts'].labels(name).set(values['s'])
        metrics['gtd'].labels(name).set(values['d'])
    # metrics['gc'].inc(random.random())


if __name__ == '__main__':
    scrape_interval = int(os.environ.get('INTERVAL', 300))
    # Start up the server to expose the metrics.
    metrics = {}
    init_metrics(metrics)
    start_http_server(8000)

    # Update metrics
    while True:
        data = collect_token_drift()
        update_metrics(metrics, data)
        time.sleep(scrape_interval)

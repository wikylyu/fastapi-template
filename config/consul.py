import consul
import os
import json

_consul_http_token = os.environ.get('CONSUL_HTTP_TOKEN')
_consul_host = os.environ.get('CONSUL_HOST') or '127.0.0.1'
_consul_client = consul.Consul(host=_consul_host, token=_consul_http_token,)
_consul_key_root="template" # FIXME 修改consul kv的根路径


def read_config_by_key(key: str) -> dict:
    _, result = _consul_client.kv.get(_consul_key_root+'/'+key)
    return json.loads(result['Value'])

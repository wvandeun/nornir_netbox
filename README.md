[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)
[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![Documentation Status](https://readthedocs.org/projects/nornir-netbox/badge/?version=latest)](https://nornir-netbox.readthedocs.io/en/latest/?badge=latest)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

# nornir_netbox

[NetBox](https://github.com/netbox-community/netbox) plugin for [Nornir](https://github.com/nornir-automation/nornir)

The NetBox plugin exposes 2 inventory classes for usage.
- `NBInventory` is deprecated and should not be used anymore, it is still available for backwards compatibility only
- `NetBoxInventory2` is the recommended NetBox inventory plugin. It provides some extra functionality such as exposing all NetBox device attributes to the Nonir Host through the data attribute. It is the recommended plugin to use. All feature development will only take place on this plugin.

## Install

The recommended way to install nornir_netbox is via pip or poetry.

```bash
pip install nornir-netbox
```

```bash
poetry add nornir-netbox
```

## Example usage

### Using the Nornir configuration file

```yaml
---
inventory:
  plugin: NBInventory
  options:
    nb_url: "https://netbox.local"
    nb_token: "123_NETBOX_API_TOKEN_456"
```

```yaml
---
inventory:
  plugin: NetBoxInventory2
  options:
    nb_url: "https://netbox.local"
    nb_token: "123_NETBOX_API_TOKEN_456"
```

### Using the InitNornir function

```python
from nornir import InitNornir

nr = InitNornir(
    inventory={
        "plugin":"NBInventory",
        "options": {
            "nb_url": "https://netbox.local",
            "nb_token": "123_NETBOX_API_TOKEN_456"
        }
    }
)
```

```python
from nornir import InitNornir

nr = InitNornir(
    inventory={
        "plugin":"NetBoxInventory2",
        "options": {
            "nb_url": "https://netbox.local",
            "nb_token": "123_NETBOX_API_TOKEN_456"
        }
    }
)
```

### NBInventory arguments

```
Arguments:
    nb_url: NetBox url, defaults to http://localhost:8080.
        You can also use env variable NB_URL
    nb_token: NetBox token. You can also use env variable NB_TOKEN
    use_slugs: Whether to use slugs or not
    ssl_verify: Enable/disable certificate validation or provide path to CA bundle file
    flatten_custom_fields: Whether to assign custom fields directly to the host or not
    filter_parameters: Key-value pairs to filter down hosts
```

### NetBoxInventory2 arguments

```
Environment Variables:
    * ``NB_URL``: Corresponds to nb_url argument
    * ``NB_TOKEN``: Corresponds to nb_token argument
Arguments:
    nb_url: NetBox url (defaults to ``http://localhost:8080``)
    nb_token: NetBox API token
    ssl_verify: Enable/disable certificate validation or provide path to CA bundle file
        (defaults to True)
    flatten_custom_fields: Assign custom fields directly to the host's data attribute
        (defaults to False)
    filter_parameters: Key-value pairs that allow you to filter the NetBox inventory.
    include_vms: Get virtual machines from NetBox as well as devices.
        (defaults to False)
    use_platform_slug: Use the NetBox platform slug for the platform attribute of a Host
        (defaults to False)
    use_platform_napalm_driver: Use the Netbox platform napalm driver setting for the platform attribute of a Host
        (defaults to False)
```

Only one of use_platform_slug and use_platform_napalm_driver can be set to true.

# Useful Links

- [nornir_netbox documentation](https://nornir-netbox.readthedocs.io)
- [Nornir](https://github.com/nornir-automation/nornir)
- [Nornir Discourse Group](https://nornir.discourse.group)
- [An Introduction to Nornir Blog](https://pynet.twb-tech.com/blog/nornir/intro.html)
- [NetBox](https://github.com/netbox-community/netbox.git)
- [NetBox documentation](https://netbox.readthedocs.io/)

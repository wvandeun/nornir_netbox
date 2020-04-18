[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)
[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

# nornir_netbox

[NetBox](https://github.com/netbox-community/netbox) inventory plugin for [Nornir](https://github.com/nornir-automation/nornir)

The NetBox inventory plugin exposes 2 inventory classes for usage.
- `NBInventory` is deprecated and should not be used anymore, it is still available for backwards compatibility only
- `NetboxInventory2` is the recommended Netbox inventory plugin. It provides some extra functionality such as exposing all Netbox device attributes to the Nonir Host through the data attribute. It is the recommended plugin to use. All feature development will only take place on this plugin.

## Install

The recommended way to install nornir_netbox is via pip or poetry.

```bash
pip install git+https://github.com/wvandeun/nornir_netbox.git
```

```bash
poetry add git+https://github.com/wvandeun/nornir_netbox.git
```

## Example usage

### Using the Nornir configuration file

```yaml
---
inventory:
  plugin: nornir_netbox.inventory.NBInventory
  options:
    nb_url: "https://netbox.local"
	nb_token: "123_NETBOX_API_TOKEN_456"
```

```yaml
---
inventory:
  plugin: nornir_netbox.inventory.NetboxInventory2
  options:
    nb_url: "https://netbox.local"
	nb_token: "123_NETBOX_API_TOKEN_456"
```

### Using the InitNornir function

```python
>>> from nornir import InitNornir
>>> InitNornir(
...	    inventory={
...		    "plugin":"nornir_netbox.inventory.NBInventory",
...		    "options": {
...		    	"nb_url": "https://netbox.local",
...		    	"nb_token": "123_NETBOX_API_TOKEN_456"
...		    }
...	    }
...	)
```

```python
>>> from nornir import InitNornir
>>> InitNornir(
...     inventory={
...		    "plugin":"nornir_netbox.inventory.NetboxInventory2",
...		    "options": {
...		    	"nb_url": "https://netbox.local",
...		    	"nb_token": "123_NETBOX_API_TOKEN_456"
...		    }
...	    }
...	)
```

# Useful Links

- [Nornir](https://github.com/nornir-automation/nornir)
- [Nornir Discourse Group](https://nornir.discourse.group)
- [An Introduction to Nornir Blog](https://pynet.twb-tech.com/blog/nornir/intro.html)
- [NetBox](https://github.com/netbox-community/netbox.git)
- [NetBox documentation](https://netbox.readthedocs.io/)

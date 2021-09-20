# Introduction

**nornir_netbox** is a [NetBox](https://github.com/netbox-community/netbox) inventory plugin for [Nornir](https://github.com/nornir-automation/nornir).

The plugin exposes 2 inventory classes for usage:

* `NBInventory` is the old version, which is deprecated. It doesn't receive future updates anymore. It is still there for backwards compatibility.
* `NetBoxInventory2` is the recommended NetBox inventory plugin. All future development will take place for this plugin.

## Quick start

The NetBoxInventory2 inventory plugin allows you to retrieve NetBox device and virtual machine inventory data.

Nornir Host objects will be created from the data in your NetBox database:

* the name will be set to the name defined in NetBox
* the hostname will be set to the primary ip address defined in NetBox, or to the name if the primary ip address is not defined
* the platform will be set to the platform defined for the device in NetBox
* all other attributes of a device/virtual machine object in NetBox will be stored under the data attribute of the Nornir Host 

Nornir Group objects will be created from specific device and virtual machine attributes in your NetBox database:
* groups will be created for the following attributes of devices and virtual machines:
  - site
  - platform
  - device_role (role for virtual machines)
  - device_type
  - manufacturer
* the name of the group will be formed by the combination of the name of the property and the slug of it's value, separated by a double underscore `attribute__slug` (for example a device with has its platform defined as `Cisco IOS`, for which the slug is `ios`. NetBoxInventory2 will create a group `platform__ios` and add the device to the group.)
* devices and virtual machines will be added to their respective groups
* defaults and groups files can then be used to define properties for devices or virtual machines (similar to to how Nornir's SimpleInventory plugin works)

### Installation

To install nornir_netbox, simply run this command:

```bash
python -m pip install nornir_netbox
```

Alternatively you can install nornir_netbox directly from source code.
nornir_netbox is developed on [Github](https://github.com/wvandeun/nornir_netbox). 

Cloning the repository using git:

```bash
git clone git://github.com/wvandeun/nornir_netbox.git
```

Once you have a copy of the source, you can install it in your own package, or install it into your site-packages easily:

```
cd nornir_netbox
python -m pip install .
```

### Using the NetBoxInventory2 plugin

```python
from nornir import InitNornir

nr = InitNornir(
    inventory={
        "plugin":"NetBoxInventory2",
        "options": {
            "nb_url": "https://netbox.local:8000",
            "nb_token": "1234567890"
        }
    }
)
```

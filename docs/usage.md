# Using NetBox as an inventory source

Before we can use NetBox as an inventory source, we need to know the following 2 properties:

* The URL of your NetBox instance
* A NetBox [API token](https://netbox.readthedocs.io/en/stable/rest-api/authentication/#tokens)

You can setup Nornir to leverage NetBoxInvetory2 as the inventory source in 2 ways:

* defining the inventory in Nornir's configuration `config.yaml` file
* defining the inventory in Nornir's `InitNornir` constructor

## Nornir configuration file

You can find more information about Nornir's configuration file in the [Nornir documentation](https://nornir.readthedocs.io/en/latest/configuration/index.html).

The relevant section of the configuration is the `inventory` section. In this section we will have to specify the plugin we want to use and the options to configure the plugin.

```yaml
---
inventory:
  plugin: NetBoxInventory2
  options:
    nb_url: https://netbox.local:8000
    nb_token: "1234567890"
```

We can then use the configuration file to initialise Nornir:

```python
from nornir import InitNornir

nr = InitNornir(config_file="config.yaml")
```

## Nornir constructor

We can achieve the same goal by using the Nornir `InitNornir` constructor. `InitNornir` accepts an inventory argument, which allows us to specify the inventory plugin to use.

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

## Configuration options

NetBoxInventory2 has the following configuration options that influence it's behaviour.

Configuration options can be set in the options attribute of the inventory configuration.

### NetBox URL

NetBox instance URL.

| name                 | nb\_url               |
|----------------------|-----------------------|
| type                 | string                |
| default              | http://localhost:8000 |
| required             | True                  |
| environment variable | NB\_URL               |

### NetBox API token

NetBox API token.

| name                 | nb\_token                                |
|----------------------|------------------------------------------|
| type                 | string                                   |
| default              | 0123456789abcdef0123456789abcdef01234567 |
| required             | True                                     |
| environment variable | NB\_TOKEN                                |

### Enable / disable SSL verification

Allows for enabling or disabling certificate validation, when using HTTPS.

Alternatively accepts a path the CA bundle file to use for certificate validation.

| name     | ssl\_verify |
|----------|-------------|
| type     | bool/string |
| default  | True        |
| required | False       |

### Flatten custom fields

This option allows you to "flatten" custom fields. By default a custom fields for a NetBox device or VM, will be stored in the custom_fields attribute of the data attribute of a Nornir host.

Enabling `flatten_custom_fields` will modify that behaviour, so that each custom field is stored direclty as an attibute of the dat attribute of a Host, which makes working with custom fields a little bit easier.

| flatten\_custom\_fields |                                                               |
|-------------------------|---------------------------------------------------------------|
| description             | Store host/vm custom fields directly in NetBox data attribute |
| type                    | bool                                                          |
| default                 | False                                                         |
| required                | False                                                         |

Example with `flatten_custom_fields` disabled
```bash
>>> pprint(nr.host["my_device"].data
{
...truncated...
	"custom_fields": {
		"cf_my_custom_field": "value"
	}
...truncated...
}
```

Example with `flatten_custom_fields` enabled
```bash
>>> pprint(nr.host["my_device"].data
{
...truncated...
	"cf_my_custom_field": "value"
...truncated...
}
```

### Filter parameters

Filter parameters allow you to filter the inventory data returned by thet NetBox API.

The NetBox API allows you to filter the returned data by attaching one or more query parameters to the request url. More information can be found in [NetBox's documentation](https://netbox.readthedocs.io/en/stable/rest-api/filtering/).

NetBoxInventory2 allows you to provide these query paramterers as key/value pairs using the `filter_parameters` option. This works the same way as passing url paramters to a HTTP request using the [Requests Python library](https://requests.readthedocs.io/en/master/user/quickstart/#passing-parameters-in-urls).

| name        | filter\_parmeters                                             |
|-------------|---------------------------------------------------------------|
| type        | dictionary                                                    |
| default     | None                                                          |
| required    | False                                                         |

*Example*: to filter the inventory for site `site1`, we would need the following:
```python
nr = InitNornir(
    inventory={
        "plugin": NetBoxInventory2,
        "options": {
            "nb_url": "http://netbox.local:8000",
            "nb_token": "1234567890",
            "filter_parameters": {"site": "site1"}
        }
    }
)
```

*Example*: to filter the inventory for site `site1` and platform `cisco_ios`, we would need the following:
```python
nr = InitNornir(
    inventory={
        "plugin": NetBoxInventory2,
        "options": {
            "nb_url": "http://netbox.local:8000",
            "nb_token": "1234567890",
            "filter_parameters": {
                "site": "site1",
                "platform": "cisco_ios",
            }
        }
    }
)
```

*Example*: to filter the inventory for site `site1` or site `site2` and platform `cisco_ios`, we would need the following:
```python
nr = InitNornir(
    inventory={
        "plugin": NetBoxInventory2,
        "options": {
            "nb_url": "http://netbox.local:8000",
            "nb_token": "1234567890",
            "filter_parameters": {
                "site": ["site1", "site2"],
                "platform": "cisco_ios",
            }
        }
    }
)
```

### Use platform slug

NetBox device/vm's have a platform attribute that indicates the type of operating system that is running on the device. This attribute is directly mappend to the Nornir Host's platform attribute, so that connection plugins understand which driver needs to be used to connect to the device.

By default the name attribute of a NetBox platform is mapped to the Nornir Host's platform. Use platform slug allows you to use the slug of the NetBox platform instead.

Whether or not you need to enable this option depends on how you defined your platforms in NetBox. Only one of use_platform_slug and use_platform_napalm_driver can be set as true.

| name        | use\_platform\_slug                                                            |
|-------------|---------------------------------------------------------------------------------|
| type        | bool                                                                            |
| default     | False                                                                           |
| required    | False                                                                           |


### Use platform NAPALM driver

Use platform NAPLAM driver works like use platform slugs, but uses the NAPLAM driver attibuted from the NetBox platform instead.

Whether or not you need to enable this option depends on how you defined your platforms in NetBox. Only one of use_platform_slug and use_platform_napalm_driver can be set as true.

| name        | use\_platform\_napalm\_driver                                                            |
|-------------|---------------------------------------------------------------------------------|
| type        | bool                                                                            |
| default     | False                                                                           |
| required    | False                                                                           |


### Include Virtual Machines

Enable this option to also create Nornir Hosts for virtual machines stored in the NetBox database.

| name     | include\_vms |
|----------|--------------|
| type     | bool         |
| default  | False        |
| required | False        |


### Defaults file

Path to file with the defaults definition. If the file doesn't exist, it will be skipped.
More information on on the defaults file can be found in [Nornir's documentation](https://nornir.readthedocs.io/en/latest/tutorial/inventory.html).

| name     | defaults\_file |
|----------|----------------|
| type     | str            |
| default  | "defaults.yaml |
| required | False          |

### Group file

Path to file with the groups definition. If the file doesn't exist, it will be skipped.
More information on on the groups file can be found in [Nornir's documentation](https://nornir.readthedocs.io/en/latest/tutorial/inventory.html).

| name     | group\_file  |
|----------|--------------|
| type     | str          |
| default  | "groups.yaml |
| required | False        |

### Ignore file permission errors

Ignore file defaults or group file permission errors. Enabling this option will continue loading the inventory when file permission errors are encountered for the defaults or group file.

| name     | ignore\_file\_permission\_errors |
|----------|----------------------|
| type     | bool                 |
| default  | False                |
| required | False                |

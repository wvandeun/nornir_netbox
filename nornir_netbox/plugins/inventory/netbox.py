import copy
import os
import warnings
from typing import Any, Dict, List, Optional, Union

from nornir.core.inventory import Hosts, Host, Inventory

import requests


class NBInventory:
    def __init__(
        self,
        nb_url: Optional[str] = None,
        nb_token: Optional[str] = None,
        use_slugs: bool = True,
        ssl_verify: Union[bool, str] = True,
        flatten_custom_fields: bool = True,
        filter_parameters: Optional[Dict[str, Any]] = {},
        **kwargs: Any,
    ) -> None:
        """
        NetBox plugin
        netbox.NBInventory is deprecated, use netbox.NetBoxInventory2 instead
        Arguments:
            nb_url: NetBox url, defaults to http://localhost:8080.
                You can also use env variable NB_URL
            nb_token: NetBox token. You can also use env variable NB_TOKEN
            use_slugs: Whether to use slugs or not
            ssl_verify: Enable/disable certificate validation or provide path to CA bundle file
            flatten_custom_fields: Whether to assign custom fields directly to the host or not
            filter_parameters: Key-value pairs to filter down hosts
        """
        msg = "netbox.NBInventory is deprecated, use netbox.NetBoxInventory2 instead"
        warnings.warn(msg, DeprecationWarning)

        self.base_url = nb_url or os.environ.get("NB_URL", "http://localhost:8080")
        nb_token = nb_token or os.environ.get(
            "NB_TOKEN", "0123456789abcdef0123456789abcdef01234567"
        )
        self.use_slugs = use_slugs
        self.flatten_custom_fields = flatten_custom_fields
        self.filter_parameters = filter_parameters

        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Token {nb_token}"})
        self.session.verify = ssl_verify

    def load(self) -> Inventory:

        url = f"{self.base_url}/api/dcim/devices/?limit=0"

        nb_devices: List[Dict[str, Any]] = []

        while url:
            r = self.session.get(url, params=self.filter_parameters)

            if not r.status_code == 200:
                raise ValueError(
                    f"Failed to get devices from NetBox instance {self.base_url}"
                )

            resp = r.json()
            nb_devices.extend(resp.get("results"))

            url = resp.get("next")

        hosts = Hosts()
        for device in nb_devices:

            data = {}
            data["serial"] = device.get("serial")
            data["vendor"] = (
                device.get("device_type", {}).get("manufacturer", {}).get("name")
            )
            data["asset_tag"] = device.get("asset_tag")

            if self.flatten_custom_fields:
                for key, value in device.get("custom_fields", {}).items():
                    data[key] = value
            else:
                data["custom_fields"] = device.get("custom_fields", {})

            platform = None
            if self.use_slugs:
                data["site"] = device.get("site", {}).get("slug")
                data["role"] = device.get("device_role", {}).get("slug")
                data["model"] = device.get("device_type", {}).get("slug")
                platform = (
                    device["platform"]["slug"]
                    if isinstance(device["platform"], dict)
                    else device["platform"]
                )
            else:
                data["site"] = device.get("site", {}).get("name")
                data["role"] = device.get("device_role")
                data["model"] = device.get("device_type")
                platform = (
                    device["platform"]["name"]
                    if isinstance(device["platform"], dict)
                    else device["platform"]
                )

            hostname = None
            if device.get("primary_ip"):
                hostname = device.get("primary_ip", {}).get("address", "").split("/")[0]
            else:
                if device.get("name") is not None:
                    hostname = device["name"]

            host = Host(
                name=device.get("name") or str(device.get("id")),
                hostname=hostname,
                platform=platform,
                data=data,
            )

            hosts[host.name] = host

        return Inventory(hosts=hosts)


class NetBoxInventory2:
    """
    Inventory plugin that uses `NetBox <https://github.com/netbox-community/netbox>`_ as backend.
    Note:
        Additional data provided by the NetBox devices API endpoint will be
        available through the NetBox Host data attribute.
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
    """

    def __init__(
        self,
        nb_url: Optional[str] = None,
        nb_token: Optional[str] = None,
        ssl_verify: Union[bool, str] = True,
        flatten_custom_fields: bool = False,
        filter_parameters: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        filter_parameters = filter_parameters or {}
        nb_url = nb_url or os.environ.get("NB_URL", "http://localhost:8080")
        nb_token = nb_token or os.environ.get(
            "NB_TOKEN", "0123456789abcdef0123456789abcdef01234567"
        )

        self.nb_url = nb_url
        self.flatten_custom_fields = flatten_custom_fields
        self.filter_parameters = filter_parameters

        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Token {nb_token}"})
        self.session.verify = ssl_verify

    def load(self) -> Inventory:

        url = f"{self.nb_url}/api/dcim/devices/?limit=0"
        nb_devices: List[Dict[str, Any]] = []

        while url:
            r = self.session.get(url, params=self.filter_parameters)

            if not r.status_code == 200:
                raise ValueError(
                    f"Failed to get devices from NetBox instance {self.nb_url}"
                )

            resp = r.json()
            nb_devices.extend(resp.get("results"))

            url = resp.get("next")

        hosts = Hosts()
        for device in nb_devices:

            data = copy.deepcopy(device)

            if self.flatten_custom_fields:
                for cf, value in device["custom_fields"].items():
                    data[cf] = value
                data.pop("custom_fields")

            hostname = None
            if device.get("primary_ip"):
                hostname = device.get("primary_ip", {}).get("address", "").split("/")[0]
            else:
                if device.get("name") is not None:
                    hostname = device["name"]

            platform = (
                device["platform"]["name"]
                if isinstance(device["platform"], dict)
                else device["platform"]
            )

            host = Host(
                name=device.get("name") or str(device.get("id")),
                hostname=hostname,
                platform=platform,
                data=data,
            )

            hosts[host.name] = host
        return Inventory(hosts=hosts)

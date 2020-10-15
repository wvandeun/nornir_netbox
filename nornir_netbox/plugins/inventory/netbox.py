import os
import warnings
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union
from typing import Type
from pathlib import Path

from nornir.core.inventory import ConnectionOptions
from nornir.core.inventory import Defaults
from nornir.core.inventory import Group
from nornir.core.inventory import Groups
from nornir.core.inventory import Host
from nornir.core.inventory import HostOrGroup
from nornir.core.inventory import Hosts
from nornir.core.inventory import Inventory
from nornir.core.inventory import ParentGroups

import requests
import ruamel.yaml


def _get_connection_options(data: Dict[str, Any]) -> Dict[str, ConnectionOptions]:
    cp = {}
    for cn, c in data.items():
        cp[cn] = ConnectionOptions(
            hostname=c.get("hostname"),
            port=c.get("port"),
            username=c.get("username"),
            password=c.get("password"),
            platform=c.get("platform"),
            extras=c.get("extras"),
        )
    return cp


def _get_defaults(data: Dict[str, Any]) -> Defaults:
    return Defaults(
        hostname=data.get("hostname"),
        port=data.get("port"),
        username=data.get("username"),
        password=data.get("password"),
        platform=data.get("platform"),
        data=data.get("data"),
        connection_options=_get_connection_options(data.get("connection_options", {})),
    )


def _get_inventory_element(
    typ: Type[HostOrGroup], data: Dict[str, Any], name: str, defaults: Defaults
) -> HostOrGroup:
    return typ(
        name=name,
        hostname=data.get("hostname"),
        port=data.get("port"),
        username=data.get("username"),
        password=data.get("password"),
        platform=data.get("platform"),
        data=data.get("data"),
        groups=data.get(
            "groups"
        ),  # this is a hack, we will convert it later to the correct type
        defaults=defaults,
        connection_options=_get_connection_options(data.get("connection_options", {})),
    )


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
        groups = Groups()
        defaults = Defaults()

        for device in nb_devices:

            serialized_device: Dict[Any, Any] = {}
            serialized_device["data"] = {}
            serialized_device["data"]["serial"] = device.get("serial")
            serialized_device["data"]["vendor"] = (
                device.get("device_type", {}).get("manufacturer", {}).get("name")
            )
            serialized_device["data"]["asset_tag"] = device.get("asset_tag")

            if self.flatten_custom_fields:
                for key, value in device.get("custom_fields", {}).items():
                    serialized_device["data"][key] = value
            else:
                serialized_device["data"]["custom_fields"] = device.get(
                    "custom_fields", {}
                )

            if self.use_slugs:
                serialized_device["data"]["site"] = device.get("site", {}).get("slug")
                serialized_device["data"]["role"] = device.get("device_role", {}).get(
                    "slug"
                )
                serialized_device["data"]["model"] = device.get("device_type", {}).get(
                    "slug"
                )
                serialized_device["platform"] = (
                    device["platform"]["slug"]
                    if isinstance(device["platform"], dict)
                    else device["platform"]
                )
            else:
                serialized_device["data"]["site"] = device.get("site", {}).get("name")
                serialized_device["data"]["role"] = device.get("device_role")
                serialized_device["data"]["model"] = device.get("device_type")
                serialized_device["platform"] = (
                    device["platform"]["name"]
                    if isinstance(device["platform"], dict)
                    else device["platform"]
                )

            serialized_device["hostname"] = None
            if device.get("primary_ip"):
                serialized_device["hostname"] = (
                    device.get("primary_ip", {}).get("address", "").split("/")[0]
                )
            else:
                if device.get("name") is not None:
                    serialized_device["hostname"] = device["name"]

            name = device.get("name") or str(device.get("id"))

            hosts[name] = _get_inventory_element(
                Host, serialized_device, name, defaults
            )

        return Inventory(hosts=hosts, groups=groups, defaults=defaults)


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
        include_vms: Get virtual machines from NetBox as well as devices.
            (defaults to False)
        use_platform_slug: Use the NetBox platform slug for the platform attribute of a Host
            (defaults to False)
    """

    def __init__(
        self,
        nb_url: Optional[str] = None,
        nb_token: Optional[str] = None,
        ssl_verify: Union[bool, str] = True,
        flatten_custom_fields: bool = False,
        filter_parameters: Optional[Dict[str, Any]] = None,
        include_vms: bool = False,
        use_platform_slug: bool = False,
        group_file: str = "groups.yaml",
        defaults_file: str = "defaults.yaml",
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
        self.include_vms = include_vms
        self.use_platform_slug = use_platform_slug

        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Token {nb_token}"})
        self.session.verify = ssl_verify
        self.group_file = Path(group_file).expanduser()
        self.defaults_file = Path(defaults_file).expanduser()

    @staticmethod
    def _extract_device_groups(device):
        extract_group_attributes = [
            {"name": "site", "path": ["site", "slug"]},
            {"name": "platform", "path": ["platform"]}, # older netbox versions
            {"name": "platform", "path": ["platform", "slug"]},
            {"name": "device_role", "path": ["device_role", "slug"]},
            {"name": "manufacturer", "path": ["device_type", "manufacturer", "slug"]},
            {"name": "device_type", "path": ["device_type", "slug"]}
        ] 

        groups = []
        for group in extract_group_attributes:
            data = device
            for hop in group.get("path", []):
                v = data.get(hop)
                if isinstance(v, dict):
                    data = v
                elif isinstance(v, str) and group.get("path", [])[-1] == hop:
                    groups.append(f"{group.get('name', '')}__{v}")
                else:
                    # Unable to extract group
                    continue
        return groups

    def load(self) -> Inventory:
        yml = ruamel.yaml.YAML(typ="safe")

        nb_devices: List[Dict[str, Any]] = []

        nb_devices = self._get_resources(
            url=f"{self.nb_url}/api/dcim/devices/?limit=0",
            params=self.filter_parameters,
        )

        if self.include_vms:
            nb_devices.extend(
                self._get_resources(
                    url=f"{self.nb_url}/api/virtualization/virtual-machines/?limit=0",
                    params=self.filter_parameters,
                )
            )

        hosts = Hosts()
        groups = Groups()
        defaults = Defaults()

        if self.defaults_file.exists():
            with self.defaults_file.open("r") as f:
                defaults_dict = yml.load(f) or {}
            defaults = _get_defaults(defaults_dict)

        if self.group_file.exists():
            with self.group_file.open("r") as f:
                groups_dict = yml.load(f) or {}

            for n, g in groups_dict.items():
                groups[n] = _get_inventory_element(Group, g, n, defaults)

            for g in groups.values():
                g.groups = ParentGroups([groups[g] for g in g.groups])

        for device in nb_devices:
            serialized_device: Dict[Any, Any] = {}
            serialized_device["data"] = device

            if self.flatten_custom_fields:
                for cf, value in device["custom_fields"].items():
                    serialized_device["data"][cf] = value
                serialized_device["data"].pop("custom_fields")

            hostname = None
            if device.get("primary_ip"):
                hostname = device.get("primary_ip", {}).get("address", "").split("/")[0]
            else:
                if device.get("name") is not None:
                    hostname = device["name"]
            serialized_device["hostname"] = hostname

            if isinstance(device["platform"], dict) and self.use_platform_slug:
                platform = device["platform"].get("slug")
            elif isinstance(device["platform"], dict):
                platform = device["platform"].get("name")
            else:
                platform = device["platform"]

            serialized_device["platform"] = platform

            name = serialized_device["data"].get("name") or str(
                serialized_device["data"].get("id")
            )

            hosts[name] = _get_inventory_element(
                Host, serialized_device, name, defaults
            )

            groups_extracted = self._extract_device_groups(device)

            for group in groups_extracted:
                if group not in groups.keys():
                    groups[group] = _get_inventory_element(Group, {}, group, defaults)

            hosts[name].groups = ParentGroups([groups[g] for g in groups_extracted])

        return Inventory(hosts=hosts, groups=groups, defaults=defaults)

    def _get_resources(self, url: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:

        resources: List[Dict[str, Any]] = []

        while url:
            r = self.session.get(url, params=params)

            if not r.status_code == 200:
                raise ValueError(
                    f"Failed to get data from NetBox instance {self.nb_url}"
                )

            resp = r.json()
            resources.extend(resp.get("results"))

            url = resp.get("next")

        return resources

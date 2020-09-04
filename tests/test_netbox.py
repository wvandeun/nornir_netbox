import json
import os

from nornir_netbox.plugins.inventory.netbox import NBInventory
from nornir_netbox.plugins.inventory.netbox import NetBoxInventory2

# We need import below to load fixtures
import pytest  # noqa


BASE_PATH = os.path.dirname(__file__)
VERSIONS = ["2.3.5", "2.8.9"]


def get_inv(requests_mock, plugin, pagination, version, **kwargs):
    if not pagination:
        with open(f"{BASE_PATH}/mocked/{version}/devices.json", "r") as f:
            requests_mock.get(
                "http://localhost:8080/api/dcim/devices/?limit=0",
                json=json.load(f),
                headers={"Content-type": "application/json"},
            )
    else:
        for offset in range(3):
            with open(f"{BASE_PATH}/mocked/{version}/devices-{offset}.json", "r") as f:
                url = "http://localhost:8080/api/dcim/devices/?limit=0"
                requests_mock.get(
                    f"{url}&offset={offset}" if offset else url,
                    json=json.load(f),
                    headers={"Content-type": "application/json"},
                )
    return plugin().load()


class TestNBInventory(object):
    plugin = NBInventory

    @pytest.mark.parametrize("version", VERSIONS)
    def test_inventory(self, requests_mock, version):
        inv = get_inv(requests_mock, self.plugin, False, version)
        with open(
            f"{BASE_PATH}/{self.plugin.__name__}/{version}/expected.json", "r"
        ) as f:
            expected = json.load(f)
        assert expected == inv.dict()

    @pytest.mark.parametrize("version", VERSIONS)
    def test_inventory_pagination(self, requests_mock, version):
        inv = get_inv(requests_mock, self.plugin, False, version)
        with open(
            f"{BASE_PATH}/{self.plugin.__name__}/{version}/expected.json", "r"
        ) as f:
            expected = json.load(f)
        assert expected == inv.dict()


class TestNetBoxInventory2(TestNBInventory):
    plugin = NetBoxInventory2

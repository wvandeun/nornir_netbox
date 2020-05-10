import json
import os

from nornir_netbox.inventory import NBInventory
from nornir_netbox.inventory import NetboxInventory2

# We need import below to load fixtures
import pytest  # noqa


BASE_PATH = os.path.dirname(__file__)


def get_inv(requests_mock, plugin, pagination, **kwargs):
    if not pagination:
        with open(f"{BASE_PATH}/mocked/devices.json", "r") as f:
            requests_mock.get(
                "http://localhost:8080/api/dcim/devices/?limit=0",
                json=json.load(f),
                headers={"Content-type": "application/json"},
            )
    else:
        for offset in range(3):
            with open(f"{BASE_PATH}/mocked/devices-{offset}.json", "r") as f:
                url = "http://localhost:8080/api/dcim/devices/?limit=0"
                requests_mock.get(
                    f"{url}&offset={offset}" if offset else url,
                    json=json.load(f),
                    headers={"Content-type": "application/json"},
                )
    return plugin().load()


class TestNBInventory(object):
    plugin = NBInventory

    def test_inventory(self, requests_mock):
        inv = get_inv(requests_mock, self.plugin, False)
        with open(f"{BASE_PATH}/{self.plugin.__name__}/expected.json", "r") as f:
            expected = json.load(f)
        assert expected == inv.dict()

    def test_inventory_pagination(self, requests_mock):
        inv = get_inv(requests_mock, self.plugin, False)
        with open(f"{BASE_PATH}/{self.plugin.__name__}/expected.json", "r") as f:
            expected = json.load(f)
        assert expected == inv.dict()


class TestNetboxInventory2(TestNBInventory):
    plugin = NetboxInventory2

import json
import os

from typing import Any
from typing import Type
from typing import Union

from nornir.core.inventory import Inventory
from nornir_netbox.plugins.inventory.netbox import NBInventory
from nornir_netbox.plugins.inventory.netbox import NetBoxInventory2

# We need import below to load fixtures
import pytest  # noqa

from requests_mock import Mocker


BASE_PATH = os.path.dirname(__file__)
VERSIONS = ["2.3.5", "2.8.9"]


def _create_mock(
    requests_mock: Mocker,
    pagination: bool,
    version: str,
    application: str,
    resource: str,
) -> None:
    """initialises mock objects for testcase"""
    if not pagination:
        with open(f"{BASE_PATH}/mocked/{version}/{resource}.json", "r") as f:
            requests_mock.get(
                f"http://localhost:8080/api/{application}/{resource}/?limit=0",
                json=json.load(f),
                headers={"Content-type": "application/json"},
            )
    else:
        for offset in range(3):
            with open(
                f"{BASE_PATH}/mocked/{version}/{resource}-{offset}.json", "r"
            ) as f:
                url = f"http://localhost:8080/api/{application}/{resource}/?limit=0"
                requests_mock.get(
                    f"{url}&offset={offset}" if offset else url,
                    json=json.load(f),
                    headers={"Content-type": "application/json"},
                )


def get_inv(
    requests_mock: Mocker,
    plugin: Type[Union[NBInventory, NetBoxInventory2]],
    pagination: bool,
    version: str,
    **kwargs: Any,
) -> Inventory:
    _create_mock(requests_mock, pagination, version, "dcim", "devices")
    _create_mock(requests_mock, False, version, "dcim", "platforms")
    if kwargs.get("include_vms", None):
        _create_mock(
            requests_mock, pagination, version, "virtualization", "virtual-machines"
        )
    return plugin(**kwargs).load()


class BaseTestInventory(object):
    plugin: Type[Union[NBInventory, NetBoxInventory2]]

    @pytest.mark.parametrize("version", VERSIONS)
    def test_inventory(self, requests_mock: Mocker, version: str) -> None:
        inv = get_inv(requests_mock, self.plugin, False, version)
        with open(
            f"{BASE_PATH}/{self.plugin.__name__}/{version}/expected.json", "r"
        ) as f:
            expected = json.load(f)
        assert expected == inv.dict()

    @pytest.mark.parametrize("version", VERSIONS)
    def test_inventory_pagination(self, requests_mock: Mocker, version: str) -> None:
        inv = get_inv(requests_mock, self.plugin, True, version)
        with open(
            f"{BASE_PATH}/{self.plugin.__name__}/{version}/expected.json", "r"
        ) as f:
            expected = json.load(f)
        assert expected == inv.dict()


class TestNBInventory(BaseTestInventory):
    plugin = NBInventory


class TestNetBoxInventory2(BaseTestInventory):
    plugin = NetBoxInventory2

    # only on NetBoxInventory2 and NetBox 2.8.9
    @pytest.mark.parametrize("version", ["2.8.9"])
    def test_inventory_include_vms(self, requests_mock: Mocker, version: str) -> None:
        inv = get_inv(requests_mock, self.plugin, False, version, include_vms=True)
        with open(
            f"{BASE_PATH}/{self.plugin.__name__}/{version}/vms-expected.json", "r"
        ) as f:
            expected = json.load(f)
        assert expected == inv.dict()

    @pytest.mark.parametrize("version", ["2.8.9"])
    def test_inventory_include_vms_pagination(
        self, requests_mock: Mocker, version: str
    ) -> None:
        inv = get_inv(requests_mock, self.plugin, True, version, include_vms=True)
        with open(
            f"{BASE_PATH}/{self.plugin.__name__}/{version}/vms-expected.json", "r"
        ) as f:
            expected = json.load(f)
        assert expected == inv.dict()

    @pytest.mark.parametrize("version", ["2.8.9"])
    def test_inventory_use_platform_slug(
        self, requests_mock: Mocker, version: str
    ) -> None:
        inv = get_inv(
            requests_mock, self.plugin, False, version, use_platform_slug=True
        )
        with open(
            f"{BASE_PATH}/{self.plugin.__name__}/{version}/expected_use_platform_slug.json",
            "r",
        ) as f:
            expected = json.load(f)
        assert expected == inv.dict()

    @pytest.mark.parametrize("version", ["2.8.9"])
    def test_inventory_use_platform_slug_include_vms(
        self, requests_mock: Mocker, version: str
    ) -> None:
        inv = get_inv(
            requests_mock,
            self.plugin,
            False,
            version,
            use_platform_slug=True,
            include_vms=True,
        )
        with open(
            f"{BASE_PATH}/{self.plugin.__name__}/{version}/vms-expected_use_platform_slug.json",
            "r",
        ) as f:
            expected = json.load(f)
        assert expected == inv.dict()

    @pytest.mark.parametrize("version", ["2.8.9"])
    def test_inventory_use_platform_napalm_driver(
        self, requests_mock: Mocker, version: str
    ) -> None:
        inv = get_inv(
            requests_mock, self.plugin, False, version, use_platform_napalm_driver=True
        )
        with open(
            f"{BASE_PATH}/{self.plugin.__name__}/{version}/expected_use_platform_napalm_driver.json",  # noqa: E501
            "r",
        ) as f:
            expected = json.load(f)
        assert expected == inv.dict()

    @pytest.mark.parametrize("version", VERSIONS)
    def test_inventory_with_defaults_file(
        self, requests_mock: Mocker, version: str
    ) -> None:
        inv = get_inv(
            requests_mock,
            self.plugin,
            False,
            version,
            defaults_file=f"{BASE_PATH}/data/defaults.yaml",
        )

        with open(
            f"{BASE_PATH}/{self.plugin.__name__}/{version}/expected-defaults.json", "r"
        ) as f:
            expected = json.load(f)

        assert expected == inv.dict()
        assert expected["defaults"]["username"] == inv.hosts["1-Core"].username
        assert expected["defaults"]["password"] == inv.hosts["2-Distribution"].password
        assert expected["defaults"]["data"]["domain"] == inv.hosts["3-Access"]["domain"]

    @pytest.mark.parametrize("version", VERSIONS)
    def test_inventory_with_groups_file(
        self, requests_mock: Mocker, version: str
    ) -> None:
        inv = get_inv(
            requests_mock,
            self.plugin,
            False,
            version,
            group_file=f"{BASE_PATH}/data/groups.yaml",
        )

        with open(
            f"{BASE_PATH}/{self.plugin.__name__}/{version}/expected-group.json", "r"
        ) as f:
            expected = json.load(f)

        assert expected == inv.dict()
        assert (
            expected["groups"]["platform__ios"]["username"]
            == inv.hosts["3-Access"].username
        )
        assert (
            expected["groups"]["platform__ios"]["password"]
            == inv.hosts["3-Access"].password
        )
        assert (
            expected["groups"]["platform__ios"]["data"]["domain"]
            == inv.hosts["3-Access"]["domain"]
        )
        assert (
            expected["groups"]["platform__junos"]["username"]
            == inv.hosts["1-Core"].username
        )
        assert (
            expected["groups"]["platform__junos"]["password"]
            == inv.hosts["1-Core"].password
        )
        assert (
            expected["groups"]["platform__junos"]["data"]["domain"]
            == inv.hosts["4"]["domain"]
        )

    @pytest.mark.parametrize("version", ["2.8.9"])
    def test_inventory_multiple_platform_sources_raises_exception(
        self, requests_mock: Mocker, version: str
    ) -> None:
        with pytest.raises(ValueError):
            inv = get_inv(
                requests_mock,
                self.plugin,
                False,
                version,
                use_platform_slug=True,
                use_platform_napalm_driver=True,
            )
            assert inv

    @pytest.mark.parametrize("version", VERSIONS)
    def test_inventory_with_defaults_and_groups_file(
        self, requests_mock: Mocker, version: str
    ) -> None:
        inv = get_inv(
            requests_mock,
            self.plugin,
            False,
            version,
            defaults_file=f"{BASE_PATH}/data/defaults.yaml",
            group_file=f"{BASE_PATH}/data/groups.yaml",
        )

        with open(
            f"{BASE_PATH}/{self.plugin.__name__}/{version}/expected-defaults-group.json",
            "r",
        ) as f:
            expected = json.load(f)

        assert expected == inv.dict()
        assert (
            expected["groups"]["platform__ios"]["username"]
            == inv.hosts["3-Access"].username
        )
        assert (
            expected["groups"]["platform__ios"]["password"]
            == inv.hosts["3-Access"].password
        )
        assert (
            expected["groups"]["platform__ios"]["data"]["domain"]
            == inv.hosts["3-Access"]["domain"]
        )
        assert (
            expected["groups"]["platform__junos"]["username"]
            == inv.hosts["1-Core"].username
        )
        assert (
            expected["groups"]["platform__junos"]["password"]
            == inv.hosts["1-Core"].password
        )
        assert (
            expected["groups"]["platform__junos"]["data"]["domain"]
            == inv.hosts["4"]["domain"]
        )
        assert expected["defaults"]["username"] == inv.hosts["2-Distribution"].username
        assert expected["defaults"]["password"] == inv.hosts["2-Distribution"].password
        assert (
            expected["defaults"]["data"]["domain"]
            == inv.hosts["2-Distribution"]["domain"]
        )

    @pytest.mark.parametrize("version", VERSIONS)
    def test_inventory_with_empty_defaults_file(
        self, requests_mock: Mocker, version: str
    ) -> None:
        "test loading inventory with empty defaults file, should not raise an exception"

        inv = get_inv(
            requests_mock,
            self.plugin,
            False,
            version,
            defaults_file=f"{BASE_PATH}/data/defaults-empty.yaml",
        )

        with open(
            f"{BASE_PATH}/{self.plugin.__name__}/{version}/expected.json", "r"
        ) as f:
            expected = json.load(f)

        assert expected == inv.dict()

    @pytest.mark.parametrize("version", VERSIONS)
    def test_inventory_with_empty_groups_file(
        self, requests_mock: Mocker, version: str
    ) -> None:
        "test loading inventory with empty groups file, should not raise an exception"

        inv = get_inv(
            requests_mock,
            self.plugin,
            False,
            version,
            groups_file=f"{BASE_PATH}/data/groups-empty.yaml",
        )

        with open(
            f"{BASE_PATH}/{self.plugin.__name__}/{version}/expected.json", "r"
        ) as f:
            expected = json.load(f)

        assert expected == inv.dict()

    @pytest.mark.parametrize("version", VERSIONS)
    def test_inventory_with_empty_defaults_and_groups_file(
        self, requests_mock: Mocker, version: str
    ) -> None:
        "test loading inventory with empty defaults and groups file, should not raise an exception"
        inv = get_inv(
            requests_mock,
            self.plugin,
            False,
            version,
            defaults_file=f"{BASE_PATH}/data/defaults-empty.yaml",
            groups_file=f"{BASE_PATH}/data/groups-empty.yaml",
        )

        with open(
            f"{BASE_PATH}/{self.plugin.__name__}/{version}/expected.json", "r"
        ) as f:
            expected = json.load(f)

        assert expected == inv.dict()

    @pytest.mark.parametrize("version", VERSIONS)
    def test_inventory_with_defaults_file_permission_error_raises_exception(
        self, tmp_path, requests_mock: Mocker, version: str
    ) -> None:
        "test loading inventory with defaults file with bad permissions, should raise an exception"

        defaults_file = tmp_path / "defaults-000.yaml"
        defaults_file.touch(mode=0, exist_ok=True)

        with pytest.raises(PermissionError):
            inv = get_inv(
                requests_mock,
                self.plugin,
                False,
                version,
                defaults_file=defaults_file,
                group_file=f"{BASE_PATH}/data/group.yaml",
            )

    @pytest.mark.parametrize("version", VERSIONS)
    def test_inventory_with_group_file_permission_error_raises_exception(
        self, tmp_path, requests_mock: Mocker, version: str
    ) -> None:
        "test loading inventory with group file that has bad permissions, should raise an exception"

        group_file = tmp_path / "group-000.yaml"
        group_file.touch(mode=0, exist_ok=True)

        with pytest.raises(PermissionError):
            inv = get_inv(
                requests_mock,
                self.plugin,
                False,
                version,
                defaults_file=f"{BASE_PATH}/data/defaults.yaml",
                group_file=group_file,
            )

    @pytest.mark.parametrize("version", VERSIONS)
    def test_inventory_with_defaults_file_ignore_permission_error(
        self, tmp_path, requests_mock: Mocker, version: str
    ) -> None:
        "test loading inventory with defaults file with bad permissions, should not raise an exception"

        defaults_file = tmp_path / "defaults-000.yaml"
        defaults_file.touch(mode=0, exist_ok=True)

        with open(
            f"{BASE_PATH}/{self.plugin.__name__}/{version}/expected.json", "r"
        ) as f:
            expected = json.load(f)

        inv = get_inv(
            requests_mock,
            self.plugin,
            False,
            version,
            defaults_file=defaults_file,
            group_file=f"{BASE_PATH}/data/group.yaml",
            ignore_file_permission_errors=True,
        )

        assert inv.dict() == expected

    @pytest.mark.parametrize("version", VERSIONS)
    def test_inventory_with_group_file_ignore_permission_error(
        self, tmp_path, requests_mock: Mocker, version: str
    ) -> None:
        "test loading inventory with group file with bad permissions, should not raise an exception"

        group_file = tmp_path / "group-000.yaml"
        group_file.touch(mode=0, exist_ok=True)

        with open(
            f"{BASE_PATH}/{self.plugin.__name__}/{version}/expected-defaults.json", "r"
        ) as f:
            expected = json.load(f)

        inv = get_inv(
            requests_mock,
            self.plugin,
            False,
            version,
            group_file=group_file,
            defaults_file=f"{BASE_PATH}/data/defaults.yaml",
            ignore_file_permission_errors=True,
        )

        assert inv.dict() == expected

    @pytest.mark.parametrize("version", VERSIONS)
    def test_inventory_with_ignore_file_errors_and_bad_permissions_on_files(
        self, tmp_path, requests_mock: Mocker, version: str
    ) -> None:
        "test loading inventory with bad permissions on both the defaults and groups file with"
        "ignore_file_errors, should not raise an exception"

        # Set the permissions on the files
        defaults_file = tmp_path / "defaults-000.yaml"
        defaults_file.touch(mode=0, exist_ok=True)
        group_file = tmp_path / "group-000.yaml"
        group_file.touch(mode=0, exist_ok=True)

        inv = get_inv(
            requests_mock,
            self.plugin,
            False,
            version,
            ignore_file_permission_errors=True,
            defaults_file=defaults_file,
            group_file=group_file,
        )

        with open(
            f"{BASE_PATH}/{self.plugin.__name__}/{version}/expected.json", "r"
        ) as f:
            expected = json.load(f)

        # Reset the permissions to the default
        os.chmod(f"{BASE_PATH}/data/defaults-perms.yaml", 0o644)
        os.chmod(f"{BASE_PATH}/data/groups-perms.yaml", 0o644)

        assert expected == inv.dict()

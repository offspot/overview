# where to write the resulting YAML file to
YAML_CONFIG_PATH = "conf.yaml"

#
# SETTINGS
#
#
NAME = "My Hotspot"
# main domain to access your domain: xxx.hotspot. ASCII, numbers and dash
DOMAIN = "my-kiwix"
# SSID: max 32 chars. Forbidden chars: ^ ! # ; + \ / " \t
SSID = "My SSID"
# PASS: max 64 chars. No ASCII control characters. Leave empty for Open network
PASSPHRASE = ""
TIMEZONE = "UTC"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin-password"
BRANDING_HORIZONTAL_LOGO_PATH = ""
BRANDING_SQUARE_LOGO_PATH = ""

#
# CONTENT SELECTION
#
# Title IDs for your ZIM files
ZIM_TITLES = [
    "openZIM:wikipedia_en_climate_change:nopic",
    "openZIM:raspberrypi.stackexchange.com_en_all:all",
]
# Package IDs from
# https:/github.com/offspot/offspot-config/blob/main/src/offspot_config/catalog.json
PACKAGES = [
    "file-manager.offspot.kiwix.org",
]
# URL to a ZIP file which content will be served in the files-resources app
FILES_APP_ZIP_URL = ""

#
# OPTIONS
#
# available at metrics.<> and show usage metrics over time.
# useless (and wrong) if you dont have an hardware clock and Pi is offline
ADD_METRICS = True
# available at clock.<> allows you to set time/date of Pi.
# mostly useful if you have an hardware clock and you're offline
ADD_HWCLOCK_MGMT = True
# includes Kiwix readers to the dashboard for downloads
ADD_READERS = True

### End of basic configuration
# top-level domain to use for your hotspot's domains (my-kiwix.hotspot)
TLD = "hotspot"
# base image to use. update if theres a newer version available
BASE_IMAGE_URL = "1.2.1"
# the actual rootfs size inside the base image. there's a script to find the value
BASE_IMAGE_ROOTFS_SIZE = 2663383040
KIWIX_ZIM_MIRROR_URL = "https://mirror.download.kiwix.org/zim/"
KIWIX_LIBRARY_URL = "https://library.kiwix.org"

import datetime
import re
from pathlib import Path

import requests
import xmltodict
from offspot_config.builder import (
    BRANDING_PATH,
    AppPackage,
    ConfigBuilder,
    FilesPackage,
)
from offspot_config.catalog import app_catalog
from offspot_config.inputs.base import BaseConfig
from offspot_config.utils.dashboard import Link, Reader
from offspot_config.utils.download import get_online_rsc_size
from offspot_config.utils.misc import b64_encode
from offspot_config.zim import ZimPackage


def get_zim_package(ident):
    publisher, name, flavour = ident.split(":", 2)
    resp = requests.get(
        f"{KIWIX_LIBRARY_URL}/catalog/v2/entries",
        params={"name": name},
        timeout=30,
    )
    resp.raise_for_status()
    catalog = xmltodict.parse(resp.content)

    if "feed" not in catalog:
        raise ValueError("Malformed OPDS response")
    if not int(catalog["feed"]["totalResults"]):
        raise OSError("Catalog has no entry; probably misbehaving")

    entries = catalog["feed"]["entry"]
    if not isinstance(entries, list):
        entries = [entries]

    for entry in entries:
        if not entry.get("name"):
            continue

        links = {link["@type"]: link for link in entry["link"]}
        version = datetime.datetime.fromisoformat(
            re.sub(r"[A-Z]$", "", entry["updated"])
        ).strftime("%Y-%m-%d")
        flavour_ = entry.get("flavour") or ""
        publisher_ = entry.get("publisher", {}).get("name") or ""
        name_ = entry["name"]

        if name == name_ and publisher == publisher_ and flavour == flavour_:
            if icon_path := links.get("image/png;width=48;height=48;scale=1", {}).get(
                "@href", ""
            ):
                icon_url = f"{KIWIX_LIBRARY_URL}{icon_path}"
            else:
                icon_url = None

            return ZimPackage(
                ident=ident,
                kind="zim",
                domain="kiwix",
                title=entry["title"],
                description=entry["summary"],
                tags=list(set(entry["tags"].split(";"))),
                languages=list(set(entry["language"].split(","))) or ["eng"],
                icon_url=icon_url,
                name=name,
                flavour=flavour,
                version=version,
                download_url=re.sub(
                    r".meta4$", "", links["application/x-zim"]["@href"]
                ),
                download_size=int(links["application/x-zim"]["@length"]),
            )
    raise ValueError(f"Unable to find Catalog entry for {ident}")


def get_builder():
    builder = ConfigBuilder(
        base=BaseConfig(
            source=BASE_IMAGE_URL,
            rootfs_size=BASE_IMAGE_ROOTFS_SIZE,
        ),
        name=NAME,
        domain=DOMAIN,
        welcome_domain="goto.kiwix",
        tld=TLD,
        ssid=SSID,
        passphrase=PASSPHRASE or None,
        timezone=TIMEZONE,
        environ={
            "ADMIN_USERNAME": ADMIN_USERNAME,
            "ADMIN_PASSWORD": ADMIN_PASSWORD,
        },
        write_config=True,
        kiwix_zim_mirror=KIWIX_ZIM_MIRROR_URL,
    )

    # add branding
    if BRANDING_HORIZONTAL_LOGO_PATH:
        print(f"> Adding branding file from {BRANDING_HORIZONTAL_LOGO_PATH}")
        logo = Path(BRANDING_HORIZONTAL_LOGO_PATH)
        builder.add_file(
            url_or_content=b64_encode(logo.read_bytes()),
            to=str(BRANDING_PATH.joinpath("horizontal-logo-light.png")),
            via="base64",
            size=logo.stat().st_size,
            is_url=False,
        )
        del logo

    if BRANDING_SQUARE_LOGO_PATH:
        print(f"> Adding branding file from {BRANDING_SQUARE_LOGO_PATH}")
        logo = Path(BRANDING_SQUARE_LOGO_PATH)
        builder.add_file(
            url_or_content=b64_encode(logo.read_bytes()),
            to=str(BRANDING_PATH.joinpath("square-logo-light.png")),
            via="base64",
            size=logo.stat().st_size,
            is_url=False,
        )
        del logo

    # dashboard links
    links = []
    if ADD_METRICS:
        links.append(Link("Metrics", "//metrics.${FQDN}"))

    readers = None
    if ADD_READERS:
        print("> Adding Readers")
        readers = [
            Reader(
                platform="windows",
                download_url="https://mirror.download.kiwix.org/release/kiwix-desktop/kiwix-desktop_windows_x64_2.4.1.zip",
                filename="kiwix-desktop_windows_x64_2.4.1.zip",
                size=132065749,
            ),
            Reader(
                platform="android",
                download_url="https://mirror.download.kiwix.org/release/kiwix-android/kiwix-3.12.0.apk",
                filename="kiwix-3.12.0.apk",
                size=105761084,
            ),
            Reader(
                platform="macos",
                download_url="https://mirror.download.kiwix.org/release/kiwix-macos/kiwix-macos_3.7.1.dmg",
                filename="kiwix-macos_3.7.1.dmg",
                size=6392295,
            ),
            Reader(
                platform="linux",
                download_url="https://mirror.download.kiwix.org/release/kiwix-desktop/kiwix-desktop_x86_64_2.3.1-4.appimage",
                filename="kiwix-desktop_x86_64_2.3.1-4.appimage",
                size=146629824,
            ),
        ]

    print("> Adding Dashboard")
    builder.add_dashboard(allow_zim_downloads=True, readers=readers, links=links)
    print("> Adding Captive Portal")
    builder.add_captive_portal()
    print("> Adding Reverse-proxy")
    builder.add_reverseproxy()

    print("> Adding ZIMs")
    for zim_ident in ZIM_TITLES:
        print(f">  - Adding {zim_ident}")
        builder.add_zim(get_zim_package(zim_ident))

    print("> Adding Packages")
    for package_ident in PACKAGES:
        print(f">  - Adding {package_ident}")
        package = app_catalog[package_ident]
        if isinstance(package, AppPackage):
            builder.add_app(package)
        elif isinstance(package, FilesPackage):
            builder.add_files_package(package)

    if FILES_APP_ZIP_URL and "file-manager.offspot.kiwix.org" in PACKAGES:
        print(f"> Adding ZIP from {FILES_APP_ZIP_URL}")
        builder.add_file(
            url_or_content=FILES_APP_ZIP_URL,
            to="${APP_DIR:file-manager.offspot.kiwix.org}",
            size=get_online_rsc_size(FILES_APP_ZIP_URL),
            via="zip",
            is_url=True,
        )

    if ADD_HWCLOCK_MGMT:
        print("> Adding Clock")
        builder.add_hwclock()

    if ADD_METRICS:
        print("> Adding Metrics")
        builder.add_metrics()

    return builder


def main():
    print("Preparing YAML Config file…")
    builder = get_builder()
    print("Rendering YAML Config file…")
    yaml_text = builder.render()
    print(f"Writing YAML to {YAML_CONFIG_PATH}")
    Path(YAML_CONFIG_PATH).write_text(yaml_text)
    print("Done.")


main()

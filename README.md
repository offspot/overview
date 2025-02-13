# Kiwix Hotspot

`offspot` is a collection of tools and solutions to support **Kiwix Hotspot**.

A Kiwix Hotspot is a Raspberry Pi computer running a WiFi hotspot and serving content and services over HTTP to the its WiFi clients.
It's a software stack on top of a regular RaspberryPi OS but distributed as an image file.
The resulting system can still be used freely.

➡️ **TUTORIAL:** [Create your own WiFi knowledge hub with Kiwix Hotspot](https://github.com/offspot/overview/blob/main/docs/Kiwix%20Hotspot%20Tutorial.md) ⬅️

---

![offspot-diagram.png](offspot-diagram.png)

## Base OS

Our Base OS is called `base-image` and is built on RaspberryOS Lite. Just like RaspberryOS, it is built using pi-gen.

[`base-image`](https://github.com/offspot/base-image) is the repository holding our changes and script to build it. Its output is an IMG file. We host our releases at [drive.offspot.it/base/](https://drive.offspot.it/base/).

You can use it to create a different base image and use it when creating a Kiwix Hotspot. Be sure not to break our key components though.

### Main Changes

- Less packages. A Kiwix Hotspot doesn't need Bluetooth and GPIO for instance.
- Default User: `user` / `raspberry`.
- SSH installed but not started. Connect to console to enable it (`sudo systemctl enable --now ssh`)
- Three partitions layout: `/boot` (`FAT32`), `/` (`ext4`) and `/data` (`ext4`). Root filesystem size is limited ❗
- Custom initial-boot resize script to expand `/data` partition to use all remaining space on device.
- No SWAP.
- Custom WiFi firmwares to support more AP clients than stock firmware.
- Reduced logs to save I/O
- Docker Stack (balena-engine + Docker Compose)
- Automatic Docker images loading on Start
- Internet-connectivity check timer
- DHCP client service configured for eth0 (`dhcpcd`)
- Persistent firewal (`iptables` restore on start)
- DNS Server (`dnsmasq`) orchestrated by offspot-runtime
- WiFI AP (`hostapd`) orchestrated by offspot-runtime
- Offspot-Runtime service on boot to configure or start DNS/AP/etc

## Offspot Runtime

[`offspot_runtime`](https://github.com/offspot/offspot-config), part of `offspot-config` repository is a collection of scripts that are run on every start via `offspot-runtime.service`.

It's goal is two fold:

- Configure the aforementioned tools that are installed on the Host.
- Start those tools.

The configuration part is meant to be run on first boot but can happen at any boot. We chose to configure those things on boot so the image-creation step (`image-creator` below) doesn't need a working system and can remain a dumb file-copying tool.

It also allows dynamically changing some settings which users are kin to customize (SSID, password, etc).

In practice, it is multiple scripts ; each focusing on a *task* (usually operating a single underlying tool) that can be invoked directly, with inputs passed on the CLI.

It's not used this way in general, as its service runs `offspot-runtime-config-fromfile /boot/firmware/offspot.yaml`

> [!IMPORTANT]
> This reads that file and calls all scripts individually with the args corresponding to the config file. As those configs are applied, configuration is removed from the file. In a booted, configured machine, that file is thus an empty YAML document.
> The file is thus changed to **request a configuration change**.

This file is mandatory to configure the Hotspot the first time and the base-image includes a minimnal one.

This file is purposedly stored on `/boot` partition as this one is FAT32 and can thus be modified on all platforms.

Documentation for this file is on [`offspot_config`](https://github.com/offspot/offspot-config)'s README.

## Repositories

| Tool                                                              | Description                                                                                                                                                                                                  |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [`base-image`](https://github.com/offspot/base-image)             | raspiOS-like _base_ image builder: adds/removes package, adds some configuration, tweaks and tools, installs `offspot_runtime` (part of `offspot_config`)                                                    |
| [`offspot_runtime`](https://github.com/offspot/offspot-config)    | set of scripts to (re-)configure some stuff on boot: network, WiFi, etc.                                                                                                                                     |
| [`offspot_config`](https://github.com/offspot/offspot-config)     | library for parsing/creating offspot YAML config. Include a Config Builder and an App Catalog                                                                                                                |
| [`image-creator`](https://github.com/offspot/image-creator)       | _somewhat_-generic Image creator taking a YAML config as input. YAML config lists all files to download, and includes a complete docker-compose. This is not user-friendly at all. Linux only, runs as root. |
| [Kiwix Imager Service](https://github.com/offspot/imager-service) | Web UI to select content. Uses the offspot-config builder to produce YAML. Calls image-creator in worker to build image then uploads it. https://imager.kiwix.org                                            |
| Kiwix Imager App                                                  | **Not implemented yet**. kiwix-hotspot replacement. UI to select content and configure. Will use offspot-config builder to gen a YAML and call image-creator                                                 |

# offspot

offspot by Kiwix is a collection of tools and solutions to support **Kiwix Hotspot**.

| Tool                                                              | Description                                                                                                                                                                                                  |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [`base-image`](https://github.com/offspot/base-image)             | raspiOS-like _base_ image builder: adds/removes package, adds some configuration, tweaks and tools, installs `offspot_runtime` (part of `offspot_config`)                                                    |
| [`offspot_runtime`](https://github.com/offspot/offspot-config)    | set of scripts to (re-)configure some stuff on boot: network, WiFi, etc.                                                                                                                                     |
| [`offspot_config`](https://github.com/offspot/offspot-config)     | library for parsing/creating offspot YAML config. Include a Config Builder and an App Catalog                                                                                                                |
| [`image-creator`](https://github.com/offspot/image-creator)       | _somewhat_-generic Image creator taking a YAML config as input. YAML config lists all files to download, and includes a complete docker-compose. This is not user-friendly at all. Linux only, runs as root. |
| [Kiwix Imager Service](https://github.com/offspot/imager-service) | Web UI to select content. Uses the offspot-config builder to produce YAML. Calls image-creator in worker to build image then uploads it. https://imager.kiwix.org                                            |
| Kiwix Imager App                                                  | **Not implemented yet**. kiwix-hotspot replacement. UI to select content and configure. Will use offspot-config builder to gen a YAML and call image-creator                                                 |

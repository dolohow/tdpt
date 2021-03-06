TDPT
====

Torrent downloading progress on Telegram

![Screencast](https://i.imgur.com/yTsldua.gif "Screencast")


## Features
* Support for the most popular torrent clients `Transmission`, `rTorrent` and `deluge`
* Easy configuration
* Uploading new torrent - just send torrent file to chat


## Installation

### Docker
Download config file and edit it for your needs
```bash
wget https://raw.githubusercontent.com/dolohow/tdpt/master/config/tdpt.ini
```

```bash
podman run -d \
  --name tdpt \
  -v PATH_TO_DIR_WITH_TDPT_INI:/config \
  dolohow/tdpt
```

TDPT
====

Transmission downloading progress on Telegram

![Screencast](https://i.imgur.com/IEOLsL6.gif "Screencast")


## Features
* Multithreading, each downloading item is handled separately
* Running post download script in separate process
* Self-adjustment of `Telegram` bot limits based on number of torrents
  tracked
* Easy configuration


## Installation
You need Python 3 to run this program.  It can now on Python 2, but I
did not make any effort to support that.

```
pip install -r requirements.txt
```

Create configuration file file
```
cp tdpt.ini.template tdpt.ini
```

Edit it and save.


## Options
Parameters:
```
[General]
call_on_finish - when transmission is done with downloading this script
                 will execute command or script specified in this
                 parameter
```


## FAQ

### `Transmission` already supports running script upon finishing download
Yes, that is true.  However the script that `transmission` will run will
be executed in the same thread.  That means any long running process
would freeze it for that amount of time which is highly undesirable.

### `tdpt` picks up new items so slow
Currently it fetches new items every 20 seconds, because this operation
can be quite expensive.  I might add option to specify this interval
based on your preferences.

### I am downloading 20 items and `tdpt` updates them very rarely
`Telegram` puts limit of how often bot can make request to one channel.
Currently the limit is 20 updates per minute.  `tdpt` makes time
adjustment based on number of torrents that it tracks to avoid hitting
limits.

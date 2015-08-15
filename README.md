# Server Status over HTTP HEAD


## Overview

**Server Status over HTTP HEAD**, a.k.a. **SSoHH**, is a simple servers monitoring solution based on HTTP HEAD request. It uses a client-server architecture: 

* **Client** - Send its status information as *User Agent* string in HTTP HEAD requests to the server
* **Server** - Parse web server log (*Nginx*) to extract the status information, and present on a web page


## Usage

### Configuration

In *client_set.sh* file:

| property | meaning |
| :---- | :---- |
| SSOHH_TAG | Private tag in requests for identify the clients |
| ENDPOINT | Web server endpoint receives requests  |
| INTERVAL | Interval in minutes (default `5`) between each request |

In *reducer.py* file:

| property | meaning |
| :---- | :---- |
| config_tag | Should be consistent with `SSOHH_TAG` in *client_set.sh* |
| config_log_path | Absolute path of *access.log* logs requests from clients  |
| config_page_path | Absolute path of the generated web page |

### Client-Side

Copy configured *client_set.sh* to each *nix machine to be monitored, `chmod +x client_set.sh` to make it executable. And then execute one of the following commands according to their environment:

* `./client_set.sh pi` for Raspbian on Raspberry Pi
* `./client_set.sh bbb` for Debian on BeagleBone Black
* `./client_set.sh linux` for Ubuntu Linux
* `./client_set.sh mac` for OS X on Macintosh

You may add/edit `MONITOR` in *client_set.sh* to customize the metrics.

### Server-Side

Ensure *reducer.py* and *template.html* are configured and in the same directory, add the following line to `crontab`:

```bash
* * * * * (sleep 10; python3 /your/path/to/ssohh/reducer.py)
```

Start the web server to host the generated page, and open your browser to visit it. (You may need to execute the script manually if it hasn't been executed by `crontab` yet.)


## Preview


## Suggestion
1. Keep `SSOHH_TAG` confidential if you don't want to see any faked lines
2. Use exclusive web server endpoint and *access.log* for SSoHH


## Known Issues

1. Not supported on Microsoft Windows Server
2. Log rotation may cause missing lines, especially for machines that have been disconnected for a while

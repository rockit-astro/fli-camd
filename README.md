## FLI camera daemon

`fli_camd` interfaces with and wraps ML50100 detectors and exposes them via Pyro.

`cam` is a commandline utility for controlling the cameras.

See [Software Infrastructure](https://github.com/warwick-one-metre/docs/wiki/Software-Infrastructure) for an overview of the observatory software architecture and instructions for developing and deploying the code.

### Configuration

Configuration is read from json files that are installed by default to `/etc/camd`.
A configuration file is specified when launching the camera server, and the `cam` frontend will search for files matching the specified camera id when launched.

The configuration options are:
```python
{
  "daemon": "localhost_test", # Run the camera server as this daemon. Daemon types are registered in `warwick.observatory.common.daemons`.
  "pipeline_daemon": "localhost_test2", # The daemon that should be notified to hand over newly saved frames for processing.
  "pipeline_handover_timeout": 10, # The maximum amount of time to wait for the pipeline daemon to accept a newly saved frame. The exposure sequence is aborted if this is exceeded.
  "log_name": "fli_camd@test", # The name to use when writing messages to the observatory log.
  "control_machines": ["LocalHost"], # Machine names that are allowed to control (rather than just query) state. Machine names are registered in `warwick.observatory.common.IP`.
  "temperature_setpoint": -20, # Default temperature for the CMOS sensor.
  "temperature_update_delay": 5, # Amount of time in seconds to wait between querying the camera temperature and cooling status
  "timerport": "/dev/gpstimer", # Serial device node for the GPS timer dongle (don't define if not attached).
  "timerbaud": 9600, # Serial baud rate for the GPS timer dongle.
  "camera_id": "TEST", # Value to use for the CAMID fits header keyword.
  "camera_serial": "ML6314917", # Camera serial number. This is reported in the `dmesg` log after connecting the camera USB.
  "output_path": "/var/tmp/", # Path to save temporary output frames before they are handed to the pipeline daemon. This should match the pipeline incoming_data_path setting.
  "output_prefix": "test", # Filename prefix to use for temporary output frames.
  "expcount_path": "/var/tmp/test-counter.json" # Path to the json file that is used to track the continuous frame and shutter numbers.
}
```

### Initial Installation

Build and install `fliusb` kernel driver:
* Clone the fliusb driver repository from https://github.com/LCOGT/fliusb.git 
* Compile using `make`
* Copy `fliusb.ko` to `/usr/lib/modules/$(uname -r)/extra/`
* Create file `/etc/modules-load.d/fliusb.conf` with contents `fliusb` 

The automated packaging scripts will push 4 RPM packages to the observatory package repository:

| Package           | Description |
| ----------------- | ------ |
| clasp-fli-camera-data  | Contains the json configuration files for the CLASP instrument. |
| observatory-fli-camera-server | Contains the `fli_camd` server and systemd service files for the camera server. |
| observatory-fli-camera-client | Contains the `cam` commandline utility for controlling the camera server. |
| python3-warwick-observatory-camera-fli | Contains the python module with shared code. |

The `observatory-fli-camera-server` and `clasp-fli-camera-data` packages should be installed on the CLASP DAS machine, then the systemd service should be enabled:
```
sudo systemctl enable fli_camd.service@<config>
sudo systemctl start fli_camd@<config>
```

where `config` is the name of the json file for the appropriate camera.

Now open a port in the firewall so the TCS and dashboard machines can communicate with the camera server:
```
sudo firewall-cmd --zone=public --add-port=<port>/tcp --permanent
sudo firewall-cmd --reload
```

where `port` is the port defined in `warwick.observatory.common.daemons` for the daemon specified in the camera config.

The `observatory-fli-camera-client` and `clasp-fli-camera-config` packages should be installed on the CLASP TCS machine for centralized control.

### Upgrading Installation

New RPM packages are automatically created and pushed to the package repository for each push to the `master` branch.
These can be upgraded locally using the standard system update procedure:
```
sudo yum clean expire-cache
sudo yum update
```

The daemon should then be restarted to use the newly installed code:
```
sudo systemctl stop fli_camd@<config>
sudo systemctl start fli_camd@<config>
```

### Testing Locally

The camera server and client can be run directly from a git clone:
```
./fli_camd test.json
CAMD_CONFIG_ROOT=. ./cam test status
```


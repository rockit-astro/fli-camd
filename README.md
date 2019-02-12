## RASA prototype camera daemons [![Travis CI build status](https://travis-ci.org/warwick-one-metre/rasa-camd.svg?branch=master)](https://travis-ci.org/warwick-one-metre/rasa-camd)

Part of the observatory software for the RASA prototype telescope.

`camd` interfaces with and wraps the FLI cameras and exposes them via Pyro.

`cam` is a commandline utility for controlling the cameras.

See [Software Infrastructure](https://github.com/warwick-one-metre/docs/wiki/Software-Infrastructure) for an overview of the W1m software architecture and instructions for developing and deploying the code.

### Software Setup

Build and install `fliusb` kernel driver:
* Clone the fliusb driver repository from https://github.com/LCOGT/fliusb.git 
* Compile using `make`
* Copy `fliusb.ko` to `/usr/lib/modules/$(uname -r)/extra/`
* Create file `/etc/modules-load.d/fliusb.conf` with contents `fliusb` 

After installing `rasa-camera-server`, the `rasa_camd` service must be enabled using:
```
sudo systemctl enable rasa_camd.service
```

The service will automatically start on system boot, or you can start it immediately using:
```
sudo systemctl start rasa_camd.service
```

Finally, open ports in the firewall so that other machines on the network can access the daemons:
```
sudo firewall-cmd --zone=public --add-port=9037/tcp --permanent
sudo firewall-cmd --reload
```

### Hardware Setup

The camera serial number can be found by checking the `dmesg` log after connecting the camera USB.

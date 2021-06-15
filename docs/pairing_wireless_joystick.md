# Pairing a wireless joystick

This software has been tested to be compatible with an XBox One wireless controller. Other video game controllers should also work, but they _might_ require some software modifications. Please share your experience getting these working.

## XBox One Controller

For the XBox controller, Bluetooth ERTM must be turned off. To check, run:
```bash
$ cat /sys/module/bluetooth/parameters/disable_ertm
Y
```

A response of `Y` means it's disabled, `N` means it's not. To disable it manually, you can run:
```bash
$ echo 1 | sudo tee /sys/module/bluetooth/parameters/disable_ertm
```

Or to permanently disable it:
```bash
$ echo "options bluetooth disable_ertm=Y" | sudo tee /etc/modprobe.d/bluetooth.conf
```

Next, get your controller and put it in pairing mode. Then run:
```bash
$ bluetoothctl
Agent registered
```

```bash
[bluetooth]# scan on
Discovery started
```

You should see something similar to the following:
```bash
[NEW] Device C8:3F:12:34:56:78 Xbox Wireless Controller
```

Take note of the Bluetooth address of the device.

Now to pair the device, run:
```bash
[bluetooth]# pair C8:3F:12:34:56:78
Attempting to pair with C8:3F:12:34:56:78
[CHG] Device C8:3F:12:34:56:78 Connected: yes
[CHG] Device C8:3F:12:34:56:78 ServicesResolved: yes
[CHG] Device C8:3F:12:34:56:78 Paired: yes
Pairing successful
```
```bash
[bluetooth]# trust C8:3F:12:34:56:78
[CHG] Device C8:3F:12:34:56:78 Trusted: yes
Changing C8:3F:12:34:56:78 trust succeeded
```
```bash
[bluetooth]# connect C8:3F:12:34:56:78
Attempting to connect to C8:3F:12:34:56:78
[CHG] Device C8:3F:12:34:56:78 Connected: yes
[CHG] Device C8:3F:12:34:56:78 Modalias: usb:v045Ep02FDd0903
[CHG] Device C8:3F:12:34:56:78 UUIDs: 00001124-0000-1000-8000-00805f9b34fb
[CHG] Device C8:3F:12:34:56:78 UUIDs: 00001200-0000-1000-8000-00805f9b34fb
[CHG] Device C8:3F:12:34:56:78 ServicesResolved: yes
Connection successful
```

To test out the controller, check that `/dev/input/js0` exists, and run:
```
$ jstest
```

It should respond to your controller inputs.

You should now be able to use your controller with your LED display!

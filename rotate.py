#!/usr/bin/env python
import dbus, sys, subprocess
from gi.repository import GLib
from dbus.mainloop.glib import DBusGMainLoop

DBusGMainLoop(set_as_default=True)

# map sensor-proxy orientation to xrandr and wacom
# there seems to be a bug:
# 'right-up' when laptop has normal orientation
# 'normal' for 90 left
# 'bottom-up' for 90 right
# 'left-up' for 180
xrandr_orientation_map = {
	'right-up': 'normal',
	'normal' : 'right',
	'bottom-up': 'left',
	'left-up': 'inverted'
}

wacom_orientation_map = {
	'right-up': 'none',
	'normal' : 'cw',
	'bottom-up': 'ccw',
	'left-up': 'half'
}


# load wacom devices 
lines = subprocess.check_output(['xsetwacom','--list', 'devices']).split('\n')
lines = filter(lambda x: x, lines) # get rid of empty line at the end
wacom = map(lambda x: x.split('\t')[0], lines)

# init dbus stuff and subscribe to events
bus = dbus.SystemBus()
proxy = bus.get_object('net.hadess.SensorProxy', '/net/hadess/SensorProxy')
iface = dbus.Interface(proxy, 'net.hadess.SensorProxy')
props = dbus.Interface(proxy, 'org.freedesktop.DBus.Properties')


def handler(source, changedProperties, invalidatedProperties, **kwargs):
	if source=='net.hadess.SensorProxy':
		if 'AccelerometerOrientation' in changedProperties:
			orientation = changedProperties['AccelerometerOrientation']

			subprocess.call(["xrandr", "-o", xrandr_orientation_map[orientation]])
			for device in wacom:
				subprocess.call(["xsetwacom", "set", device, "rotate", wacom_orientation_map[orientation]])

props.connect_to_signal('PropertiesChanged', handler, sender_keyword='sender')
iface.ClaimAccelerometer()
#iface.ClaimLight()

loop = GLib.MainLoop()
loop.run()

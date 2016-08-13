import sys

import alexandra
import click
import pychromecast
from pprint import pprint as p


device_name = None
cast = None
app = alexandra.Application()
wsgi_app = app.create_wsgi_app()

@click.command()
@click.option('--device', help='name of chromecast device')
def server(device):
    global cast
    global device_name
    global device_list

    # Initialize the connection 
    app.run('0.0.0.0', 50421, debug=True)

    # If the device was explicitly set
    if device:
        print('>> trying to connect to {}'.format(device))

        device_name = device
        cast = pychromecast.get_chromecast(friendly_name=device)
        if cast is None:
            click.echo("Couldn't find device '{}'".format(device))
            sys.exit(-1)

        print(repr(cast))
    else:
        # We're going to search for the device to connect to
        # TODO - trigger this as an intent
        poll_for_devices()
        # TODO - add multithreading and stall.
        exit()


@app.intent('Reconnect')
def reconnect(slots, session):
    global cast

    cast = pychromecast.get_chromecast(friendly_name=device_name)

    if cast is None:
        return alexandra.respond(
            'Failed to connect to Chromecast named %s.' % device_name)

    return alexandra.respond('Reconnected.')


@app.intent('SkipMedia')
def skip_media(slots, session):
    mc = cast.media_controller

    if not mc.status.supports_skip_forward:
        return alexandra.respond("Skipping not supported")

    mc.skip()
    return alexandra.respond()


@app.intent('PlayMedia')
def play_media(slots, session):
    mc = cast.media_controller

    if mc.status.player_is_playing:
        return alexandra.respond("Already playing")

    mc.play()
    return alexandra.respond()


@app.intent('PauseMedia')
def pause_media(slots, session):
    mc = cast.media_controller

    if not mc.status.player_is_playing:
        return alexandra.respond("Already paused")

    mc.pause()
    return alexandra.respond()


@app.intent('Reboot')
def reboot(slots, session):
    cast.reboot()
    return alexandra.respond()

@app.intent('SearchForDevice')
def search_for_device(slots, session):
    global cast
    # We're searching for a new cast device, so if our active device is set
    if cast:
        # unset it...dun dun dun
        cast = None

    # Tell the end user what's going on
    alexandra.respond("I'm searching for chromecasts...")
    
    # Get all the chromecast's on the network by their device objects.
    device_list = [pychromecast.get_chromecast(friendly_name=device_name) for device_name in pychromecast.get_chromecasts_as_dict().keys()]

    # If a player is playing, we want to list that player first as it is most probably the player we want to control.
    device_list.sort(key=lambda cast: int(cast.media_controller.status.player_is_playing), reverse=True)

    # TODO SAY:
    # Select the chromecast that you want by name. I'll list the devices. Say the device you want when you hear it.
    # [Chromecast('192.168.1.15', port=8009, device=DeviceStatus(friendly_name=u'Living Room', model_name=u'Chromecast', manufacturer=u'Google Inc.', api_version=(1, 0), uuid=UUID('2c5168da-e209-2708-afcc-0978fe445383'), cast_type='cast')),
    #  Chromecast('192.168.1.38', port=8009, device=DeviceStatus(friendly_name=u'Bedroom Audio', model_name=u'Chromecast Audio', manufacturer=u'Google Inc.', api_version=(1, 0), uuid=UUID('37d34be1-b464-86e4-f7c6-422e96d6a095'), cast_type='audio')),
    #  Chromecast('192.168.1.39', port=8009, device=DeviceStatus(friendly_name=u'Living Room Audio', model_name=u'Chromecast Audio', manufacturer=u'Google Inc.', api_version=(1, 0), uuid=UUID('04491a7c-4d5c-0e90-590a-d8e7bebc4a23'), cast_type='audio')),
    #  Chromecast('192.168.1.3', port=8009, device=DeviceStatus(friendly_name=u'Bedroom', model_name=u'Chromecast', manufacturer=u'Google Inc.', api_version=(1, 0), uuid=UUID('1a5c890b-566a-a4ea-840f-83e202665c89'), cast_type='cast')),
    #  Chromecast('192.168.1.40', port=8009, device=DeviceStatus(friendly_name=u'Upstairs Computer', model_name=u'Chromecast Audio', manufacturer=u'Google Inc.', api_version=(1, 0), uuid=UUID('695d871f-788f-6085-9cd4-68c4fd6c8a9e'), cast_type='audio')),
    #  Chromecast('192.168.1.39', port=42273, device=DeviceStatus(friendly_name=u'Home', model_name=u'Google Cast Group', manufacturer=u'Google Inc.', api_version=(1, 0), uuid=UUID('3b919716-40d2-447f-a76e-3511a2050760'), cast_type='group'))]
    return alexandra.respond("Found these chromecasts:")


if __name__ == '__main__':
    server()

# Customizing Settings

There is a settings directory used to configure your panel, the framework software, and apps.

## System Settings

System settings are stored in: `config/system.json`

These are the global settings that configure your LED display. For example, to turn your LED display off automatically after it boots, set `"displayOffAfterBoot": true` here:

```json
    "settings": {
        "title": "Synack LED Display",
        "displayOffAfterBoot": false
    },
```

## Per-App Settings

Per-app settings are stored in: `config/apps/*.json`

These are the settings that configure each app to be shown on your LED display. For example, to configure the Synack logo app, you can edit `synack_display.json`.

To turn off your personalizations, you can set `"enable": false` here:

```json
    {
        "type": "text",
        "text": "malcolmst",
        "point": [32, 7],
        "font": "6x9",
        "color": [255, 255, 255],
        "scroll": "auto",
        "align": "center",
        "enable": true
    },
```

## App Display Order

The app display order file is stored in: `config/screen_order.txt`

This is a text file with one app name per line, describing the order of apps shown on the LED display. Each line should correspond to the name of a file in the `apps` settings directory, without the `.json` extension.

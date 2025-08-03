# MikroTik Netwatch Home Assistant Integration

A Home Assistant integration that exposes MikroTik RouterOS netwatch functionality as sensors using the MikroTik REST API.

## Features

- Exposes each netwatch entry as a sensor with `up`/`down` status
- Provides detailed attributes including RTT statistics, packet loss, and more
- Supports HTTPS with optional SSL certificate validation
- Configurable scan intervals
- HACS compatible

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click "Explore & Download Repositories"
4. Search for "MikroTik Netwatch"
5. Download the integration
6. Restart Home Assistant
7. Go to Configuration → Integrations
8. Click "Add Integration" and search for "MikroTik Netwatch"

### Manual Installation

1. Copy the `custom_components/mikrotik_netwatch` folder to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant
3. Go to Configuration → Integrations
4. Click "Add Integration" and search for "MikroTik Netwatch"

## Configuration

The integration is configured through the Home Assistant UI:

### Parameters

1. **Host**: MikroTik IP address or hostname, optionally with `:<port>`
2. **Username**: RouterOS username with API access
3. **Password**: RouterOS password
4. **Scan Interval**: Query frequency in seconds (default: 60, range: 5-300)
5. **Ignore SSL Errors**: Ignore SSL/TLS certificate errors (default: false)

## Sensor Details

### Sensor Value
- The sensor state represents the netwatch status: `up` or `down`

### Sensor Attributes

All other netwatch data is available as sensor attributes, for example:

- `comment`: Description of the monitored host
- `host`: Target IP address being monitored
- `disabled`: Whether the netwatch entry is disabled
- `interval`: Check interval
- `packet-count`: Number of packets per test
- `done-tests`: Total completed tests
- `failed-tests`: Number of failed tests
- `loss-count`: Current packet loss count
- `loss-percent`: Packet loss percentage
- `response-count`: Successful responses
- `sent-count`: Packets sent
- `since`: When monitoring started
- `type`: Test type (icmp, tcp, etc.)
- `rtt-avg`: Average round-trip time (in milliseconds)
- `rtt-jitter`: RTT jitter (in milliseconds)
- `rtt-max`: Maximum RTT (in milliseconds)
- `rtt-min`: Minimum RTT (in milliseconds)
- `rtt-stdev`: RTT standard deviation (in milliseconds)

### Time Format Conversion
RTT values are automatically converted from MikroTik's format (`11ms687us`) to milliseconds for easy use in Home Assistant automations and dashboards.

## Requirements

- Home Assistant 2023.1.0 or later
- MikroTik RouterOS device with REST API and netwatch enabled
- RouterOS user account with API access permissions

## Usage Examples

### Automation Example
```yaml
automation:
  - alias: "Notify when VPN connection is down"
    trigger:
      - platform: state
        entity_id: sensor.netwatch_remote_vpn_interface
        to: "down"
    action:
      - service: notify.pushbullet
        data:
          message: "VPN connection is down!"
```

### Dashboard Card Example
```yaml
type: entities
entities:
  - entity: sensor.netwatch_remote_vpn_interface
    secondary_info: last-changed
  - type: attribute
    entity: sensor.netwatch_remote_vpn_interface
    attribute: rtt-avg
    name: "Average RTT"
  - type: attribute
    entity: sensor.netwatch_remote_vpn_interface
    attribute: loss-percent
    name: "Packet Loss %"
```

## Troubleshooting

### Connection Issues
1. Ensure the MikroTik device is reachable from Home Assistant and the hostname is resolvable
2. Verify the REST API is enabled in RouterOS and Netwatch is configured
3. Check that the user account has sufficient permissions
4. If using HTTPS with self-signed certificates, enable "Ignore SSL certificate errors" or fix the certificate

### No Sensors Appearing
1. Ensure netwatch is configured in RouterOS with at least one entry
2. Check Home Assistant logs for any error messages
3. Verify the integration was added successfully in Configuration → Integrations

## Contributing

Contributions are welcome! Please feel free to submit a PR.

## License

This project is licensed under the MIT License.


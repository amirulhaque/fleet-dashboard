import requests
import re
from datetime import datetime
from zoneinfo import ZoneInfo

API = "http://aika168.com/Ajax/DevicesAjax.asmx/GetTrackingForShare"

NEPAL_TZ = ZoneInfo("Asia/Kathmandu")

rows = ""

with open("vehicles.txt") as f:

    for line in f:

        if not line.strip():
            continue

        vehicle, token = line.strip().split(",", 1)

        try:

            r = requests.post(
                API,
                data=f"{{Key:'{token}'}}",
                headers={"Content-Type": "application/json"},
                timeout=20
            )

            raw = r.json()["d"]

            speed = re.search(
                r'speed:"([^"]*)"', raw
            ).group(1)

            gps_time = re.search(
                r'deviceUtcDate:"([^"]*)"', raw
            ).group(1)

            status_match = re.search(
                r'status:"([^"]*)"', raw
            )

            status = (
                status_match.group(1)
                if status_match
                else "Unknown"
            )

            lat = re.search(
                r'latitude:"([^"]*)"', raw
            ).group(1)

            lon = re.search(
                r'longitude:"([^"]*)"', raw
            ).group(1)

            # Status Colors
            if status.lower() == "move":
                status_color = "green"
            elif status.lower() == "stop":
                status_color = "red"
            else:
                status_color = "orange"

            # Address
            address_match = re.search(
                r'address:"([^"]*)"',
                raw
            )

            if address_match and address_match.group(1).strip():

                address = address_match.group(1)

            else:

                try:

                    geo = requests.get(
                        f"https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={lat}&lon={lon}",
                        headers={
                            "User-Agent": "FleetDashboard"
                        },
                        timeout=20
                    )

                    address = geo.json().get(
                        "display_name",
                        f"{lat},{lon}"
                    )

                    parts = address.split(",")

                    if len(parts) > 4:
                        address = ",".join(parts[:4])

                except:

                    address = f"{lat},{lon}"

            map_html = f"""
            <a href="https://maps.google.com/?q={lat},{lon}"
               target="_blank">
               Open Map
            </a>
            """

            rows += f"""
            <tr>
                <td>{vehicle}</td>

                <td style="color:{status_color};font-weight:bold">
                    {status}
                </td>

                <td>{speed} km/h</td>

                <td>{gps_time}</td>

                <td>{address}</td>

                <td>{map_html}</td>

            </tr>
            """

        except Exception as e:

            rows += f"""
            <tr>
                <td>{vehicle}</td>
                <td colspan="5">
                    Error: {e}
                </td>
            </tr>
            """

html = f"""
<!DOCTYPE html>
<html>

<head>

<meta charset="UTF-8">
<meta http-equiv="refresh" content="60">

<title>Fleet Tracking Dashboard</title>

<style>

body {{
    font-family: Arial, sans-serif;
    margin: 20px;
    background: #f4f4f4;
}}

h1 {{
    color: #2b6edc;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    background: white;
}}

th {{
    background: #2b6edc;
    color: white;
    padding: 12px;
    text-align: left;
}}

td {{
    border: 1px solid #ddd;
    padding: 10px;
}}

tr:nth-child(even) {{
    background: #f8f8f8;
}}

a {{
    color: blue;
    font-weight: bold;
}}

</style>

</head>

<body>

<h1>🚚 Fleet Tracking Dashboard</h1>

<p>
<b>Last Updated:</b>
{datetime.now(NEPAL_TZ).strftime("%Y-%m-%d %H:%M:%S")}
</p>

<table>

<tr>
    <th>Vehicle</th>
    <th>Status</th>
    <th>Speed</th>
    <th>Last GPS Time</th>
    <th>Location</th>
    <th>Map</th>
</tr>

{rows}

</table>

</body>
</html>
"""

with open(
    "dashboard.html",
    "w",
    encoding="utf-8"
) as f:
    f.write(html)

print("dashboard.html created")
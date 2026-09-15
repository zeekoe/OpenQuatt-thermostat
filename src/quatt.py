#!/usr/bin/env python3
import sys

from fetch_openquatt_metrics import (
    FetchError,
    fetch_openquatt_metrics,
)

fields_to_fetch = (
    ("hp1OutsideTemp", "sensor", "HP1 - Outside temperature"),
    ("roomTemp", "sensor", "Room Temperature (Selected)"),
    ("supplyTemp", "sensor", "Water Supply Temp (Selected)"),
    ("totalHeat", "sensor", "Total Heat Power"),
    ("totalCoolingPower", "sensor", "Total Cooling Power"),
    ("totalCop", "sensor", "Total COP"),
    ("hp1Freq", "sensor", "HP1 - Compressor frequency"),
    ("hp1WaterIn", "sensor", "HP1 - Water in temperature"),
    ("hp1WaterOut", "sensor", "HP1 - Water out temperature"),
    ("hp1Power", "sensor", "HP1 - Power Input"),
    ("hp1EvaporatorCoilTemp", "sensor", "HP1 - Evaporator coil temperature"),
)

def print_results(metrics):
    label_width = max(len(item["label"]) for item in metrics["results"])
    for item in metrics["results"]:
        print("%-*s : %s" % (label_width, item["label"], item["value"]))

    if metrics["missing"]:
        print(
            "\nMissing keys: %s" % ", ".join(str(item) for item in metrics["missing"]),
            file=sys.stderr,
        )
    if metrics["errors"]:
        print("\nErrors: %s" % metrics["errors"], file=sys.stderr)

try:
    metrics = fetch_openquatt_metrics(
        url="http://openquatt.lan:80/openquatt/entities",
        display_fields=fields_to_fetch
    )
except FetchError as exc:
    print(str(exc), file=sys.stderr)

if not metrics["ok"]:
    print("Request failed: %s" % metrics["payload"], file=sys.stderr)
print(metrics["results"])

print_results(metrics)

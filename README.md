# sofar-inverter-control

## Background

Inspired by [sofar2mqtt](https://github.com/cmcgerty/Sofar2mqtt) but wanting something based on ESPHome rather than MQTT, I wrote this code to control a Sofar Solar inverter. This works with the inverter in passive mode, so that the inverter can be controlled by Home Assistant.

Like sofar2mqtt, this code uses the Sofar Solar Modbus protocol to read and write registers in the inverter. The inverter is connected to the ESP8266 via a MAX3485 serial to RS485 adapter.

After developing the ESPHome module, I also wrote a pyscript program that runs each night, looks at the half hourly Octopus Agile electricity prices and works out a plan to charge the battery during the cheapest slots (accounting for typical usage and expected solar generation). 

It’s not too clever - just some simple heuristics at this time. The output of that script (basically a ‘desired mode’ for every half hour of the day) feeds an automation which controls the inverter. 

One additional part of the daily plan is to put the inverter in 'battery_save' mode whenever the price is below the average for the day. During these periods, grid power is used even if the battery has charge. This really stretches out the battery storage so that we usually have some left for peak periods. 

The overall effect is pretty nice: even on cloudy days we’re always paying below the average Agile Octopus price, so it feels like a worthwhile experiment.

## Repo contents

This repo contains:

* an ESPHhome configuration for an ESP8266 to monitor and control a Sofar Solar inverter. This includes passive mode control, enabling charge/discharge behaviour to be changed by Home Assistant.
* a Home Assistant Pyscript program to, on a nightly basis, calculate a charging plan that fills the batteries with cheap power (for Octopus Agile customers).
* a Home Assistant template sensor and automation to apply the charging plan as the day progresses.

This repo is a WIP, and may be written up into a blog post at some point.

No guarantees are made about the suitability of this code for your own use. It is provided as-is, and you are responsible for any damage it may cause. You should not use this code without understanding it first.

# sofar-inverter-control

This repo contains:

* an ESPHhome configuration for an ESP8266 to monitor and control a Sofar Solar inverter. This includes passive mode control, enabling charge/discharge behaviour to be changed by Home Assistant.
* a Home Assistant Pyscript program to, on a nightly basis, calculate a charging plan that fills the batteries with cheap power (for Octopus Agile customers).
* a Home Assistant template sensor and automation to apply the charging plan as the day progresses.

This repo is a WIP, and may be written up into a blog post at some point.

No guarantees are made about the suitability of this code for your own use. It is provided as-is, and you are responsible for any damage it may cause. You should not use this code without understanding it first.

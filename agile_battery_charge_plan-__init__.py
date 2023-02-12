#
# Pyscript Agile Octopus daily charge planner
# Uses a simple heuristic to work out cheapest times of day to charge/discharge batteries
# This file should be named: /config/pyscript/apps/agile_battery_charge_plan/__init__.py
#
from datetime import datetime, timezone, timedelta
import math

#
# Required configuration in /config/pyscript/apps/config.yml
# e.g:
# ```
# allow_all_imports: true
# hass_is_global: true
# apps:
#   agile_battery_charge_plan:
#     expected_daily_total_load: 13
#     battery_capacity: 6.88
#     current_battery_pct_entity_id: sensor.solar_battery_percentage
#     octopus_current_rate_entity_id: sensor.octopus_energy_electricity_01p223456_01234567890_current_rate
#     forecast_solar_generation_entity_id: sensor.estimated_solar_production_energy_production_today
#     forecast_solar_generation_multiplier: 1.2
#     charge_rate_kwh_per_slot: 1.5
# 
# ```
#
config = pyscript.config["apps"]["agile_battery_charge_plan"]
expected_daily_total_load = config["expected_daily_total_load"]
battery_capacity = config["battery_capacity"]
current_battery_pct_entity_id = config["current_battery_pct_entity_id"]
octopus_current_rate_entity_id = config["octopus_current_rate_entity_id"]
forecast_solar_generation_entity_id = config["forecast_solar_generation_entity_id"]
forecast_solar_generation_multiplier = config["forecast_solar_generation_multiplier"]
charge_rate_kwh_per_slot = config["charge_rate_kwh_per_slot"]


@time_trigger("startup", "cron(5 0 * * *)", "cron(5 17 * * *)", "cron(5 22 * * *)")
@service
def agile_battery_charge_plan():
    log.info(f"agile_battery_charge_plan running")

    #
    # Work out how much battery charge we need
    #
    current_charge = float(state.get(current_battery_pct_entity_id)) * battery_capacity / 100
    charge_battery_to_kwh = max(0, min(battery_capacity, expected_daily_total_load - current_charge))

    rates = state.getattr(octopus_current_rate_entity_id)["rates"]
    forecast_solar_generation = float(state.get(forecast_solar_generation_entity_id))

    # tweak our expected generation
    forecast_solar_generation = forecast_solar_generation * float(forecast_solar_generation_multiplier)

    goal_kwh = min(12 - forecast_solar_generation, charge_battery_to_kwh)
    log.info(f"Goal is to store {goal_kwh} kWh. Starting charge: {current_charge} kWh, expecting to generate: {forecast_solar_generation}")

    now = datetime.now().replace(tzinfo=timezone.utc)
    
    #
    # Try and fill the battery to the required level, filling from cheapest morning slots first
    #
    plan = sorted(rates, key=lambda x: x['rate'])
    cumulative_charge = 0

    sum_rate = 0
    for period in plan:
        sum_rate += period["rate"]
    mean_rate = sum_rate / len(plan)

    for period in plan:
        if cumulative_charge < goal_kwh and period["to"].hour < 10:
            # charge during this slot
            cumulative_charge += float(charge_rate_kwh_per_slot)
            period["desired_mode"] = "charge"
        elif period["rate"] < mean_rate:
            # if rate is less than mean average, use from grid instead of battery
            period["desired_mode"] = "battery_save"
        else:
            # use from battery, if available
            period["desired_mode"] = "auto"
    

    plan = sorted(plan, key=lambda x: x["from"])
    for period in plan:
        log.debug(f"agile_battery_charge_plan: {period['from']}: {period['desired_mode']}")
    
    state.set(f"sensor.agile_inverter_plan", value=cumulative_charge, new_attributes={
            "plan": plan,
            "unit_of_measurement": "kWh"
        })
    
    log.info("agile_battery_charge_plan completed")
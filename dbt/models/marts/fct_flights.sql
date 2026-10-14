select
    flight_record_id,
    flight_date,
    reporting_airline as airline_code,
    flight_number_reporting_airline as flight_number,
    tail_number,
    origin as origin_airport_code,
    dest as destination_airport_code,
    crs_dep_time as scheduled_departure_time,
    dep_time as actual_departure_time,
    crs_arr_time as scheduled_arrival_time,
    arr_time as actual_arrival_time,
    dep_delay_minutes,
    arr_delay_minutes,
    coalesce(dep_del15, false) as departed_15_plus_minutes_late,
    coalesce(arr_del15, false) as arrived_15_plus_minutes_late,
    cancelled,
    cancellation_code,
    diverted,
    crs_elapsed_time as scheduled_elapsed_minutes,
    actual_elapsed_time as actual_elapsed_minutes,
    air_time as air_minutes,
    distance as distance_miles,
    carrier_delay,
    weather_delay,
    nas_delay,
    security_delay,
    late_aircraft_delay,
    case
        when cancelled then 'cancelled'
        when diverted then 'diverted'
        else 'operated'
    end as flight_status
from {{ ref('stg_bts_flights') }}

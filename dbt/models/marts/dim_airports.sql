with airport_observations as (
    select
        origin as airport_code,
        origin_airport_id as airport_id,
        origin_city_name as city_name,
        origin_state as state_code
    from {{ ref('stg_bts_flights') }}

    union all

    select
        dest as airport_code,
        dest_airport_id as airport_id,
        dest_city_name as city_name,
        dest_state as state_code
    from {{ ref('stg_bts_flights') }}
)

select
    airport_code,
    max(airport_id) as airport_id,
    max(city_name) as city_name,
    max(state_code) as state_code,
    count(*) as observed_flight_count
from airport_observations
group by airport_code

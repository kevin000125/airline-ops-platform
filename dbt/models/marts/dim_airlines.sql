select
    reporting_airline as airline_code,
    max(dot_id_reporting_airline) as dot_airline_id,
    count(*) as observed_flight_count
from {{ ref('stg_bts_flights') }}
group by reporting_airline

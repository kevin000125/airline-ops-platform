select flight_record_id
from {{ ref('stg_bts_flights') }}
where year <> extract(year from flight_date)
   or month <> extract(month from flight_date)

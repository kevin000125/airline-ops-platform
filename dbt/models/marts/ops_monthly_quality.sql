select
    date_trunc('month', flight_date)::date as reporting_month,
    count(*) as total_flights,
    count(*) filter (where flight_status = 'operated') as operated_flights,
    count(*) filter (where flight_status = 'cancelled') as cancelled_flights,
    count(*) filter (where flight_status = 'diverted') as diverted_flights,
    count(*) filter (where arrived_15_plus_minutes_late) as delayed_arrivals,
    round(
        100.0 * count(*) filter (where flight_status = 'cancelled')
        / nullif(count(*), 0),
        2
    ) as cancellation_rate_pct,
    round(
        100.0 * count(*) filter (where arrived_15_plus_minutes_late)
        / nullif(count(*) filter (where flight_status = 'operated'), 0),
        2
    ) as arrival_delay_rate_pct
from {{ ref('fct_flights') }}
group by 1

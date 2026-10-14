with row_counts as (
    select
        (select count(*) from {{ ref('stg_bts_flights') }}) as staging_rows,
        (select count(*) from {{ ref('fct_flights') }}) as fact_rows
)

select *
from row_counts
where staging_rows <> fact_rows

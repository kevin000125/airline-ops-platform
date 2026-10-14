CREATE SCHEMA IF NOT EXISTS control;
CREATE SCHEMA IF NOT EXISTS staging;

CREATE TABLE IF NOT EXISTS control.pipeline_loads (
    dataset_name text NOT NULL,
    reporting_year smallint NOT NULL,
    reporting_month smallint NOT NULL CHECK (reporting_month BETWEEN 1 AND 12),
    source_sha256 char(64) NOT NULL,
    source_row_count bigint NOT NULL,
    source_path text NOT NULL,
    loaded_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (dataset_name, reporting_year, reporting_month)
);

CREATE TABLE IF NOT EXISTS staging.bts_flights (
    year smallint NOT NULL,
    month smallint NOT NULL,
    day_of_month smallint NOT NULL,
    day_of_week smallint NOT NULL,
    flight_date date NOT NULL,
    reporting_airline text NOT NULL,
    dot_id_reporting_airline integer,
    tail_number text,
    flight_number_reporting_airline integer NOT NULL,
    origin_airport_id integer,
    origin_airport_seq_id integer,
    origin text NOT NULL,
    origin_city_name text,
    origin_state text,
    dest_airport_id integer,
    dest_airport_seq_id integer,
    dest text NOT NULL,
    dest_city_name text,
    dest_state text,
    crs_dep_time smallint,
    dep_time double precision,
    dep_delay_minutes double precision,
    dep_del15 boolean,
    crs_arr_time smallint,
    arr_time double precision,
    arr_delay_minutes double precision,
    arr_del15 boolean,
    cancelled boolean NOT NULL,
    cancellation_code text,
    diverted boolean NOT NULL,
    crs_elapsed_time double precision,
    actual_elapsed_time double precision,
    air_time double precision,
    distance double precision,
    carrier_delay double precision,
    weather_delay double precision,
    nas_delay double precision,
    security_delay double precision,
    late_aircraft_delay double precision
);

CREATE INDEX IF NOT EXISTS bts_flights_flight_date_idx
    ON staging.bts_flights (flight_date);

CREATE INDEX IF NOT EXISTS bts_flights_route_idx
    ON staging.bts_flights (origin, dest);

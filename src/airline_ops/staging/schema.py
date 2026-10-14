from dataclasses import dataclass

import pyarrow as pa


@dataclass(frozen=True)
class StagingColumn:
    source_name: str
    target_name: str
    data_type: pa.DataType


COLUMNS = (
    StagingColumn("Year", "year", pa.int16()),
    StagingColumn("Month", "month", pa.int8()),
    StagingColumn("DayofMonth", "day_of_month", pa.int8()),
    StagingColumn("DayOfWeek", "day_of_week", pa.int8()),
    StagingColumn("FlightDate", "flight_date", pa.date32()),
    StagingColumn("Reporting_Airline", "reporting_airline", pa.string()),
    StagingColumn("DOT_ID_Reporting_Airline", "dot_id_reporting_airline", pa.int32()),
    StagingColumn("Tail_Number", "tail_number", pa.string()),
    StagingColumn(
        "Flight_Number_Reporting_Airline",
        "flight_number_reporting_airline",
        pa.int32(),
    ),
    StagingColumn("OriginAirportID", "origin_airport_id", pa.int32()),
    StagingColumn("OriginAirportSeqID", "origin_airport_seq_id", pa.int32()),
    StagingColumn("Origin", "origin", pa.string()),
    StagingColumn("OriginCityName", "origin_city_name", pa.string()),
    StagingColumn("OriginState", "origin_state", pa.string()),
    StagingColumn("DestAirportID", "dest_airport_id", pa.int32()),
    StagingColumn("DestAirportSeqID", "dest_airport_seq_id", pa.int32()),
    StagingColumn("Dest", "dest", pa.string()),
    StagingColumn("DestCityName", "dest_city_name", pa.string()),
    StagingColumn("DestState", "dest_state", pa.string()),
    StagingColumn("CRSDepTime", "crs_dep_time", pa.int16()),
    StagingColumn("DepTime", "dep_time", pa.float64()),
    StagingColumn("DepDelayMinutes", "dep_delay_minutes", pa.float64()),
    StagingColumn("DepDel15", "dep_del15", pa.float64()),
    StagingColumn("CRSArrTime", "crs_arr_time", pa.int16()),
    StagingColumn("ArrTime", "arr_time", pa.float64()),
    StagingColumn("ArrDelayMinutes", "arr_delay_minutes", pa.float64()),
    StagingColumn("ArrDel15", "arr_del15", pa.float64()),
    StagingColumn("Cancelled", "cancelled", pa.float64()),
    StagingColumn("CancellationCode", "cancellation_code", pa.string()),
    StagingColumn("Diverted", "diverted", pa.float64()),
    StagingColumn("CRSElapsedTime", "crs_elapsed_time", pa.float64()),
    StagingColumn("ActualElapsedTime", "actual_elapsed_time", pa.float64()),
    StagingColumn("AirTime", "air_time", pa.float64()),
    StagingColumn("Distance", "distance", pa.float64()),
    StagingColumn("CarrierDelay", "carrier_delay", pa.float64()),
    StagingColumn("WeatherDelay", "weather_delay", pa.float64()),
    StagingColumn("NASDelay", "nas_delay", pa.float64()),
    StagingColumn("SecurityDelay", "security_delay", pa.float64()),
    StagingColumn("LateAircraftDelay", "late_aircraft_delay", pa.float64()),
)

SOURCE_COLUMNS = tuple(column.source_name for column in COLUMNS)
TARGET_COLUMNS = tuple(column.target_name for column in COLUMNS)
SOURCE_TYPES = {column.source_name: column.data_type for column in COLUMNS}


def staging_schema(metadata: dict[bytes, bytes] | None = None) -> pa.Schema:
    return pa.schema(
        [pa.field(column.target_name, column.data_type) for column in COLUMNS],
        metadata=metadata,
    )

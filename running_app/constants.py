import enum


class FieldTypes(enum.Enum):
    iso_date_string = 1
    iso_date_list = 2
    iso_time_string = 3
    iso_pace_string = 4
    iso_duration_string = 5
    decimal = 6
    integer = 7
    string = 8
    string_list = 9
    boolean = 10

import enum


class FieldTypes(enum.Enum):
    iso_date_string = 1
    iso_time_string = 2
    iso_pace_string = 3
    iso_duration_string = 4
    decimal = 5
    integer = 6
    string = 7
    string_list = 8
    boolean = 9

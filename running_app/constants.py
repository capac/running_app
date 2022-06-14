import enum


class FieldTypes(enum.Enum):
    iso_date_string = 1
    iso_time_string = 2
    iso_pace_string = 3
    decimal = 4
    integer = 5
    string = 6
    string_list = 7
    boolean = 8

import enum


class FieldTypes(enum.Enum):
    iso_date_string = 1
    iso_time_string = 2
    decimal = 3
    integer = 4
    string = 5
    string_list = 6
    boolean = 7

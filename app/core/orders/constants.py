from enum import StrEnumEnum


class OrderStatusEnum(StrEnumEnum):
    unlisted = "unlisted"
    ordered = "ordered"
    done = "done"

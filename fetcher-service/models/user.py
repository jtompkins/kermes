from collections import namedtuple

User = namedtuple(
    "User",
    [
        "user_id",
        "email",
        "delivery_email",
        "prefer_kindle",
        "send_threshold",
        "send_day",
    ],
)

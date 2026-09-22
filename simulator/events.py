from dataclasses import dataclass
from typing import Any


@dataclass
class ScenarioEvent:
    time: int
    type: str
    params: dict[str, Any]


def parse_events(raw_events: list[dict]) -> list[ScenarioEvent]:
    events = []

    for item in raw_events:
        event = ScenarioEvent(
            time=int(item["time"]),
            type=item["type"],
            params={
                key: value
                for key, value in item.items()
                if key not in {"time", "type"}
            },
        )

        events.append(event)

    return sorted(events, key=lambda x: x.time)

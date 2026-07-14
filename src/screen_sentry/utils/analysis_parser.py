import re
from dataclasses import dataclass
from enum import Enum, StrEnum


class ThreatLevel(Enum):
    THREAT = "THREAT"
    UNCERTAIN = "UNCERTAIN"
    NO_THREAT = "NO_THREAT"


class AnalysisSource(StrEnum):
    CAPTURE = "capture"
    WATCH = "watch"


@dataclass
class AnalysisImage:
    data: bytes
    source: AnalysisSource


@dataclass
class AnalysisResult:
    image: AnalysisImage
    level: ThreatLevel
    category: str | None
    message: str
    raw: str


def parse_analysis(image: AnalysisImage, raw: str) -> AnalysisResult:
    raw = raw.strip()

    match = re.match(
        r"^(THREAT|UNCERTAIN|NO_THREAT)(?::\s*([A-Z_]+))?\s*-\s*(.+)$", raw, re.DOTALL
    )

    if match:
        level_str, category, message = match.groups()
        level = ThreatLevel(level_str)
        return AnalysisResult(
            image,
            level=level,
            category=category if level != ThreatLevel.NO_THREAT else None,
            message=message.strip(),
            raw=raw,
        )

    return AnalysisResult(
        image,
        level=ThreatLevel.UNCERTAIN,
        category="PARSE_ERROR",
        message=raw,
        raw=raw,
    )

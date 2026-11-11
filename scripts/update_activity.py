"""Generate an SVG from GitHub's public contribution calendar using only Python."""

import argparse
from datetime import date, datetime, timedelta, timezone
from html import escape
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


class CalendarParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.dates = {}
        self.counts = {}
        self.current = None
        self.text = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "td" and "data-date" in attrs:
            self.dates[attrs["id"]] = attrs["data-date"]
        if tag == "tool-tip":
            self.current = attrs.get("for")
            self.text = []

    def handle_data(self, data):
        if self.current:
            self.text.append(data)

    def handle_endtag(self, tag):
        if tag == "tool-tip" and self.current:
            text = "".join(self.text).strip()
            match = re.match(r"([\d,]+) contributions?\b", text)
            if match:
                self.counts[self.current] = int(match[1].replace(",", ""))
            elif text.startswith("No contributions"):
                self.counts[self.current] = 0
            self.current = None

    def daily_counts(self):
        return {
            date.fromisoformat(day): self.counts[key]
            for key, day in self.dates.items() if key in self.counts
        }


def render(values, end):
    start = end - timedelta(days=30)
    days = [start + timedelta(days=i) for i in range(31)]
    missing = [day for day in days if day not in values]
    if missing:
        raise ValueError(f"Missing calendar data for {missing[0]}; retaining the previous SVG")
    counts = [values[day] for day in days]
    ceiling = max(4, ((max(counts) + 3) // 4) * 4)
    left, top, right, bottom = 65, 80, 1138, 275
    coords = [
        (left + i * (right - left) / 30, bottom - count * (bottom - top) / ceiling)
        for i, count in enumerate(counts)
    ]
    points = " ".join(f"{x:.1f},{y:.1f}" for x, y in coords)
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="350" viewBox="0 0 1200 350" role="img" aria-labelledby="title desc">',
        '<title id="title">Berwin\'s contribution activity</title>',
        f'<desc id="desc">{sum(counts)} contributions from {start} to {end}, from GitHub\'s public contribution calendar.</desc>',
        '<rect width="1200" height="350" rx="16" fill="#0d1117"/>',
        '<g font-family="Arial,sans-serif">',
        '<text x="35" y="39" fill="#79b8ff" font-size="20" font-weight="600">Building in public</text>',
        f'<text x="1160" y="39" text-anchor="end" fill="#9eb3cd" font-size="14">{sum(counts)} contributions / last 31 days</text>',
    ]
    for i in range(5):
        y = bottom - i * (bottom - top) / 4
        parts.extend([
            f'<path d="M{left} {y}H{right}" stroke="#243044" stroke-dasharray="4 6"/>',
            f'<text x="48" y="{y + 5}" fill="#9eb3cd" font-size="13" text-anchor="end">{ceiling * i // 4}</text>',
        ])
    parts.append(f'<polygon points="{left},{bottom} {points} {right},{bottom}" fill="#203657" opacity=".55"/>')
    parts.append(f'<polyline points="{points}" fill="none" stroke="#79b8ff" stroke-width="3" stroke-linejoin="round"/>')
    for day, count, (x, y) in zip(days, counts, coords):
        label = escape(f"{day}: {count} contributions")
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="#7ee7b7"><title>{label}</title></circle>')
    for i in [0, 5, 10, 15, 20, 25, 30]:
        parts.append(f'<text x="{coords[i][0]:.1f}" y="303" fill="#9eb3cd" font-size="13" text-anchor="middle">{days[i].strftime("%b %d")}</text>')
    parts.append(f'<text x="35" y="332" fill="#71849f" font-size="12">Source: public GitHub contribution calendar / updated {end}</text>')
    parts.append('</g></svg>')
    return "\n".join(parts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="Use a saved calendar HTML file")
    parser.add_argument("--end-date", type=date.fromisoformat, default=datetime.now(timezone.utc).date())
    args = parser.parse_args()
    if args.input:
        html = args.input.read_text()
    else:
        start = args.end_date - timedelta(days=30)
        url = f"https://github.com/users/3rw-1n/contributions?from={start}&to={args.end_date}"
        request = Request(url, headers={"User-Agent": "Berwin-Profile", "Accept-Language": "en-US"})
        with urlopen(request, timeout=30) as response:
            html = response.read().decode("utf-8")
    calendar = CalendarParser()
    calendar.feed(html)
    svg = render(calendar.daily_counts(), args.end_date)
    output = ROOT / "assets" / "activity.svg"
    output.write_text(svg)
    print(f"Updated {output}")


if __name__ == "__main__":
    main()

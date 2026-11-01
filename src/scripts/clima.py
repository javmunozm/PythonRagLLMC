import sys

from src.clients.weather import current_temperature
from src.services.weather import weather_report


def main(city: str) -> None:
    print(weather_report(city, current_temperature))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "Santiago")

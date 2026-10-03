from app.schemas.asset import Asset


class RoutingService:
    """Deterministic routing service to map components to domains."""

    DOMAIN_MAPPING = {
        "battery module": "Battery & Energy Storage",
        "battery pack": "Battery & Energy Storage",
        "cell": "Battery & Energy Storage",
        "inverter": "Power Electronics",
        "dc-dc converter": "Power Electronics",
        "igbt module": "Power Electronics",
        "capacitor": "Power Electronics",
        "contactor": "Power Electronics",
        "battery connector": "Power Electronics",
        "busbar": "Power Electronics",
        "permanent magnet": "Electric Drive Systems",
        "motor housing": "Electric Drive Systems",
        "cooling component": "Electric Drive Systems",
        "bearing": "Electric Drive Systems",
        "gateway ecu": "Control & Computing",
        "onboard charger": "Charging Electronics",
        "charging communication module": "Charging Electronics",
        "charging relay": "Charging Electronics",
        "wireless charging module": "Charging Electronics",
        "voltage sensor": "Sensors & Communication",
        "pressure sensor": "Sensors & Communication",
        "proximity sensor": "Sensors & Communication",
        "camera": "Sensors & Communication",
        "radar sensor": "Sensors & Communication",
        "ultrasonic sensor": "Sensors & Communication",
        "gps module": "Sensors & Communication",
        "can bus": "Sensors & Communication",
        "speaker": "Auxiliary Electronics",
        "usb charging module": "Auxiliary Electronics",
        "infotainment display": "Auxiliary Electronics",
        "touchscreen": "Auxiliary Electronics",
        "instrument cluster": "Auxiliary Electronics",
        "audio amplifier": "Auxiliary Electronics",
        "led lighting": "Auxiliary Electronics",
        "seat heater module": "Auxiliary Electronics",
        "electric compressor controller": "Auxiliary Electronics",
    }

    # Handling overlaps based on primary domains or fallback rules
    # pcb -> Control & Computing (or Power Electronics)
    # fuse, protection circuit -> Power Electronics
    # current sensor -> Sensors & Communication
    # transformer -> Power Electronics
    # hvac controller -> Control & Computing
    # bms -> Battery & Energy Storage

    OVERLAP_MAPPING = {
        "pcb": "Control & Computing",
        "fuse": "Power Electronics",
        "protection circuit": "Power Electronics",
        "current sensor": "Sensors & Communication",
        "transformer": "Power Electronics",
        "hvac controller": "Control & Computing",
        "bms": "Battery & Energy Storage",
        "motor controller": "Electric Drive Systems",
    }

    @classmethod
    def determine_domain(cls, asset: Asset) -> str:
        if not asset.component:
            return "Unknown"

        comp = asset.component.lower().strip()

        if comp in cls.DOMAIN_MAPPING:
            return cls.DOMAIN_MAPPING[comp]
        
        if comp in cls.OVERLAP_MAPPING:
            return cls.OVERLAP_MAPPING[comp]

        return "Unknown"

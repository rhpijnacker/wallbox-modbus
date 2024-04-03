import enum

class Control(int, enum.Enum):
    USER = 0,
    REMOTE = 1

class SetpointType(int, enum.Enum):
    CURRENT = 0,
    POWER = 1

class ChargerLockState(int, enum.Enum):
    UNLOCK = 0,
    LOCK = 1

class ChargerStates(int, enum.Enum):
    NO_CAR_CONNECTED = 0
    CHARGING = 1
    CONNECTED_WAITING_FOR_CAR_DEMAND = 2
    CONNECTED_CONTROLLED_BY_EVSE_APP = 3
    CONNECTED_NOT_CHARGING = 4
    CONNECTED_END_OF_SCHEDULE = 5
    NO_CAR_CONNECTED_AND_CHARGER_LOCKED = 6
    ERROR = 7
    CONNECTED_IN_QUEUE_BY_POWER_SHARING = 8
    ERROR_UNCONFIGURED_POWER_SHARING_SYSTEM = 9
    CONNECTED_IN_QUEUE_BY_POWER_BOOST = 10 # Home uses all available power
    DISCHARGING = 11

class RegisterAddresses(int, enum.Enum):
    CONTROL = 0x51       # RW, 0: User (default) / 1: Remote
    SETPOINT_TYPE = 0x53 # RW, 0: Current (default) / 1: Power by phase

    CHARGER_LOCK_STATE = 0x100 # RW, 0: Unlock / 1: Lock

    CHARGER_STATE = 0x219
    STATE_OF_CHARGE = 0x21a

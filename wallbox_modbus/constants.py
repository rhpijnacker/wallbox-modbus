import enum

class Control(int, enum.Enum):
    USER = 0,
    REMOTE = 1

class AutoChargingDischarging(int, enum.Enum):
    DISABLE = 0,
    ENABLE = 1

class SetpointType(int, enum.Enum):
    CURRENT = 0,
    POWER = 1

class ChargerLockState(int, enum.Enum):
    UNLOCK = 0,
    LOCK = 1

class Action(int, enum.Enum):
    START_CHARGING_DISCHARGING = 1,
    STOP_CHARGING_DISCHARGING = 2,
    REBOOT_CHARGER = 3,
    UPDATE_FIRMWARE = 4
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
    FIRMWARE_VERSION = 0x1      # RO
    SERIAL_HIGH = 0x2           # RO
    SERIAL_LOW = 0x3            # RO
    PART_NUMBER_1 = 0x4         # RO
    PART_NUMBER_2 = 0x5         # RO
    PART_NUMBER_3 = 0x6         # RO
    PART_NUMBER_4 = 0x7         # RO
    PART_NUMBER_5 = 0x8         # RO
    PART_NUMBER_6 = 0x9         # RO

    CONTROL = 0x51              # RW, 0: User (default) / 1: Remote
    AUTO_CHARGING_DISCHARGING = 0x52
                                # RW, 0: Disable / 1: Enable (default) 
    SETPOINT_TYPE = 0x53        # RW, 0: Current (default) / 1: Power by phase

    CHARGER_LOCK_STATE = 0x100  # RW, 0: Unlock / 1: Lock
    ACTION = 0x101              # RW, 1: Start (dis)charging / 2: Stop (dis)charging / 3: Reboot charger / 4: Update firmware
    CURRENT_SETPOINT = 0x102    # RW, AC max charging current (-32A to 32A)
    POWER_SETPOINT = 0x104      # RW, AC max charging power (-7400W to 7400W)

    MAX_AVAILABLE_CURRENT = 0x200   # RO  (0A to 32A)
    MAX_AVAILABLE_POWER = 0x202     # RO  (0W to 7400W)
    AC_CURRENT_RMS = 0x207          # RO  (0A to 100A)
    AC_VOLTAGE_RMS = 0x20a          # RO  (0V to 5000V)
    AC_ACTIVE_POWER_RMS = 0x20e     # RO  (0W to 50000W)

    CHARGER_STATE = 0x219
    STATE_OF_CHARGE = 0x21a     # RO, (0% to 100%)

import enum
class shifter_calibrate:
    def __init__(self):
        pass

    def to_dict(self):
        ret = dict()
        return ret

    def get_topic(self):
        return 'shifter/calibrate'

    def from_dict(input_dict):
        return shifter_calibrate(
        )

class shifter_shift:
    def __init__(self, gear):
        self.gear = gear #int8

    def to_dict(self):
        ret = dict()
        ret['gear'] = self.gear
        return ret

    def get_topic(self):
        return 'shifter/shift'

    def from_dict(input_dict):
        return shifter_shift(
            input_dict['gear'],
        )

class shifter_shift_up:
    def __init__(self):
        pass

    def to_dict(self):
        ret = dict()
        return ret

    def get_topic(self):
        return 'shifter/shift_up'

    def from_dict(input_dict):
        return shifter_shift_up(
        )

class shifter_shift_down:
    def __init__(self):
        pass

    def to_dict(self):
        ret = dict()
        return ret

    def get_topic(self):
        return 'shifter/shift_down'

    def from_dict(input_dict):
        return shifter_shift_down(
        )


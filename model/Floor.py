

class Floor:
    _free: int
    _max: int
    _floorName: str

    def __init__(self, free, used, floorName=""):
        self._free = free
        self._max = used + free
        self._floorName = floorName

    def __str__(self):
        return self._floorName + " :: Free Seats: " + str(self._free) + " Max Seats: " + str(self._max)

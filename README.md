# bibChairSnatcher

How does one write code that ugly?

This tool will grab the seat with the lowest number possible due to extreme performance enhancements and not because of laziness

## Config
Store a config.cfg file within the same folder as the python file / executable
```conf
[bib]
# Choose from "vormittags", "nachmittags", "abends", "nachts"
daytime="vormittags"
# 0 Days means today
daysOffset=0
# Choose from "first_floor", "second_floor", "empore", "third_floor", "ground_floor"
# Otherwise they will all be tried in the same order as above
preferredFloor= None
# Debug output
debug=True
# Save login cookie? Your password will not be stored in either way
saveLogin=True
```
# bibChairSnatcher

## run

`python snatch.py <path-to-cfg> <path-to-secret>`

example:

`python snatch.py config_morning.cfg resources/secret`

or without secret file:

`python snatch.py config_morning.cfg`
(then you have to type in password evrytim)

## misc

### cookie

cookie gets created automatically and if a cookie is available and valid it will be used

### config

- if you don't specify floor, it will go from best to worst floor in order while looking for a seat
- daysOffset means how many days from today you want to reserve a spot
- daytime should be self-explanatory: possible values: `["vormittags", "nachmittags", "abends", "nachts"]`

### secret

create `secret` file:
first line is your login name
second line your password (scary)

example:

```
@1234567
thisismyrealpassword
```

### faq and help

if you can't run it or if there is a problem, i don't care
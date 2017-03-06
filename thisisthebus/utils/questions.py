import datetime


def today_or_another_day():

    today = datetime.datetime.now().strftime("%Y-%m-%d")
    print("Which day in this location?")
    print("1) Today (%s)" % today)
    print("2) Some other date")

    response = input("Enter 1-2: ")

    try:
        response = int(response)
    except ValueError:
        return

    if response == 1:
        day = today
    elif response == 2:
        day = str(input("Enter YYYY-MM-DD\n"))
    else:
        return
    return day
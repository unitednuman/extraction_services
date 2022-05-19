from allsop import AllSop


def run():
    try:
        AllSop().scraper()
    except BaseException as be:
        print(be)




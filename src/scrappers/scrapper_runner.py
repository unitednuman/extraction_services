from scrappers.allsop import AllSop


def run():
    try:
        print("Running.......")
        AllSop().scraper()
    except BaseException as be:
        print(be)

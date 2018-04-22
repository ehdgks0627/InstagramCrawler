from HashTagSearchManager import HashTagSearchManager
import logging as log

if __name__ == '__main__':
    log.basicConfig(level=log.INFO)
    HashTagSearchManager().extract_recent_tag("food")
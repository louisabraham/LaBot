
# logger = logging.getLogger()
# path = Path(os.getcwd())
# LabotPath = str(path.parent.parent)

import logging
import json
import pickle
import os

logger = logging.getLogger()


def make_i18n_pickle():
    path = os.getcwd() + "/sources/data/i18n_fr.json"
    logger.debug(path)

    try:
        if not os.path.exists("./sources/pickles"):
            os.makedirs("./sources/pickles")

        f = open(path, encoding="utf-8", mode="r")
        i18n = json.load(f)
        f.close()
        f = open("./sources/pickles/I18nPickle", "wb+")
        i18n_dict = i18n["texts"]
        pickle.dump(i18n_dict, f)
        f.close()
        logger.debug("Made pickle with i18n information from %s", path)
        return i18n_dict
    except FileNotFoundError:
        logger.error(
            "Coudn't find json file. Please make sure to run decompile.sh before this script."
        )


def read_objects():
    path = "./sources/data/MonsterMiniBoss.json"
    logger.debug("Making pickle with item information from %s", path)

    try:
        f = open(path, "r")
        items = json.load(f)
        item_dict = {}
        for item in items:
            item_dict[item["id"]] = item
        f.close()

        if not os.path.exists("./sources/pickles"):
            os.makedirs("./sources/pickles")

        f = open("./sources/pickles/MonsterMiniBossPickle", "wb+")
        pickle.dump(item_dict, f)
        f.close()
        logger.debug(
            "Made pickle with item information at %s", "./sources/pickles/MonstersPickle"
        )
        return item_dict
    except FileNotFoundError:
        logger.error(
            "Coudn't find json file. Please make sure to run decompile.sh before this script."
        )


if __name__ == "__main__":
    #make_i18n_pickle()
    read_objects()
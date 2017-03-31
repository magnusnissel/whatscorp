import os
import re
import glob
import base64
import xml.etree.ElementTree as etree
from dateutil.parser import parse


BASE_DIR = os.path.dirname(os.path.realpath(__file__))
SETTINGS_PATH = os.path.join(BASE_DIR, "settings.xml")
IMPORT_DIR = os.path.join(BASE_DIR, "import")
CORPUS_DIR = os.path.join(BASE_DIR, "corpus")
XML_DIR = os.path.join(CORPUS_DIR, "xml")
CSV_DIR = os.path.join(CORPUS_DIR, "csv")



"""
Intentionally vague, are their date/time differences?
In any case, the part before the first dash is date & time, followed by the
speaker followed by a colon and the message text
"""

LINE_RE = re.compile(r"([^-\n\r]+)-([^:\n\r]+):([^\n\r]+)$",
                     flags=re.M | re.I | re.U)


def parse_date(s):
    try:
        return parse(s, fuzzy=True)
    except ValueError:
        return None


def parse_lines(text):
    lines = []
    for m in LINE_RE.finditer(text):
        ln = {"TIMESTAMP": parse_date(m.group(1).strip("\n").strip()),
              "SPEAKER": m.group(2).strip(),
              "MESSAGE": m.group(3).strip()}
        lines.append(ln)
    return lines


def scramble(name):
    """Note: This is not supposed to provide security / actual anonymity.
    It is merely a means to convert names into something a researcher
    or reader of a paper will not be able to easily associate with an
    actual person's name or nickname. A simple (reversible) base64 encoding,
    with the padding removed and +- instead of /_."""
    return base64.urlsafe_b64encode(name.encode()).decode("utf-8").strip("=")


def pseudonymize_lines(lines, pseudo):
    for ln in lines:
        ln["SPEAKER"] = pseudo[ln["SPEAKER"]]
    return lines


def to_xml(lines):
    root = etree.Element("chat")
    for ln in lines:
        if ln["TIMESTAMP"]:
            ts = ln["TIMESTAMP"].isoformat()
        else:
            ts = ""
        m = etree.Element("message")
        m.set("speaker", ln["SPEAKER"])
        m.set("timestamp", ts)
        m.text = ln["MESSAGE"]
        root.append(m)
    return etree.ElementTree(root)


def process_file(fp, set):
    with open(fp, encoding="utf-8") as h:
        text = h.read()
    lines = parse_lines(text)
    speakers = {ln["SPEAKER"] for ln in lines}
    if set["scramble"]:
        pseudo = {s: scramble(s) for s in speakers}
        lines = pseudonymize_lines(lines, pseudo)
        speakers = {ln["SPEAKER"] for ln in lines}
    if set["split"]:
        by_speaker = {s: [] for s in speakers}
        for ln in lines:
            by_speaker[ln["SPEAKER"]].append(ln)
        for speaker, lines in by_speaker.items():
            xml = to_xml(lines)
            fn = "chat_{}".format(speaker)
            xml_fp = os.path.join(XML_DIR, "{}.xml".format(fn))
            csv_fp = os.path.join(CSV_DIR, "{}.csv".format(fn))
            print(fn)
            xml.write(xml_fp, encoding='utf-8', xml_declaration=True)
    else:
        xml = to_xml(lines)
        fn = "chat_{}".format("-".join(speakers))
        xml_fp = os.path.join(XML_DIR, "{}.xml".format(fn))
        csv_fp = os.path.join(CSV_DIR, "{}.csv".format(fn))
        xml.write(xml_fp, encoding='utf-8', xml_declaration=True)
        print(fn)


def get_settings():
    s = {"scramble": False, "split": False}  # defaults if missing/error
    try:
        tree = etree.parse(SETTINGS_PATH)
    except IOError:
        pass
    else:
        scramble = tree.find(".//scramble")
        split = tree.find(".//split")
        try:
            s["scramble"] = bool(int(scramble.text))
            s["log"] = bool(int(scramble.get("log", "1")))

        except (AttributeError, ValueError):
            pass
        try:
            s["split"] = bool(int(split.text))
        except (AttributeError, ValueError):
            pass
    return s


def main():
    settings = get_settings()

    try:
        os.makedirs(XML_DIR)
    except FileExistsError:
        pass
    try:
        os.makedirs(CSV_DIR)
    except FileExistsError:
        pass

    for fp in glob.iglob(os.path.join(IMPORT_DIR, "*.txt")):
        process_file(fp, settings)


if __name__ == "__main__":
    main()

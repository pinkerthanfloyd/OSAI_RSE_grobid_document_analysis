from __future__ import annotations

import re
from lxml import etree

TEI_NS = {"tei": "http://www.tei-c.org/ns/1.0"}
URL_RE = re.compile(r"https?://[^\s<>\"]+")


def _root(tei_xml: str) -> etree._Element:
    return etree.fromstring(tei_xml.encode("utf-8"))


def extract_abstract(tei_xml: str) -> str:
    root = _root(tei_xml)
    nodes = root.xpath("//tei:teiHeader//tei:profileDesc//tei:abstract", namespaces=TEI_NS)
    if not nodes:
        return ""
    text = " ".join(nodes[0].itertext())
    return re.sub(r"\s+", " ", text).strip()


def count_figures(tei_xml: str) -> int:
    root = _root(tei_xml)
    figures = root.xpath("//tei:text//tei:figure", namespaces=TEI_NS)
    return len(figures)


def extract_links(tei_xml: str) -> list[str]:
    root = _root(tei_xml)
    links: set[str] = set()

    # Structured links
    for node in root.xpath("//tei:ref[@target] | //tei:ptr[@target]", namespaces=TEI_NS):
        t = node.get("target")
        if t and t.startswith(("http://", "https://")):
            links.add(t.strip())

    # Fallback regex scan over all text
    all_text = etree.tostring(root, encoding="unicode", method="text")
    for m in URL_RE.finditer(all_text):
        links.add(m.group(0).rstrip(").,;"))

    return sorted(links)

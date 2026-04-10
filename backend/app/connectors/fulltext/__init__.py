from backend.app.connectors.fulltext.base import FullTextConnector
from backend.app.connectors.fulltext.cairn import CairnConnector
from backend.app.connectors.fulltext.elsevier import ElsevierTdmConnector
from backend.app.connectors.fulltext.erudit import EruditConnector
from backend.app.connectors.fulltext.europe_pmc import EuropePmcConnector
from backend.app.connectors.fulltext.hal import HalFullTextConnector
from backend.app.connectors.fulltext.openedition import OpenEditionConnector

__all__ = [
    "CairnConnector",
    "ElsevierTdmConnector",
    "EruditConnector",
    "EuropePmcConnector",
    "FullTextConnector",
    "HalFullTextConnector",
    "OpenEditionConnector",
]

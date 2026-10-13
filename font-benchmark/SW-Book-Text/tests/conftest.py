import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "specimen"))
import pytest
from fontTools.ttLib import TTFont

FONTS = {"Regular": os.path.join(ROOT, "fonts", "SWBookText-Regular.ttf"),
         "Bold": os.path.join(ROOT, "fonts", "SWBookText-Bold.ttf")}


@pytest.fixture(scope="session", params=["Regular", "Bold"])
def weight(request):
    return request.param


@pytest.fixture(scope="session")
def path(weight):
    return FONTS[weight]


@pytest.fixture(scope="session")
def font(path):
    return TTFont(path)

"""Makes NGO data + nav available in every template (used by base.html)."""
from .data_loader import ngo


def ngo_data(request):
    return {"ngo": ngo()}

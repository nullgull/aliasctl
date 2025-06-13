from textual.theme import Theme
from types import SimpleNamespace


COLORS = SimpleNamespace(
	base="#d2aaff",
	background="#12021f", # selected line in text area
	surface="#291B35", # input areas
	boost="#41344b"
)

default_theme = Theme(
	name="default_theme",
	primary=COLORS.base,
	foreground=COLORS.base,
	background=COLORS.background,
	surface=COLORS.surface,
	boost=COLORS.boost
)
import json
from pathlib import Path
from datetime import datetime


CONFIG_DIR = Path.home() / ".aliasctl"
ALIASES_FILE = CONFIG_DIR / "aliases.json"
DOMAIN_FILE = CONFIG_DIR / "domain"
ALIAS_TYPE_STANDARD = "standard"
ALIAS_TYPE_CUSTOM = "custom"


def ensure_config():
	CONFIG_DIR.mkdir(exist_ok=True)

	if not DOMAIN_FILE.exists() or not DOMAIN_FILE.read_text().strip():
		domain = input("Enter your domain: ").strip()
		if not domain or "@" in domain:
			raise ValueError("Invalid domain format.")
		DOMAIN_FILE.write_text(domain + "\n")
		print(f"Saved domain to {DOMAIN_FILE}")

	if not ALIASES_FILE.exists():
		ALIASES_FILE.write_text(json.dumps({ALIAS_TYPE_STANDARD: {}, ALIAS_TYPE_CUSTOM: {}}))


def get_domain():
	return DOMAIN_FILE.read_text().strip()


def get_alias(identifier):
	aliases = load_aliases()

	for alias_type in [ALIAS_TYPE_STANDARD, ALIAS_TYPE_CUSTOM]:
		for key, value in aliases.get(alias_type, {}).items():
			if value["identifier"] == identifier:
				return f"{key}@{get_domain()}"

	return None


def load_aliases():
	return json.loads(ALIASES_FILE.read_text())


def alias_attributes(identifier):
	return {
		"identifier": identifier,
		"created": datetime.utcnow().isoformat() + "Z"
	}


def generate_standard_alias_identifier(standard_aliases):
	nums = [int(k) for k in standard_aliases] if standard_aliases else []
	last = max(nums) if nums else -1
	return f"{last + 1:04d}"


def save_aliases(data):
	ALIASES_FILE.write_text(json.dumps(data, indent=2))


def create_alias(identifier, custom=None):
	# Check if alias for this identifier already exists
	alias = get_alias(identifier)
	if alias:
		return alias

	aliases = load_aliases()
	domain = get_domain()
	alias_type = ALIAS_TYPE_CUSTOM if custom else ALIAS_TYPE_STANDARD
	scoped_aliases = aliases.setdefault(alias_type, {})

	if custom and custom in scoped_aliases:
		raise ValueError(f"❌ Custom alias '{custom}' already exists.")

	alias_key = custom if custom else generate_standard_alias_identifier(scoped_aliases)
	scoped_aliases[alias_key] = alias_attributes(identifier)

	save_aliases(aliases)
	return f"{alias_key}@{domain}"


def delete_alias(identifier):
	aliases = load_aliases()
	domain = get_domain()

	for alias_type in [ALIAS_TYPE_STANDARD, ALIAS_TYPE_CUSTOM]:
		for alias_key, attrs in list(aliases.get(alias_type, {}).items()):
			if attrs.get("identifier") == identifier:
				del aliases[alias_type][alias_key]
				save_aliases(aliases)
				return f"{alias_key}@{domain}"

	return None
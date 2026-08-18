import json
import os
from typing import Any, Dict

import yaml


class ConfigurationError(Exception):
    pass


class ConfigurationLoader:
    """Loads and validates configuration from YAML and JSON files."""

    def __init__(self, config_dir: str = "configs"):
        self.config_dir = config_dir

    def _get_path(self, filename: str) -> str:
        return os.path.join(self.config_dir, filename)

    def load_yaml(self, filename: str) -> Dict[str, Any]:
        """Loads a YAML configuration file."""
        filepath = self._get_path(filename)
        if not os.path.exists(filepath):
            raise ConfigurationError(f"Configuration file not found: {filepath}")
        try:
            with open(filepath, "r") as f:
                return yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Error parsing YAML file {filepath}: {e}")

    def load_json(self, filename: str) -> Dict[str, Any]:
        """Loads a JSON configuration file."""
        filepath = self._get_path(filename)
        if not os.path.exists(filepath):
            raise ConfigurationError(f"Configuration file not found: {filepath}")
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Error parsing JSON file {filepath}: {e}")

    def load_all_configs(self) -> Dict[str, Any]:
        """Loads all configuration files into a single dictionary."""
        config: Dict[str, Any] = {}
        
        # Load main config
        main_config = self.load_yaml("config.yaml")
        config["main"] = main_config
        
        # Determine active profile (can be overridden by env variable)
        active_profile = os.environ.get("RATC_PROFILE", main_config.get("active_profile", "development"))
        config["active_profile"] = active_profile

        # Load subsystem configs
        try:
            config["scheduler"] = self.load_yaml("scheduler.yaml")
        except ConfigurationError:
            config["scheduler"] = {}

        try:
            config["telemetry"] = self.load_yaml("telemetry.yaml")
        except ConfigurationError:
            config["telemetry"] = {}
            
        try:
            config["experiment"] = self.load_yaml("experiment.yaml")
        except ConfigurationError:
            config["experiment"] = {}

        try:
            config["logging"] = self.load_yaml("logging.yaml")
        except ConfigurationError:
            config["logging"] = {}

        # Load profiles
        try:
            config["client_profiles"] = self.load_json("client_profiles.json").get("profiles", [])
        except ConfigurationError:
            config["client_profiles"] = []

        try:
            config["privacy_profiles"] = self.load_json("privacy_profiles.json").get("profiles", [])
        except ConfigurationError:
            config["privacy_profiles"] = []

        return config

# Create a default instance for easy importing
config_loader = ConfigurationLoader()

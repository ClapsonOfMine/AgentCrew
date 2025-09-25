from typing import Dict, Optional
from AgentCrew.modules.custom_llm import (
    DeepInfraService,
    CustomLLMService,
    GithubCopilotService,
    GithubCopilotResponseService,
)
from AgentCrew.modules.google import GoogleAINativeService
from AgentCrew.modules.llm.base import BaseLLMService
from AgentCrew.modules.anthropic import AnthropicService
from AgentCrew.modules.groq import GroqService

from AgentCrew.modules.config import ConfigManagement
from AgentCrew.modules.openai import OpenAIResponseService


class ServiceManager:
    """Singleton manager for LLM service instances."""

    _instance = None

    @classmethod
    def get_instance(cls):
        """Get the singleton instance of ServiceManager."""
        if cls._instance is None:
            cls._instance = ServiceManager()
        return cls._instance

    def __init__(self):
        """Initialize the service manager with empty service instances."""
        if ServiceManager._instance is not None:
            raise RuntimeError(
                "ServiceManager is a singleton. Use get_instance() instead."
            )

        self.services: Dict[str, BaseLLMService] = {}
        self.service_classes = {
            "claude": AnthropicService,
            "groq": GroqService,
            "openai": OpenAIResponseService,
            "google": GoogleAINativeService,
            "deepinfra": DeepInfraService,
            "github_copilot": GithubCopilotService,
            "copilot_response": GithubCopilotResponseService,
        }
        # Store details for custom providers
        self.custom_provider_details: Dict[str, Dict] = {}
        self._load_custom_provider_configs()

    def _load_custom_provider_configs(self):
        """Loads configurations for custom LLM providers."""
        try:
            config_manager = ConfigManagement()
            custom_providers = config_manager.read_custom_llm_providers_config()
            for provider_config in custom_providers:
                name = provider_config.get("name")
                # We are interested in 'openai_compatible' type for CustomLLMService
                if name and provider_config.get("type") == "openai_compatible":
                    if not provider_config.get("api_base_url"):
                        print(
                            f"Warning: Custom provider '{name}' is missing 'api_base_url' and will be skipped."
                        )
                        continue
                    self.custom_provider_details[name] = {
                        "api_base_url": provider_config.get("api_base_url"),
                        "api_key": provider_config.get("api_key", ""),
                        "extra_headers": provider_config.get("extra_headers", {}),
                    }
        except Exception as e:
            print(f"Error loading custom LLM provider configurations for services: {e}")

    def initialize_standalone_service(self, provider: str) -> BaseLLMService:
        """
        Initializes and returns a new service instance for the specified provider.
        This does not cache the service instance in self.services.
        """
        if provider in self.custom_provider_details:
            details = self.custom_provider_details[provider]
            api_key = details.get("api_key", "")
            extra_headers = details.get("extra_headers", None)

            if not details.get("api_base_url"):
                raise ValueError(
                    f"Missing api_base_url for custom provider: {provider}"
                )

            if (
                details.get("api_base_url", "")
                .rstrip("/")
                .endswith(".githubcopilot.com")
            ):
                # Special case for OpenAI compatible custom providers
                return GithubCopilotService(api_key=api_key, provider_name=provider)
            else:
                return CustomLLMService(
                    base_url=details["api_base_url"],
                    api_key=api_key,
                    provider_name=provider,
                    extra_headers=extra_headers,
                )
        elif provider in self.service_classes:
            return self.service_classes[provider]()
        else:
            known_providers = list(self.service_classes.keys()) + list(
                self.custom_provider_details.keys()
            )
            raise ValueError(
                f"Unknown provider: {provider}. Available providers: {', '.join(sorted(list(set(known_providers))))}"
            )

    def get_service(self, provider: str) -> BaseLLMService:
        """
        Get or create a service instance for the specified provider.
        Caches the instance for subsequent calls.

        Args:
            provider: The provider name

        Returns:
            An instance of the appropriate LLM service
        """
        if provider in self.services:
            return self.services[provider]

        service_instance: Optional[BaseLLMService] = None

        if provider in self.custom_provider_details:
            details = self.custom_provider_details[provider]
            api_key = details.get("api_key", "")
            extra_headers = details.get("extra_headers", None)

            if not details.get("api_base_url"):
                raise RuntimeError(
                    f"Configuration error: Missing api_base_url for custom provider {provider}"
                )

            try:
                if (
                    details.get("api_base_url", "")
                    .rstrip("/")
                    .endswith(".githubcopilot.com")
                ):
                    # Special case for OpenAI compatible custom providers
                    service_instance = GithubCopilotService(
                        api_key=api_key, provider_name=provider
                    )
                else:
                    service_instance = CustomLLMService(
                        base_url=details["api_base_url"],
                        api_key=api_key,
                        provider_name=provider,
                        extra_headers=extra_headers,
                    )
            except Exception as e:
                raise RuntimeError(
                    f"Failed to initialize custom provider service '{provider}': {str(e)}"
                )

        elif provider in self.service_classes:
            try:
                service_instance = self.service_classes[provider]()
            except Exception as e:
                raise RuntimeError(
                    f"Failed to initialize built-in '{provider}' service: {str(e)}"
                )

        if service_instance:
            self.services[provider] = service_instance
            return service_instance
        else:
            known_providers = list(self.service_classes.keys()) + list(
                self.custom_provider_details.keys()
            )
            raise ValueError(
                f"Unknown provider: {provider}. Available providers: {', '.join(sorted(list(set(known_providers))))}"
            )

    def set_model(self, provider: str, model_id: str) -> bool:
        """
        Set the model for a specific provider.

        Args:
            provider: The provider name
            model_id: The model ID to use

        Returns:
            True if successful, False otherwise
        """
        service = self.get_service(provider)
        if hasattr(service, "model"):
            service.model = model_id
            return True
        return False

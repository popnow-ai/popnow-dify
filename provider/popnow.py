from typing import Any
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from client import PopNowClient, PopNowError

class PopnowProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            PopNowClient(credentials.get('api_key')).invoke('balance', {})
        except PopNowError as error:
            raise ToolProviderCredentialValidationError(str(error)) from None

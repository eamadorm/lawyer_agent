import google.auth
from google.cloud import modelarmor_v1
from loguru import logger


class ModelArmorGuard:
    def __init__(self, project_id: str, location: str, template_id: str):
        self.template_path = (
            f"projects/{project_id}/locations/{location}/templates/{template_id}"
        )
        self.client = None

        try:
            creds, _ = google.auth.default()
            # Inicializamos el cliente apuntando al endpoint regional correcto
            self.client = modelarmor_v1.ModelArmorClient(
                transport="rest",
                client_options={
                    "api_endpoint": f"https://modelarmor.{location}.rep.googleapis.com"
                },
                credentials=creds,
            )
            logger.success("✅ Model Armor Client Initialized")
        except Exception as e:
            logger.warning(f"⚠️ Model Armor Init Failed: {e}")

    def sanitize_prompt(self, prompt: str) -> bool:
        """Retorna True si es seguro, False si fue bloqueado."""
        if not self.client:
            return True  # Fail open si no hay cliente (o fail close según tu política)

        try:
            user_prompt_data = modelarmor_v1.DataItem(text=prompt)
            request = modelarmor_v1.SanitizeUserPromptRequest(
                name=self.template_path, user_prompt_data=user_prompt_data
            )
            response = self.client.sanitize_user_prompt(request)

            if (
                response.sanitization_result.filter_match_state
                == modelarmor_v1.FilterMatchState.MATCH_FOUND
            ):
                logger.error(
                    f"🚨 Prompt Blocked by Model Armor: {response.sanitization_result}"
                )
                return False

            return True
        except Exception as e:
            logger.error(f"⚠️ Prompt Sanitization Error: {e}")
            return True

    def sanitize_response(self, text: str) -> str:
        """Retorna el texto sanitizado o lanza error si es bloqueado."""
        if not self.client:
            return text

        try:
            llm_resp_data = modelarmor_v1.DataItem(text=text)
            request = modelarmor_v1.SanitizeModelResponseRequest(
                name=self.template_path, model_response_data=llm_resp_data
            )
            response = self.client.sanitize_model_response(request)

            if (
                response.sanitization_result.filter_match_state
                == modelarmor_v1.FilterMatchState.MATCH_FOUND
            ):
                logger.error(
                    f"🚨 Response Blocked by Model Armor: {response.sanitization_result}"
                )
                return "🚫 **Security Alert**: The response was blocked by security policy."

            # Nota: Si Model Armor soportara redacción automática en esta versión, devolveríamos response.data
            return text
        except Exception as e:
            logger.error(f"⚠️ Response Sanitization Error: {e}")
            return text
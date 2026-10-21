from src.config import Settings, settings


def test_settings_defaults():
    assert settings.PROJECT_NAME == "Nexum AI: Secure Image Analyzer Agent"
    assert settings.VERSION == "1.0.0"
    assert settings.MODEL_NAME == "gemini-3.6-flash"
    assert isinstance(settings.GOOGLE_API_KEY, str)


def test_settings_instance():
    custom_settings = Settings()
    assert custom_settings.PROJECT_NAME == settings.PROJECT_NAME
    assert custom_settings.VERSION == settings.VERSION
    assert custom_settings.MODEL_NAME == settings.MODEL_NAME

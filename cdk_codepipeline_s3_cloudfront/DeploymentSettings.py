from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict
)


class DeploymentSettingsConfiguration(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_prefix='CODEPIPELINE_',
        extra='ignore'
    )

    GITHUB_REPO_OWNER: str = "OWNER"
    """GitHub repository owner"""

    GITHUB_REPO_NAME: str
    """GitHub repository name"""

    GITHUB_REPO_BRANCH: str = "main"
    """GitHub repository branch"""

    SECRETS_MANAGER_GITHUB_TOKEN_KEY: str = "github-token"


DeploymentSettings = DeploymentSettingsConfiguration()

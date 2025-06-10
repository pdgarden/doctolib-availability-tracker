from typing import Literal

from pydantic import Field, SecretStr, computed_field
from pydantic_settings import BaseSettings


class Configuration(BaseSettings):
    # Common
    environment: Literal["local", "dev", "preprod", "prod"] = Field(description="Execution environment")

    # Emails
    sender_email: str = Field(description="Gmail account used to send email")
    sender_gmail_password: SecretStr = Field(description="Sender gmail app password used to send email")
    receiver_email: str = Field(description="Gmail account used to receive email")
    smtp_server: str = Field(description="SMTP server to use to send email")

    # Scraper
    headless: bool = Field(description="Set to true to run in headless mode", default=True)

    # Search
    search_term: str = Field(description="Search term to use in doctolib search page", examples=["ORL"])
    search_place: str = Field(description="Search place to use in doctolib search page", examples=["Paris", "Agen"])

    # Filter appointments
    nb_days_filter: int = Field(
        default=14,
        description="Appointments starting in more than this number of days must be deleted",
    )
    raw_filtered_doctor_names: str | None = Field(
        default=None,
        description="Doctor names that must be filtered when checking interesting appointments."
        "Value must correspond to the value in doctolib and is case sensitive."
        "Names must be separated by '|'.",
        examples=["Dupont", "Dupont|DURAND"],
    )
    raw_filtered_cities: str | None = Field(
        default=None,
        description="Cities that must be filtered when checking interesting appointments."
        "Value must correspond to the value in doctolib and is case sensitive."
        "Names must be separated by '|'.",
        examples=["Périgueux", "Agen"],
    )

    @computed_field
    def filtered_doctor_names(self) -> list[str]:
        return self.raw_filtered_doctor_names.split("|") if self.raw_filtered_doctor_names is not None else []

    @computed_field
    def filtered_cities(self) -> list[str]:
        return self.raw_filtered_cities.split("|") if self.raw_filtered_cities is not None else []


config = Configuration(_env_file=".env")

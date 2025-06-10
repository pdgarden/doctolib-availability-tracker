from loguru import logger

from src import constants
from src.configuration import config
from src.notify import send_email
from src.scraper import Scraper


def main() -> None:
    """Main program."""
    logger.info("Start")
    scraper = Scraper(
        search_term=config.search_term,
        search_place=config.search_place,
        filtered_doctor_names=config.filtered_doctor_names,
        filtered_cities=config.filtered_cities,
        nb_days_filter=config.nb_days_filter,
        start_url=constants.URL_DOCTOLIB,
        headless=config.headless,
    )
    scraper.scrap_scenario()

    if len(scraper.accepted_availabilities) > 0:
        availabilities = scraper.get_accepted_availabilities_pretty()
        send_email(
            receiver_email=config.receiver_email,
            subject=f"""[Doctolib Tracker] Nouveaux RDV disponibles pour\
                    {config.search_term} ({config.search_place})""",
            message_txt=f"""{availabilities.get("message_txt")}""",
            message_html=f"""{availabilities.get("message_html")}""",
        )

    logger.info("end")


if __name__ == "__main__":
    main()

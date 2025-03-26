"""
Get doctor availability.
"""

# ------------------------------------------------------------------------------------------------ #
# Imports

import re
import time
from datetime import date, timedelta

from loguru import logger
from pydantic import BaseModel
from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from src import constants

# ------------------------------------------------------------------------------------------------ #
# Models


class DoctorAvailability(BaseModel):
    """Data model for doctor availability."""

    doctor_name: str
    next_availability: date | None
    address: str


# ------------------------------------------------------------------------------------------------ #
# Class


class Scraper:
    """Class to scrap doctor availability.

    TODO: Add scenario explanation and context.
    """

    def __init__(
        self,
        search_term: str,
        search_place: str,
        filtered_doctor_names: list[str],
        filtered_cities: list[str],
        headless: bool,
        nb_days_filter: int = 14,
        start_url: str = constants.URL_DOCTOLIB,
    ) -> None:
        """Init the method.

        Args::
            search_term (str): Search term to use in doctolib search page, (e.g. "ORL")
            search_place (str): Search place to use in doctolib search page, (e.g. "Paris")
            filtered_doctor_names (list[str]): Availabilities of doctors with a name in this list will be filtered
            filtered_cities (list[str]): Availabilities of cities with a name in this list will be filtered
            nb_days_filter (int): Availabilities after today + nb_days_filter will be filtered
            start_url (str): Doctolib search place: (e.g."https://www.doctolib.fr/")
        """
        self.search_term: str = search_term
        self.search_place: str = search_place
        self.start_url: str = start_url
        self.nb_days_filter: str = nb_days_filter
        self.filtered_doctor_names: str = filtered_doctor_names
        self.filtered_cities: str = filtered_cities
        self.availabilities: list[DoctorAvailability] = []

        # Browser
        if headless:
            chrome_options = Options()
            chrome_options.add_argument("--headless=new")
        else:
            chrome_options = None

        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
        self.wait: WebDriverWait = WebDriverWait(self.driver, 1.5)

    def open_browser(self) -> None:
        """Open browser."""
        self.driver.get(url=self.start_url)

    def handle_cookies(self) -> None:
        """Handle cookies."""
        try:
            cookie_disagree_element = "button#didomi-notice-agree-button"
            accept_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, cookie_disagree_element)))
            accept_button.click()
        except TimeoutException as exc:
            logger.warning(f"Couldn't handle cookies. Perhaps not asked: {exc.__class__.__name__}")

    def launch_search(self) -> None:
        """Launch search."""
        time.sleep(2)
        # Find and click the search input field (updated selector)
        search_input = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input.searchbar-input.searchbar-query-input"))
        )
        search_input.click()

        # Type the search term
        search_input.send_keys(self.search_term)

        # Wait for suggestions to appear
        time.sleep(1)

        # Select the first suggestion (updated selector)
        first_suggestion = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.searchbar-result.searchbar-result-active"))
        )
        first_suggestion.click()

        # Search place
        search_input = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input.searchbar-input.searchbar-place-input"))
        )
        search_input.click()
        search_input.send_keys(self.search_place)
        time.sleep(1)
        first_suggestion = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.searchbar-result.searchbar-result-active"))
        )
        first_suggestion.click()

        # Click the search button (updated selector)
        search_button = self.driver.find_element(By.CSS_SELECTOR, ".searchbar-submit-button")
        search_button.click()

    def extract_doctor_availability(self) -> None:
        """Extract doctor availability."""
        time.sleep(3)

        doctors_elements = self.driver.find_elements(By.CSS_SELECTOR, "li.w-full")
        for i, doctor_element in enumerate(doctors_elements):
            try:
                logger.debug(i)
                time.sleep(1)
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", doctor_element
                )

                doctor_name = (
                    WebDriverWait(doctor_element, 1.5)
                    .until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "h2.dl-text.dl-text-body.dl-text-bold.dl-text-s.dl-text-primary-110")
                        )
                    )
                    .text
                )
                address = doctor_element.find_elements(By.CLASS_NAME, "dl-text-regular.dl-text-s")[2].text

                next_availability = self.get_next_availability_date(doctor_element=doctor_element)

                doctor = DoctorAvailability(
                    doctor_name=doctor_name,
                    next_availability=next_availability,
                    address=address,
                )
                logger.debug(doctor)
                self.availabilities.append(doctor)

            except Exception as exc:
                logger.info(f"Skipped {i}\n {exc}")

    def get_next_availability_date(self, doctor_element: WebElement) -> date | None:
        """Get the next availability date from a doctor element.

        TODO: Improve readability and add unit test
        """

        # If the doctor schedule is not empty this week
        week_availabilities = doctor_element.find_elements(
            By.CSS_SELECTOR, "div.Tappable-inactive.availabilities-slot.availabilities-slot-desktop"
        )

        if len(week_availabilities) > 0:
            next_availability_date_raw = week_availabilities[0].get_attribute("title")

            # Parse date
            av_day_of_month = next_availability_date_raw.split(".")[1].split(" ")[1]
            av_day_of_month = int(re.sub("[^0-9]", "", av_day_of_month))  # Handle case when day is '1er' instead of '1'
            today = date.today()
            av_month = today.month if today.day <= av_day_of_month else today.month % 12 + 1
            av_year = today.year if today.month <= av_month else today.year + 1
            next_availability_date = date(year=av_year, month=av_month, day=av_day_of_month)

        # Check for next availability date
        else:
            # Extract next appointment
            next_availability_date_raw = [e[16:] for e in doctor_element.text.split("\n") if "Prochain RDV le" in e]
            if len(next_availability_date_raw) == 0:
                next_availability_date = None
            else:
                next_availability_date_elements = next_availability_date_raw[0].split(" ")

                # Parse date
                day_of_month = int(re.sub("[^0-9]", "", next_availability_date_elements[0]))
                year = int(next_availability_date_elements[2])
                month = {
                    "janvier": 1, "février": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6, "juillet": 7,
                    "août": 8, "septembre": 9, "octobre": 10, "novembre": 11, "décembre": 12,
                }.get(next_availability_date_elements[1])  # fmt: skip
                next_availability_date = date(year=year, month=month, day=day_of_month)

        return next_availability_date

    def go_next_page(self) -> None:
        """Go to next search page, return False if there is no next page"""
        next_page_available = False
        try:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            next_page_element = self.driver.find_element(
                By.XPATH,
                "//span[contains(@class, 'dl-button-label') and contains(text(), 'Suivant')]",
            )
            time.sleep(1)
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_page_element)
            time.sleep(1)
            next_page_element.click()
            next_page_available = True

        except (NoSuchElementException, ElementClickInterceptedException) as exc:
            logger.debug(f"Can't go to next page {exc.__class__.__name__}, it could be last page")

        return next_page_available

    def filter_availabilities(self) -> None:
        """Retrieve interesting doctor availabilities"""

        self.accepted_availabilities = []
        for doctor_availability in self.availabilities:
            if (
                # doctor has availability
                doctor_availability.next_availability is not None
                # availability is soon enough
                and doctor_availability.next_availability <= date.today() + timedelta(days=self.nb_days_filter)
                # doctor name is not filtered
                and not any(
                    [filter_name in doctor_availability.doctor_name for filter_name in self.filtered_doctor_names]
                )
                # doctor address is not filtered
                and not any([filter_city in doctor_availability.doctor_name for filter_city in self.filtered_cities])
            ):
                self.accepted_availabilities.append(doctor_availability)

        logger.info(
            f"{len(self.accepted_availabilities)} / {len(self.availabilities)} appointments ok: "
            f"\n{self.accepted_availabilities}"
        )

    def scrap_scenario(self) -> None:
        """Scrap doctor availability."""
        logger.info("Start scraping scenario")
        self.open_browser()
        self.handle_cookies()
        self.launch_search()
        last_page = False
        while not last_page:
            logger.debug("New page")
            self.extract_doctor_availability()
            logger.debug("Extracted")
            last_page = not self.go_next_page()
        self.filter_availabilities()
        logger.info("End scraping scenario")

    def get_accepted_availabilities_pretty(self) -> str:
        """Return a str representing accepted availabilities in a pretty format."""

        availabilities_str = "\n".join(
            [
                f"- {doctor.next_availability.strftime("%d/%m/%Y")}: {doctor.address} ({doctor.doctor_name})"
                for doctor in sorted(self.accepted_availabilities, key=lambda e: e.next_availability)
            ]
        )

        # Handle encoding issues. Could be improved to keep special characters.
        availabilities_str = availabilities_str.encode("ascii", "ignore").decode("ascii")

        return availabilities_str

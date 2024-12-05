import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
from pydantic import BaseModel, Field, computed_field


class Lawyer(BaseModel):
    """
    A class representing a lawyer's profile information.

    Attributes:
        name (str): The full name of the lawyer.
        organisation (str): The organisation the lawyer works for.
        country (str): The country the lawyer is based in.
        practice_areas (list[str]): The practice areas the lawyer specialises in.
        specific_focus (str): The specific focus of the lawyer's practice.
        bio (str): A brief biography of the lawyer.
        address_link (str): The link to the lawyer's address.
        organisation_link (str): The link to the organisation's website.
    """

    name: str = Field(title="Full Name", description="The full name of the lawyer")
    organisation: str = Field(title="Organisation", description="The organisation the lawyer works for")
    country: str = Field(title="Country", description="The country the lawyer is based in")
    practice_areas: list[str] = Field(title="Practice Areas", description="The practice areas the lawyer specialises in")
    specific_focus: str = Field(title="Specific Focus", description="The specific focus of the lawyer's practice")
    bio: str = Field(title="Biography", description="A brief biography of the lawyer")
    address_link: str = Field(title="Address", description="The address of the lawyer")
    organisation_link: str = Field(title="Organisation Link", description="The link to the organisation's website")

    @computed_field
    def address(self) -> str:
        """
        Compute the address from the address_link.

        Returns:
            str: The formatted address.
        """
        try:
            return self.address_link.split('search/')[1].replace('+', ' ').replace('%2c', ',')
        except:
            return self.address_link


# Read Countries
COUNTRIES = json.loads(open('countries.json').read())

DATABASE = pd.DataFrame(columns=Lawyer.model_fields.keys())
DATABASE.head()


def process_profile(profile_html: str, country: str) -> Lawyer:
    """
    Process a lawyer's profile HTML and extract relevant information.

    Args:
        profile_html (str): The HTML content of the lawyer's profile.
        country (str): The country code of the lawyer.

    Returns:
        Lawyer: A Lawyer object containing the extracted information.
    """
    soup = BeautifulSoup(profile_html, 'html.parser')
    return Lawyer(
        name=next((soup.find('div', class_='card-title h6 mb-0').text.strip() for _ in [None] if soup.find('div', class_='card-title h6 mb-0')), ''),
        organisation=next((soup.find('a', class_='d-block py-1 text-charcoal td-none td-underline-hover firm-profile-link fw-800').text.strip() for _ in [None] if soup.find('a', class_='d-block py-1 text-charcoal td-none td-underline-hover firm-profile-link fw-800')), ''),
        country=country,
        practice_areas=next(([area.text.strip() for area in soup.find_all('div', class_='card-text fs-10 fw-600') if area.find_previous('div', class_='card-text fs-9 fw-800').text.strip() == 'Practice Areas'] for _ in [None] if soup.find_all('div', class_='card-text fs-10 fw-600')), []),
        specific_focus=next((soup.find('div', string='Specific Focus').find_next('div', class_='card-text fs-10 fw-600').text.strip() for _ in [None] if soup.find('div', string='Specific Focus')), ''),
        bio=next((soup.find('p', class_='card-text fs-8 text-start text-truncate px-2').text.strip() for _ in [None] if soup.find('p', class_='card-text fs-8 text-start text-truncate px-2')), ''),
        address_link=next((soup.find('a', class_="background-white background-transparent-hover text-coral text-white-hover border border-1 border-transparent border-white-hover rounded-circle d-inline-flex justify-content-center align-items-center p-2 fs-7 mx-1")['href'] for _ in [None] if soup.find('a', class_="background-white background-transparent-hover text-coral text-white-hover border border-1 border-transparent border-white-hover rounded-circle d-inline-flex justify-content-center align-items-center p-2 fs-7 mx-1")), ''),
        organisation_link=next((soup.find('a', class_='d-block py-1 text-charcoal td-none td-underline-hover firm-profile-link fw-800')['href'] for _ in [None] if soup.find('a', class_='d-block py-1 text-charcoal td-none td-underline-hover firm-profile-link fw-800')), '')
    )


PROFILES = []

# Main execution loop
for country in COUNTRIES.keys():
    print(f"Harvesting profiles for {country}...")
    code = COUNTRIES[country]['code']
    response = requests.get(url=f'https://www.bestlawyers.com/findalawyer/getsearchresults?countryCode={code}&subnationalCode=&city=&practiceArea=&skip=0&take=10000')
    raw_profiles = json.loads(response.text)['cards']
    print(f"Found {len(raw_profiles)} profiles for {country}")
    for item in raw_profiles:
        profile = process_profile(item, code)
        PROFILES.append(process_profile(item, code).model_dump())
        print(f"Harvested profile for {profile.name} in {country}")

    with open('profiles.csv', 'a+') as f:
        for profile in PROFILES:
            f.write(f"{profile}\n")
    print(f"Finished harvesting profiles for {country}")

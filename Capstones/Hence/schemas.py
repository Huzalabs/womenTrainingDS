from pydantic import BaseModel, Field, computed_field


class Lawyer(BaseModel):
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
        return self.address_link.split('search/')[1].replace('+', ' ').replace('%2c', ',')

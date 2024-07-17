from pydantic import BaseModel, EmailStr, field_validator


class LoginSchema(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email", "password")
    @classmethod
    def fixer(cls, v: str) -> str:
        return v.lstrip(" ").rstrip(" ")


class SignUpSchema(BaseModel):
    email: EmailStr
    name: str
    phone: str
    password: str

    @field_validator("email", "password")
    @classmethod
    def pass_fixer(cls, v: str) -> str:
        return v.lstrip(" ").rstrip(" ")

    @field_validator("phone")
    @classmethod
    def phone_fixer(cls, v: str) -> str:
        return v.lstrip(" ").rstrip(" ").replace("-", "").replace(" ", "")

    @field_validator("name")
    @classmethod
    def name_fixer(cls, v: str) -> str:
        return (
            v.lstrip(" ")
            .rstrip(" ")
            .capitalize()
            .replace(",", "")
            .replace("_", "")
            .replace(".", "")
            .capitalize()
        )

import httpx
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from src.v1.api import token_checker

page_router = APIRouter()
client = httpx.AsyncClient()

templates = Jinja2Templates(directory="src/pages/templates")

base_dict = {
    "get_all_hotel": "/pages/hotels",
    "get_about_page": "/pages/aboutus",
    "get_contacts_page": "/pages/contacts",
    "get_login_page": "/pages/login",
    "get_registration_page": "/pages/signup",
    "get_profile_page": "/pages/profile",
}


@page_router.get("/login")
async def login(request: Request):
    return templates.TemplateResponse(
        "login.html",
        base_dict | {"request": request},
    )


@page_router.get("/logout")
async def logout(request: Request):
    return templates.TemplateResponse(
        "logout.html",
        base_dict | {"request": request},
    )


@page_router.get("/signup")
async def signup(request: Request):
    return templates.TemplateResponse(
        "signup.html",
        base_dict | {"request": request},
    )


@page_router.get("/hotels")
async def hotels(request: Request):
    token = request.session.get("auth")

    if token:
        hotels: list = (
            await client.get(
                "http://127.0.0.1:8000/api/v1/hotel/view",
                headers={"auth": request.session.get("auth")},
            )
        ).json()

        return templates.TemplateResponse(
            "hotels.html",
            base_dict
            | {
                "request": request,
                "hotels": hotels,
            },
        )

    else:
        return templates.TemplateResponse(
            "login.html",
            base_dict | {"request": request},
        )


@page_router.get("/hotel/{id}")
async def hotel(request: Request, id: int):
    token = request.session.get("auth")

    if not token:
        return templates.TemplateResponse(
            "login.html",
            base_dict | {"request": request},
        )
    
    hotel: dict = (
        await client.get(
            "http://127.0.0.1:8000/api/v1/hotel/view?hotel_id=" + str(id),
            headers={"auth": request.session.get("auth")},
        )
    ).json()

    reviews: list = (
        await client.get(
            "http://127.0.0.1:8000/api/v1/review/view?hotel_id=" + str(id),
            headers={"auth": request.session.get("auth")},
        )
    ).json()

    reviews_result = []

    for review in reviews:
        username: str = (
            await client.get(
                "http://127.0.0.1:8000/api/v1/user/view?user_id="
                + str(review["user_id"]),
                headers={"auth": token},
            )
        ).json()

        review["client_name"] = username

        reviews_result.append(review)

    return templates.TemplateResponse(
        "hotel.html",
        base_dict
        | {
            "request": request,
            "name": hotel.get("name"),
            "location": hotel.get("location"),
            "stars": hotel.get("stars"),
            "description": hotel.get("description"),
            "price": hotel.get("price"),
            "hotel_id": hotel.get("id"),
            "hotel_photo": hotel.get("photo"),
            "reviews": reviews_result,
        },
    )


@page_router.get("/contacts")
async def contacts(request: Request):
    return templates.TemplateResponse(
        "contacts.html",
        base_dict | {"request": request},
    )


@page_router.get("/aboutus")
async def aboutus(request: Request):
    return templates.TemplateResponse(
        "aboutus.html",
        base_dict | {"request": request},
    )


@page_router.get("/profile")
async def profile(request: Request):
    token = request.session.get("auth")

    # check: dict = (
    #     await client.get(
    #         "http://127.0.0.1:8000/api/v1/check_token",
    #         headers={"auth": token},
    #     )
    # ).json()

    if token:
        user: dict = (
            await client.get(
                "http://127.0.0.1:8000/api/v1/user/view",
                headers={"auth": token},
            )
        ).json()

        bookings = []
        reviews = []
        
        try:
            for booking in user["bookings"]:
                hotel: dict = (
                    await client.get(
                        "http://127.0.0.1:8000/api/v1/hotel/view?hotel_id="
                        + str(booking["hotel_id"]),
                        headers={"auth": token},
                    )
                ).json()

                booking["hotel_name"] = hotel.get("name")
                booking["sum"] = hotel.get("price")

                bookings.append(booking)

            for review in user["reviews"]:
                hotel: dict = (
                    await client.get(
                        "http://127.0.0.1:8000/api/v1/hotel/view?hotel_id="
                        + str(review["hotel_id"]),
                        headers={"auth": token},
                    )
                ).json()

                review["hotel_name"] = hotel.get("name")

                reviews.append(review)
        
        except:
            pass

        return templates.TemplateResponse(
            "profile.html",
            base_dict
            | {
                "request": request,
                "username": user.get("name"),
                "email": user.get("email"),
                "bookings": bookings,
                "reviews": reviews,
            },
        )

    else:
        return templates.TemplateResponse(
            "login.html",
            base_dict | {"request": request},
        )

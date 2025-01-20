import random
from fastapi import FastAPI, HTTPException, Body, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Optional

app = FastAPI()


class UserData(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    avatar: str


class SupportData(BaseModel):
    url: str
    text: str


class ResponseModel(BaseModel):
    data: UserData
    support: SupportData


class User(BaseModel):
    email: str
    password: str


class UserUpdate(BaseModel):
    job: str
    name: str


# Моковые данные для демонстрации
mock_users = {
    2: {
        "id": 2,
        "email": "janet.weaver@reqres.in",
        "first_name": "Janet",
        "last_name": "Weaver",
        "avatar": "https://reqres.in/img/faces/2-image.jpg",
    }
}
mock_registered_users = {"eve.holt@reqres.in": ""}


def validate_user_data(user: User):
    if not user.email or user.email == "":
        raise HTTPException(status_code=400, detail="Missing email or username")
    if not user.password or user.password == "":
        raise HTTPException(status_code=400, detail="Missing password")


def get_current_time():
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:-3]


@app.get("/api/users/{user_id}", response_model=Optional[ResponseModel])
def get_user(user_id: int):
    user = mock_users.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Пример данных поддержки (может быть изменено в зависимости от реальных данных)
    support_data = SupportData(url="http://example.com", text="Support text")

    response_data = ResponseModel(
        data=UserData(**user),
        support=support_data
    )
    return response_data


@app.post("/api/register")
def register_user(user: User = Body()):
    if (not user.email or user.email == "") and (not user.password or user.password == ""):
        return Response(status_code=400, media_type="application/json",
                        content='{"error": "Missing email or username"}')
    if not user.email or user.email == "":
        return Response(status_code=400, media_type="application/json",
                        content='{"error": "Missing email or username"}')
    if not user.password or user.password == "":
        return Response(status_code=400, media_type="application/json",
                        content='{"error": "Missing password"}')

    # Проверка на существование зарегистрированного пользователя
    elif user.email in mock_registered_users:
        return {
            "id": 4,
            "token": "QpwL5tke4Pnpja7X4"
        }
    else:
        return Response(status_code=400, media_type="application/json",
                        content='{"error": "Note: Only defined users succeed registration"}')


@app.post("/api/login")
def login_user(user: User = Body()):
    if (not user.email or user.email == "") and (not user.password or user.password == ""):
        return Response(status_code=400, media_type="application/json",
                        content='{"error": "Missing email or username"}')
    if not user.email or user.email == "":
        return Response(status_code=400, media_type="application/json",
                        content='{"error": "Missing email or username"}')
    if not user.password or user.password == "":
        return Response(status_code=400, media_type="application/json", content='{"error": "Missing password"}')

    elif user.email in mock_registered_users:
        return {
            "token": "QpwL5tke4Pnpja7X4"
        }
    else:
        return Response(status_code=400, media_type="application/json", content='{"error": "user not found"}')


@app.put("/api/users/{user_id}")
def put_user(user: UserUpdate = Body()):
    current_time = get_current_time()
    return {
        "job": user.job,
        "name": user.name,
        "updatedAt": current_time
    }


@app.post("/api/users")
def create_user(user: UserUpdate = Body()):
    current_time = get_current_time()
    content = {
        "job": user.job,
        "name": user.name,
        "id": random.randint(1, 999),
        "updatedAt": current_time
    }
    return JSONResponse(status_code=201, media_type="application/json", content=content)


@app.patch("/api/users/{user_id}")
def patch_user(user: UserUpdate = Body()):
    current_time = get_current_time()
    return {
        "job": user.job,
        "name": user.name,
        "updatedAt": current_time
    }


@app.delete("/api/users/{user_id}")
def delete_user():
    return Response(status_code=204)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

import json
from typing import Dict, Any
import pytest
import requests
import random
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Константы для URL и других настроек
TEST = "http://127.0.0.1:8000"
PROD = "https://reqres.in"
NAME_USERS = ["Ivan", "Petr", "Jon"]
JOB_USERS = ["QA_Jun", "QA_Mid", "QA_Sen"]


# Вспомогательная функция для отправки запросов и проверки ответа
def send_request(method: str, endpoint: str, payload: Dict[str, Any] = None, headers: Dict[str, str] = None,
                 base_url: str = PROD):
    url = f"{base_url}{endpoint}"
    try:
        if method == 'GET':
            response = requests.get(url)
        elif method == 'POST':
            response = requests.post(url, data=json.dumps(payload),
                                     headers=headers or {"Content-Type": "application/json"})
        elif method == 'PUT':
            response = requests.put(url, data=json.dumps(payload),
                                    headers=headers or {"Content-Type": "application/json"})
        elif method == 'PATCH':
            response = requests.patch(url, data=json.dumps(payload),
                                      headers=headers or {"Content-Type": "application/json"})
        elif method == 'DELETE':
            response = requests.delete(url)
        else:
            raise ValueError(f"Неподдерживаемый HTTP метод: {method}")
        logger.info(f"Отправлен запрос {method} к {url}, получен статус код {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Ошибка при отправке запроса {method} к {url}: {e}")
        raise


# Вспомогательная функция для проверки статуса и содержимого ответа
def check_response(response, expected_status_code: int, expected_body: Dict[str, Any] = None):
    try:
        assert response.status_code == expected_status_code, (
            f"Ожидается статус код {expected_status_code}, но получен {response.status_code}. "
            f"Тело ответа: {response.text}"
        )
        if expected_body is not None:
            body = response.json()
            for key, value in expected_body.items():
                assert body.get(key) == value, f"Ожидается {key} равен {value}, но получен {body.get(key)}"
        logger.info(f"Проверка ответа пройдена для статус кода {expected_status_code}")
    except AssertionError as e:
        logger.error(f"Проверка ответа не пройдена: {e}")
        raise


# Фикстура для случайного выбора имени и должности пользователя
@pytest.fixture(params=[(name, job) for name in NAME_USERS for job in JOB_USERS])
def user_data(request):
    return request.param


# Фикстура для случайного выбора ID пользователя
@pytest.fixture(params=[str(random.randint(1, 100)) for _ in range(5)])
def user_id(request):
    return request.param


# Фикстура для параметризации базового URL
@pytest.fixture(params=[PROD, TEST], ids=["prod", "test"])
def base_url(request):
    return request.param


class TestUser:
    @pytest.mark.parametrize("user_id, expected_email", [
        (2, "janet.weaver@reqres.in"),
    ])
    def test_user_data_successful(self, user_id, expected_email, base_url):
        endpoint = f"/api/users/{user_id}"
        response = send_request('GET', endpoint, base_url=base_url)
        check_response(response, 200)
        body = response.json()
        assert "data" in body, "Тело ответа не содержит ключ 'data'"
        data = body["data"]
        assert data["id"] == user_id, f"Ожидается id {user_id}, но получен {data['id']}"
        assert data["email"] == expected_email, f"Ожидается email {expected_email}, но получен {data['email']}"

    @pytest.mark.parametrize("user_id", [pytest.param(random.randint(10000, 30000), id=f"user_{i}") for i in range(3)])
    def test_user_data_unsuccessful(self, user_id, base_url):
        endpoint = f"/api/users/{user_id}"
        response = send_request('GET', endpoint, base_url=base_url)
        check_response(response, 404)


class TestRegister:
    @pytest.mark.parametrize("email, expected_id, expected_token", [("eve.holt@reqres.in", 4, "QpwL5tke4Pnpja7X4")])
    def test_user_register_successful(self, email, expected_id, expected_token, base_url):
        endpoint = "/api/register"
        body = {
            "email": email,
            "password": "pistol"
        }
        response = send_request('POST', endpoint, body, base_url=base_url)
        check_response(response, 200, {"id": expected_id, "token": expected_token})

    @pytest.mark.parametrize("email, password, expected_message", [
        ("eve.holt@reqres.in", "", "Missing password"),
        ("", "pistol", "Missing email or username"),
        ("", "", "Missing email or username"),
        ("blablauser", "pistol", "Note: Only defined users succeed registration")
    ])
    def test_register_unsuccessful(self, email, password, expected_message, base_url):
        endpoint = "/api/register"
        body = {
            "email": email,
            "password": password
        }
        response = send_request('POST', endpoint, body, base_url=base_url)
        check_response(response, 400)
        data = response.json()
        print(data)
        assert data[
                   "error"] == expected_message, f"Ожидается сообщение {expected_message}, но получено {data['detail']}"


class TestLoginUser:
    @pytest.mark.parametrize("email, password, expected_token",
                             [("eve.holt@reqres.in", "cityslicka", "QpwL5tke4Pnpja7X4")])
    def tests_login_successful(self, email, password, expected_token, base_url):
        endpoint = "/api/login"
        body = {
            "email": email,
            "password": password
        }
        response = send_request('POST', endpoint, body, base_url=base_url)
        check_response(response, 200, {"token": expected_token})

    @pytest.mark.parametrize("email, password, expected_message", [
        ("eve.holt@reqres.in", "", "Missing password"),
        ("", "pistol", "Missing email or username"),
        ("", "", "Missing email or username"),
        ("blablauser", "pistol", "user not found")
    ])
    def test_login_unsuccessful(self, email, password, expected_message, base_url):
        endpoint = "/api/login"
        body = {
            "email": email,
            "password": password
        }
        response = send_request('POST', endpoint, body, base_url=base_url)
        check_response(response, 400)
        data = response.json()
        assert data[
                   "error"] == expected_message, f"Ожидается сообщение {expected_message}, но получено {data['detail']}"


class TestCrudUser:
    def test_create_user_successful(self, user_data, base_url):
        name, job = user_data
        endpoint = "/api/users"
        body = {
            "name": name,
            "job": job
        }
        response = send_request('POST', endpoint, body, base_url=base_url)
        check_response(response, 201)
        data = response.json()
        assert data["job"] == job, f"Ожидается job {job}, но получен {data['job']}"
        assert data["name"] == name, f"Ожидается name {name}, но получен {data['name']}"

    def test_put_user_successful(self, user_data, user_id, base_url):
        name, job = user_data
        endpoint = f"/api/users/{user_id}"
        body = {
            "name": name,
            "job": job
        }
        response = send_request('PUT', endpoint, body, base_url=base_url)
        check_response(response, 200)
        data = response.json()
        assert data["job"] == job, f"Ожидается job {job}, но получен {data['job']}"
        assert data["name"] == name, f"Ожидается name {name}, но получен {data['name']}"

    def test_patch_user_successful(self, user_data, user_id, base_url):
        name, job = user_data
        endpoint = f"/api/users/{user_id}"
        body = {
            "name": name,
            "job": job
        }
        response = send_request('PATCH', endpoint, body, base_url=base_url)
        check_response(response, 200)
        data = response.json()
        assert data["job"] == job, f"Ожидается job {job}, но получен {data['job']}"
        assert data["name"] == name, f"Ожидается name {name}, но получен {data['name']}"

    def test_delete_user_successful(self, user_id, base_url):
        endpoint = f"/api/users/{user_id}"
        response = send_request('DELETE', endpoint, base_url=base_url)
        check_response(response, 204)

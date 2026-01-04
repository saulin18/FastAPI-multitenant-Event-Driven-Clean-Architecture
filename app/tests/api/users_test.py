from uuid import uuid4
import pytest
from fastapi import status
from httpx import AsyncClient


class TestCreateUsers:
    url = "/users/"

    @pytest.mark.asyncio
    async def test_create_user_sucess(self, client: AsyncClient):
        response = await client.post(
            url=self.url,
            json={
                "email": "test@test.com",
                "username": "test",
                "password": "test",
                "full_name": "test",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == "test@test.com"
        assert data["username"] == "test"
        assert data["full_name"] == "test"
        assert "id" in data
        assert data["is_active"] is True

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, client: AsyncClient):
        response1 = await client.post(
            url=self.url,
            json={
                "email": "duplicate@test.com",
                "username": "user1",
                "password": "test",
                "full_name": "test",
            },
        )
        assert response1.status_code == status.HTTP_201_CREATED

        # Intentamos crear otro usuario con el mismo email
        response2 = await client.post(
            url=self.url,
            json={
                "email": "duplicate@test.com",  # Email duplicado
                "username": "user2",
                "password": "test",
                "full_name": "test",
            },
        )
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response2.json()["detail"].lower()


class TestUpdateDeleteUsers:
    url = "/users/{user_id}"

    @pytest.mark.asyncio
    async def test_update_user_sucess(self, client: AsyncClient, create_user):
        response = await client.put(
            url=self.url.format(user_id=create_user.id),
            json={
                "email": "updated@test.com",
                "username": "updated_user",
                "full_name": "Updated Name",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "updated@test.com"
        assert data["username"] == "updated_user"
        assert data["full_name"] == "Updated Name"
        assert data["id"] == str(create_user.id)

    @pytest.mark.asyncio
    async def test_update_user_invalid_user_id(self, client: AsyncClient):
        # Usar un UUID válido que no existe
        non_existent_id = uuid4()
        response = await client.put(
            url=self.url.format(user_id=non_existent_id),
            json={
                "email": "test@test.com",
                "username": "test",
                "full_name": "test",
            },
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_update_user_invalid_uuid_format(self, client: AsyncClient):
        # Test para formato UUID inválido (debería dar 422)
        response = await client.put(
            url=self.url.format(user_id="invalid"),
            json={
                "email": "test@test.com",
                "username": "test",
                "full_name": "test",
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

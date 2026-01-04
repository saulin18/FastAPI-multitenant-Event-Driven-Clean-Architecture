from httpx import AsyncClient
import pytest
from fastapi import status

from app.application.dtos.tenant_dtos import CursorPagedTenantResponse


class TestListCreateTenants:
    url = "/tenants/"

    @pytest.mark.asyncio
    async def test_list_tenants(self, client: AsyncClient):
        response = await client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == dict(
            CursorPagedTenantResponse(
                items=[],
                next_cursor=None,
                previous_cursor=None,
                has_next_page=False,
                has_previous_page=False,
                page_size=10,
            )
        )

    @pytest.mark.asyncio
    async def test_create_tenant(self, client: AsyncClient):
        response = await client.post(
            self.url, json={"name": "test", "domain": "test.com"}
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["name"] == "test"
        assert response.json()["domain"] == "test.com"

    @pytest.mark.asyncio
    async def test_create_tenant_duplicate_domain(self, client: AsyncClient):
        response1 = await client.post(
            self.url, json={"name": "test", "domain": "test.com"}
        )
        assert response1.status_code == status.HTTP_201_CREATED
        response2 = await client.post(
            self.url, json={"name": "test", "domain": "test.com"}
        )
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response2.json()["detail"].lower()


class TestGetUpdateDeleteTenants:
    url = "/tenants/{tenant_id}"

    @pytest.mark.asyncio
    async def test_get_tenant(self, client: AsyncClient, create_tenant):
        response = await client.get(self.url.format(tenant_id=create_tenant.id))
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["name"] == "test"
        assert response.json()["domain"] == "test.com"

    @pytest.mark.asyncio
    async def test_update_tenant(self, client: AsyncClient, create_tenant):
        response = await client.put(
            self.url.format(tenant_id=create_tenant.id),
            json={"name": "test2", "domain": "test2.com"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["name"] == "test2"
        assert response.json()["domain"] == "test2.com"

    @pytest.mark.asyncio
    async def test_delete_tenant(self, client: AsyncClient, create_tenant):
        response = await client.delete(self.url.format(tenant_id=create_tenant.id))
        assert response.status_code == status.HTTP_204_NO_CONTENT

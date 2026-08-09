import uuid


async def _make_lead(client, email="lead@example.com", source=None):
    r = await client.post("/leads/create", json={"email": email, "source": source})
    return r.json()["id"]


async def test_create_lead_persists_a_real_row(client):
    r = await client.post("/leads/create", json={
        "email": "new@example.com", "name": "Jordan Lee", "source": "funnel",
    })
    assert r.status_code == 200
    body = r.json()
    assert body["email"] == "new@example.com"
    assert body["status"] == "new"

    fetched = await client.get(f"/leads/{body['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["email"] == "new@example.com"


async def test_get_nonexistent_lead_returns_404(client):
    r = await client.get(f"/leads/{uuid.uuid4()}")
    assert r.status_code == 404


async def test_list_leads_filters_by_source(client):
    await _make_lead(client, email="a@example.com", source="funnel")
    await _make_lead(client, email="b@example.com", source="social")

    r = await client.get("/leads/", params={"source": "funnel"})
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 1
    assert body["leads"][0]["email"] == "a@example.com"

import uuid


async def _make_campaign(client, name="Welcome Series", campaign_type="email"):
    r = await client.post("/campaigns/create", json={"name": name, "campaign_type": campaign_type})
    return r.json()["id"]


async def test_create_campaign_persists_a_real_row(client):
    r = await client.post("/campaigns/create", json={
        "name": "Welcome Series", "campaign_type": "email", "budget": 5000,
    })
    assert r.status_code == 200
    body = r.json()
    assert body["name"] == "Welcome Series"
    assert body["status"] == "draft"
    assert body["budget"] == 5000

    fetched = await client.get(f"/campaigns/{body['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "Welcome Series"


async def test_get_nonexistent_campaign_returns_404(client):
    r = await client.get(f"/campaigns/{uuid.uuid4()}")
    assert r.status_code == 404


async def test_list_campaigns_filters_by_type(client):
    await _make_campaign(client, name="Email Blast", campaign_type="email")
    await _make_campaign(client, name="Social Push", campaign_type="social")

    r = await client.get("/campaigns/", params={"campaign_type": "email"})
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 1
    assert body["campaigns"][0]["name"] == "Email Blast"

import uuid

import httpx
import respx


async def _make_campaign(client):
    r = await client.post("/campaigns/create", json={"name": "Welcome Series", "campaign_type": "email"})
    return r.json()["id"]


async def _make_lead(client, email):
    await client.post("/leads/create", json={"email": email})


async def _make_email_campaign(client, campaign_id, **overrides):
    payload = {
        "campaign_id": campaign_id,
        "subject": "Welcome!",
        "from_email": "hello@company.com",
        "html_content": "<p>Hi there</p>",
        **overrides,
    }
    r = await client.post("/email/create", json=payload)
    return r.json()["id"]


async def test_create_email_campaign_persists_a_real_row(client):
    campaign_id = await _make_campaign(client)

    r = await client.post("/email/create", json={
        "campaign_id": campaign_id, "subject": "Welcome!", "from_email": "hello@company.com",
    })

    assert r.status_code == 200
    body = r.json()
    assert body["subject"] == "Welcome!"
    assert body["campaign_id"] == campaign_id


async def test_create_email_campaign_for_nonexistent_campaign_returns_404(client):
    r = await client.post("/email/create", json={
        "campaign_id": str(uuid.uuid4()), "subject": "Welcome!", "from_email": "hello@company.com",
    })
    assert r.status_code == 404


async def test_send_without_sendgrid_configured_reports_honest_failure(client):
    # conftest leaves SENDGRID_API_KEY unset by default
    campaign_id = await _make_campaign(client)
    email_campaign_id = await _make_email_campaign(client, campaign_id)

    r = await client.post(f"/email/{email_campaign_id}/send", json={"recipient_emails": ["a@example.com"]})

    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "failed"
    assert "not configured" in body["error"]
    assert body["delivered"] == 0


async def test_send_nonexistent_email_campaign_returns_404(client):
    r = await client.post(f"/email/{uuid.uuid4()}/send", json={"recipient_emails": ["a@example.com"]})
    assert r.status_code == 404


@respx.mock
async def test_send_with_explicit_recipients_calls_sendgrid_for_each(client, monkeypatch):
    monkeypatch.setenv("SENDGRID_API_KEY", "test_key")
    import app.config as config_module
    monkeypatch.setattr(config_module.settings, "sendgrid_api_key", "test_key")

    route = respx.post("https://api.sendgrid.com/v3/mail/send").mock(
        return_value=httpx.Response(202)
    )

    campaign_id = await _make_campaign(client)
    email_campaign_id = await _make_email_campaign(client, campaign_id)

    r = await client.post(f"/email/{email_campaign_id}/send", json={
        "recipient_emails": ["a@example.com", "b@example.com"]
    })

    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "sent"
    assert body["recipients"] == 2
    assert body["delivered"] == 2
    assert route.call_count == 2

    request = route.calls[0].request
    assert request.headers["Authorization"] == "Bearer test_key"


@respx.mock
async def test_send_falls_back_to_all_leads_when_no_recipients_given(client, monkeypatch):
    monkeypatch.setenv("SENDGRID_API_KEY", "test_key")
    import app.config as config_module
    monkeypatch.setattr(config_module.settings, "sendgrid_api_key", "test_key")

    respx.post("https://api.sendgrid.com/v3/mail/send").mock(return_value=httpx.Response(202))

    await _make_lead(client, "lead1@example.com")
    await _make_lead(client, "lead2@example.com")
    await _make_lead(client, "lead3@example.com")

    campaign_id = await _make_campaign(client)
    email_campaign_id = await _make_email_campaign(client, campaign_id)

    r = await client.post(f"/email/{email_campaign_id}/send", json={})

    assert r.status_code == 200
    assert r.json()["recipients"] == 3


@respx.mock
async def test_send_reports_partial_failure_honestly(client, monkeypatch):
    monkeypatch.setenv("SENDGRID_API_KEY", "test_key")
    import app.config as config_module
    monkeypatch.setattr(config_module.settings, "sendgrid_api_key", "test_key")

    respx.post("https://api.sendgrid.com/v3/mail/send").mock(
        side_effect=[httpx.Response(202), httpx.Response(400, text="bad request")]
    )

    campaign_id = await _make_campaign(client)
    email_campaign_id = await _make_email_campaign(client, campaign_id)

    r = await client.post(f"/email/{email_campaign_id}/send", json={
        "recipient_emails": ["good@example.com", "bad@example.com"]
    })

    assert r.status_code == 200
    body = r.json()
    assert body["delivered"] == 1
    assert body["bounced"] == 1
    assert "error" in body

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


def _variant_payload():
    return [
        {"name": "a", "subject": "Save 10% today", "html_content": "<p>A</p>"},
        {"name": "b", "subject": "Your discount is waiting", "html_content": "<p>B</p>"},
    ]


async def test_create_email_campaign_with_variants_persists_them(client):
    campaign_id = await _make_campaign(client)

    r = await client.post("/email/create", json={
        "campaign_id": campaign_id, "subject": "Welcome!", "from_email": "hello@company.com",
        "variants": _variant_payload(),
    })

    assert r.status_code == 200
    body = r.json()
    assert len(body["variants"]) == 2
    names = {v["name"] for v in body["variants"]}
    assert names == {"a", "b"}


async def test_create_email_campaign_rejects_a_single_variant(client):
    campaign_id = await _make_campaign(client)

    r = await client.post("/email/create", json={
        "campaign_id": campaign_id, "subject": "Welcome!", "from_email": "hello@company.com",
        "variants": [{"name": "a", "subject": "Only one"}],
    })

    assert r.status_code == 400


@respx.mock
async def test_send_with_variants_splits_recipients_and_tracks_per_variant_counts(client, monkeypatch):
    monkeypatch.setenv("SENDGRID_API_KEY", "test_key")
    import app.config as config_module
    monkeypatch.setattr(config_module.settings, "sendgrid_api_key", "test_key")

    respx.post("https://api.sendgrid.com/v3/mail/send").mock(return_value=httpx.Response(202))

    campaign_id = await _make_campaign(client)
    email_campaign_id = await _make_email_campaign(client, campaign_id, variants=_variant_payload())

    recipients = [f"user{i}@example.com" for i in range(40)]
    r = await client.post(f"/email/{email_campaign_id}/send", json={"recipient_emails": recipients})

    assert r.status_code == 200
    body = r.json()
    assert body["ab_test"] is True
    assert body["recipients"] == 40
    assert body["delivered"] == 40

    results = await client.get(f"/email/{email_campaign_id}/ab-results")
    assert results.status_code == 200
    result_body = results.json()
    assert set(result_body["variants"].keys()) == {"a", "b"}
    # Every recipient landed in exactly one variant bucket - the total across
    # both variants must equal what was actually sent.
    total_sent = sum(v["sent"] for v in result_body["variants"].values())
    assert total_sent == 40
    assert result_body["error"] is None


async def test_ab_results_without_two_variants_returns_400(client):
    campaign_id = await _make_campaign(client)
    email_campaign_id = await _make_email_campaign(client, campaign_id)

    r = await client.get(f"/email/{email_campaign_id}/ab-results")

    assert r.status_code == 400


async def test_ab_results_for_nonexistent_campaign_returns_404(client):
    r = await client.get(f"/email/{uuid.uuid4()}/ab-results")
    assert r.status_code == 404


@respx.mock
async def test_send_without_variants_is_not_flagged_as_ab_test(client, monkeypatch):
    monkeypatch.setenv("SENDGRID_API_KEY", "test_key")
    import app.config as config_module
    monkeypatch.setattr(config_module.settings, "sendgrid_api_key", "test_key")

    respx.post("https://api.sendgrid.com/v3/mail/send").mock(return_value=httpx.Response(202))

    campaign_id = await _make_campaign(client)
    email_campaign_id = await _make_email_campaign(client, campaign_id)

    r = await client.post(f"/email/{email_campaign_id}/send", json={"recipient_emails": ["a@example.com"]})

    assert r.status_code == 200
    assert r.json()["ab_test"] is False

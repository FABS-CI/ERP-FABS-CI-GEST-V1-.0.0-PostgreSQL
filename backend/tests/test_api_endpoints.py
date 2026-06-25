import pytest
import httpx

BASE_URL = "http://localhost:8005/api"

def test_health():
    response = httpx.get("http://localhost:8005/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"

def test_users_list():
    response = httpx.get(f"{BASE_URL}/users")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data

def test_clients_list():
    response = httpx.get(f"{BASE_URL}/clients")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data

def test_products_list():
    response = httpx.get(f"{BASE_URL}/products")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data

def test_orders_list():
    response = httpx.get(f"{BASE_URL}/orders")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data

def test_invoices_list():
    response = httpx.get(f"{BASE_URL}/invoices")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data

def test_create_order():
    # Récupérer client_id
    clients_resp = httpx.get(f"{BASE_URL}/clients")
    clients = clients_resp.json()["items"]
    
    if clients:
        client_id = clients[0]["id"]
        response = httpx.post(f"{BASE_URL}/orders", json={
            "numero_commande": "TEST-ORDER-FINAL",
            "client_id": client_id,
            "montant_ht": 500.0,
            "montant_tva": 90.0,
            "montant_ttc": 590.0,
        })
        assert response.status_code == 201
        data = response.json()
        assert "id" in data

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

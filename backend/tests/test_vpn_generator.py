from app.services.vpn_service import _build_client_config, _generate_password, _generate_username
from app.services.wireguard_keygen import generate_keypair


def test_wireguard_keypair_is_base64_and_unique():
    priv1, pub1 = generate_keypair()
    priv2, pub2 = generate_keypair()
    assert priv1 != priv2
    assert pub1 != pub2
    assert len(priv1) > 0 and len(pub1) > 0


def test_build_client_config_contains_expected_sections():
    config = _build_client_config(
        client_private_key="CLIENTPRIVKEY",
        allowed_ip="10.10.10.5/32",
        dns="1.1.1.1",
        router_public_key="ROUTERPUBKEY",
        endpoint="vpn.example.com:13231",
    )
    assert "[Interface]" in config
    assert "PrivateKey = CLIENTPRIVKEY" in config
    assert "Address = 10.10.10.5/32" in config
    assert "[Peer]" in config
    assert "PublicKey = ROUTERPUBKEY" in config
    assert "Endpoint = vpn.example.com:13231" in config


def test_generate_username_format_and_uniqueness():
    names = {_generate_username() for _ in range(20)}
    assert len(names) == 20
    for name in names:
        assert name.startswith("vpn-")
        assert len(name) == len("vpn-") + 6


def test_generate_password_is_random_and_reasonably_long():
    passwords = {_generate_password() for _ in range(20)}
    assert len(passwords) == 20
    for pw in passwords:
        assert len(pw) == 14

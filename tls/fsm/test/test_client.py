# This file is dual licensed under the terms of the Apache License, Version
# 2.0, and the BSD License. See the LICENSE file in the root of this repository
# for complete details.

from __future__ import absolute_import, division, print_function

from ..client import TLSClient

import pytest


class TestTLSClientAnonymousKeyExchangeHandshake(object):
    """
    :py:class:`TLSClient` models a handshake using anonymous key
    exchange.  (RFC 5246 sections 7.3 and F.1.1.1)
    """

    @pytest.fixture
    def tls_client(self):
        """
        A :py:class:`TLSClient` instance for use in tests.
        """
        return TLSClient()

    def test_end_to_end(self, tls_client):
        """
        A handshake progresses by sending a ClientHello, receiving a
        ServerHello, a ServerKeyExchange, and then a ServerHelloDone,
        then sending a ChangeCipherSpec and Finished.
        """
        assert tls_client.connection_established() == []
        assert tls_client.send_client_hello() == ["ClientHello"]
        assert tls_client.received_server_hello() == ["processed ServerHello"]
        assert tls_client.received_server_key_exchange() == [
            "processed ServerKeyExchange",
        ]
        assert tls_client.received_server_hello_done() == []
        assert tls_client.send_client_key_exchange() == ["ClientKeyExchange"]
        assert tls_client.send_change_cipher_spec() == [
            "ChangeCipherSpec",
            "cipher spec set",
        ]
        assert tls_client.send_finished() == ["Finished"]

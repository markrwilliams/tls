from automat import MethodicalMachine


class TLSClient(object):
    """
    Implementing the TLS client as a finite state machine.  The state table for
    this is documented:
        https://github.com/pyca/tls/blob/master/docs/_notes/tls-handshake.rst#client-as-a-state-machine

    XXX: Some things to pay attention to when reviewing this:
        1. Naming of inputs, outputs, and states -- can they be improved? Do
        tell!
        2. There are some common states for both the client and server state
        machines:
            https://github.com/pyca/tls/blob/master/docs/_notes/tls-handshake.rst#common-states-for-both-state-machines.
            Can we organize this in a DRY-er way, without subclassing?
    """
    _machine = MethodicalMachine()

    @_machine.state(initial=True)
    def no_connection(self):
        """
        The intial state, before a connection is established.
        """

    @_machine.input()
    def connection_established(self):
        """
        A TCP connection has been established.
        """

    @_machine.state()
    def want_to_send_client_hello(self):
        """
        A ClientHello has been sent over the TCP connection.
        """

    @_machine.output()
    def _emit_client_hello(self):
        return "ClientHello"

    @_machine.input()
    def send_client_hello(self):
        """
        Send a ClientHello over the TCP connection.
        """

    @_machine.state()
    def waiting_for_server_hello(self):
        """
        Waiting for a ServerHello in respons to a ClientHello.
        """

    @_machine.state()
    def dead(self):
        """
        An error occurred, dead state, etc.
        """

    @_machine.input()
    def server_hello_wait_expired(self):
        """
        We can't wait for a ServerHello any longer.
        """

    @_machine.output()
    def _cleanup_after_expired_client_hello(self):
        """
        Clean up after expired ClientHello
        """
        return "cleaned up client hello"

    @_machine.input()
    def received_server_hello(self):
        """
        We got a ServerHello
        """

    @_machine.state()
    def waiting_for_server_hello_done(self):
        """
        We got a ServerHello and now we're waiting for a ServerHelloDone.
        """

    @_machine.output()
    def _process_server_hello(self):
        """
        Actually act on ServerHello
        """
        return "processed ServerHello"

    @_machine.state()
    def received_server_hello_done(self):
        """
        Received a ServerHelloDone.
        """

    @_machine.input()
    def server_hello_done_wait_expired(self):
        """
        We can't wait for a ServerHelloDone any longer.
        """

    @_machine.output()
    def _cleanup_after_expired_server_hello_done(self):
        """
        Clean up after we've timed out waiting for ServerHelloDone.
        """
        return "cleaned up after ServerHelloDone"

    @_machine.input()
    def received_server_hello_done(self):
        """
        We got a ServerHelloDone
        """
        return "processed ServerHelloDone"

    @_machine.state()
    def want_to_send_client_key_exchange(self):
        """
        We want to send a ClientKeyExchange
        """

    @_machine.input()
    def send_client_key_exchange(self):
        """
        Send a client key exchange.
        """

    @_machine.output()
    def _emit_client_key_exhange(self):
        """
        Emit a ClientKeyExchange message
        """
        return "ClientKeyExchange"

    @_machine.state()
    def want_to_send_change_cipher_spec(self):
        """
        We want to send a ChangeCipherSpec.
        """

    @_machine.input()
    def send_change_cipher_spec(self):
        """
        Send the ChangeCipherSpec message.
        """

    @_machine.output()
    def _emit_change_cipher_spec(self):
        """
        Emit the ChangeCipherSpec message.
        """
        return "ChangeCipherSpec"

    @_machine.output()
    def _set_cipher_spec(self):
        """
        Set the desired cipher specification.
        """
        return "cipher spec set"

    @_machine.state()
    def want_to_finish(self):
        """
        We want to send the Finished message.
        """

    @_machine.input()
    def send_finished(self):
        """
        Send a Finished message.
        """

    @_machine.output()
    def _emit_finished(self):
        """
        Emit a finished message.
        """
        return "Finished"

    @_machine.state()
    def finished(self):
        """
        The handshake is finished.
        """

    no_connection.upon(connection_established,
                       enter=want_to_send_client_hello,
                       outputs=[])
    want_to_send_client_hello.upon(send_client_hello,
                                   enter=waiting_for_server_hello,
                                   outputs=[_emit_client_hello])

    waiting_for_server_hello.upon(received_server_hello,
                                  enter=waiting_for_server_hello_done,
                                  outputs=[_process_server_hello])

    waiting_for_server_hello.upon(server_hello_wait_expired,
                                  enter=dead,
                                  outputs=[_cleanup_after_expired_client_hello])

    waiting_for_server_hello_done.upon(received_server_hello_done,
                                       enter=want_to_send_client_key_exchange,
                                       outputs=[])

    waiting_for_server_hello_done.upon(
        server_hello_done_wait_expired,
        enter=dead,
        outputs=[_cleanup_after_expired_server_hello_done])

    want_to_send_client_key_exchange.upon(
        send_client_key_exchange,
        enter=want_to_send_change_cipher_spec,
        outputs=[_emit_client_key_exhange],
    )

    want_to_send_change_cipher_spec.upon(
        send_change_cipher_spec,
        enter=want_to_finish,
        outputs=[_emit_change_cipher_spec, _set_cipher_spec],
    )

    want_to_finish.upon(
        send_finished,
        enter=finished,
        outputs=[_emit_finished],
    )

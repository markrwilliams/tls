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

    @_machine.input()
    def receive_finished(self):
        """
        The client received a Finished message from the server.
        """

    @_machine.input()
    def receive_hello_request(self):
        """
        The client received a HelloRequest from the server.
        """

    @_machine.input()
    def receive_server_hello_done(self):
        """
        The client received a ServerHelloDone message.
        """

    @_machine.input()
    def receive_tls_alert_close_notify(self):
        """
        The client received an Alert(close_notify) message from the server.
        """

    @_machine.input()
    def receive_session_alert_close_notify(self):
        """
        The client received Session.alert(close_notify)
        TODO: [send an Alert(close_notify) to tell the server you would like to
        stop].
        """

    @_machine.input()
    def receive_session_write_data(self):
        """
        TODO: The client received Session.write_data with the app data.
        """

    @_machine.output()
    def _send_client_hello(self):
        """
        Send the server a The clientHello message.
        """

    @_machine.output()
    def _send_certificate(self):
        """
        Send the server a Certificate message.
        """

    @_machine.output()
    def _send_client_key_exchange(self):
        """
        Send the server a The ClientKeyExchange message.
        """

    @_machine.output()
    def _send_certificate_verify(self):
        """
        Send the server a CertificateVerify message.
        """

    @_machine.output()
    def _send_change_cipher_spec(self):
        """
        To help avoid pipeline stalls, ChangeCipherSpec is an independent TLS
        protocol content type, and is not actually a TLS handshake message.

        Send it to the server.
        """

    @_machine.output()
    def _send_finished(self):
        """
        Send the server a Finished message.
        """

    @_machine.output()
    def _send_alert_no_renegotiation(self):
        """
        Send the server an Alert(no_renegotiation) message.
        """

    @_machine.state()
    def idle(self):
        """
        The client is idle.
        """

    @_machine.state()
    def wait_1(self):
        """
        The client is waiting.
        """

    @_machine.state()
    def wait_2(self):
        """
        The client is waiting (for a Finished).
        """

    @_machine.state()
    def app_data(self):
        """
        The client is ready to exchange application data.
        """

    @_machine.state()
    def shutdown(self):
        """
        The connection to the server has been shut down.
        """

    @_machine.state()
    def host_initiated_closing(self):
        """
        The host has initiated closing the connection.
        """
    @_machine.output()
    def _send_alert_close_notify(self):
        """
        Send the server an Alert(close_notify) message.
        """

    @_machine.output()
    def _close_callback_false(self):
        """
        TODO: Indicates something bad happened and we shut the connection down
        instead of closing it.

        I don't think this is a good output name, but unsure what to call it.
        """

    @_machine.output()
    def _close_callback_true(self):
        """
        TODO: Indicates we closed the connection cleanly.

        I don't think this is a good output name, but unsure what to call it.
        """

    @_machine.output()
    def _indicate_EOF_to_the_application_somehow(self):
        """
        TODO: The (sad) name says it all.
        """

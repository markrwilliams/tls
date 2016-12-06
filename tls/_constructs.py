# This file is dual licensed under the terms of the Apache License, Version
# 2.0, and the BSD License. See the LICENSE file in the root of this repository
# for complete details.

from __future__ import absolute_import, division, print_function

from functools import partial

from construct import (Array, Bytes, Pass, Struct,
                       Switch, UBInt16, UBInt32,
                       UBInt8)

from tls._common import enums

from tls._common._constructs import (EnumClass, EnumSwitch, Opaque,
                                     PrefixedBytes, SizeAtLeast, SizeAtMost,
                                     SizeWithin, TLSOneOf, TLSPrefixedArray,
                                     UBInt24)

from tls.ciphersuites import CipherSuites


ProtocolVersion = Struct(
    "version",
    UBInt8("major"),
    UBInt8("minor"),
)

TLSPlaintext = Struct(
    "TLSPlaintext",
    UBInt8("type"),
    ProtocolVersion,
    PrefixedBytes("fragment",
                  SizeAtMost(UBInt16("length"),
                             max_size=2 ** 14)),
)

TLSCompressed = Struct(
    "TLSCompressed",
    UBInt8("type"),
    ProtocolVersion,
    PrefixedBytes("fragment",
                  SizeAtMost(UBInt16("length"),
                             max_size=2 ** 14 + 1024)),
)

TLSCiphertext = Struct(
    "TLSCiphertext",
    UBInt8("type"),
    ProtocolVersion,
    PrefixedBytes("fragment",
                  SizeAtMost(UBInt16("length"),
                             max_size=2 ** 14 + 2048)),
)

Random = Struct(
    "random",
    UBInt32("gmt_unix_time"),
    Bytes("random_bytes", 28),
)

SessionID = Struct(
    "session_id",
    PrefixedBytes("session_id"),
)

CompressionMethods = Struct(
    "compression_methods",
    SizeAtLeast(UBInt8("length"), min_size=1),
    Array(lambda ctx: ctx.length, UBInt8("compression_methods"))
)

HostName = PrefixedBytes("hostname", UBInt16("length"))

ServerName = Struct(
    "server_name",
    EnumClass(UBInt8("name_type"), enums.NameType),
    Switch(
        "name",
        lambda ctx: ctx.name_type,
        {
            enums.NameType.HOST_NAME: HostName
        }
    )
)

ServerNameList = TLSPrefixedArray("server_name_list", ServerName)

ClientCertificateURL = Struct(
    "client_certificate_url",
    # The "extension_data" field of this extension SHALL be empty.
)

SignatureAndHashAlgorithm = Struct(
    "algorithms",
    EnumClass(UBInt8("hash"), enums.HashAlgorithm),
    EnumClass(UBInt8("signature"), enums.SignatureAlgorithm),
)

SupportedSignatureAlgorithms = TLSPrefixedArray(
    "supported_signature_algorithms",
    SignatureAndHashAlgorithm,
    length_validator=partial(SizeAtLeast, min_size=1),
)

MaxFragmentLength = EnumClass(UBInt8("size"), enums.MaxFragmentLength)

Extension = Struct(
    "extensions",
    *EnumSwitch(
        type_field=UBInt16("type"),
        type_enum=enums.ExtensionType,
        value_field="data",
        value_choices={
            enums.ExtensionType.SERVER_NAME: Opaque(ServerNameList),
            enums.ExtensionType.SIGNATURE_ALGORITHMS: Opaque(
                SupportedSignatureAlgorithms
            ),
            enums.ExtensionType.CLIENT_CERTIFICATE_URL: Opaque(
                ClientCertificateURL,
            ),
            enums.ExtensionType.MAX_FRAGMENT_LENGTH: Opaque(
                MaxFragmentLength,
            ),
        },
        default=Pass,
    )
)

Extensions = TLSPrefixedArray("extensions", Extension)

ClientHello = Struct(
    "ClientHello",
    ProtocolVersion,
    Random,
    SessionID,
    TLSPrefixedArray("cipher_suites",
                     EnumClass(UBInt8("cipher_suite"), CipherSuites),
                     length_validator=partial(SizeAtLeast, min_size=1)),
    CompressionMethods,
    Extensions,
)

ServerHello = Struct(
    "ServerHello",
    ProtocolVersion,
    Random,
    SessionID,
    Bytes("cipher_suite", 2),
    UBInt8("compression_method"),
    Extensions,
)

ClientCertificateType = Struct(
    "certificate_types",
    SizeAtLeast(UBInt8("length"), min_size=1),
    Array(lambda ctx: ctx.length, UBInt8("certificate_types")),
)


DistinguishedName = Struct(
    "certificate_authorities",
    UBInt16("length"),
    Bytes("certificate_authorities", lambda ctx: ctx.length),
)

CertificateRequest = Struct(
    "CertificateRequest",
    ClientCertificateType,
    SupportedSignatureAlgorithms,
    DistinguishedName,
)

ServerDHParams = Struct(
    "ServerDHParams",
    PrefixedBytes("dh_p", UBInt16("dh_p_length")),
    PrefixedBytes("dh_g", UBInt16("dh_g_length")),
    PrefixedBytes("dh_Ys", UBInt16("dh_Ys_length")),
)

PreMasterSecret = Struct(
    "pre_master_secret",
    ProtocolVersion,
    Bytes("random_bytes", 46),
)

ASN1Cert = Struct(
    "ASN1Cert",
    SizeWithin(UBInt32("length"),
               min_size=1, max_size=2 ** 24 - 1),
    Bytes("asn1_cert", lambda ctx: ctx.length),
)

Certificate = Struct(
    "Certificate",
    SizeWithin(UBInt32("certificates_length"),
               min_size=1, max_size=2 ** 24 - 1),
    Bytes("certificates_bytes", lambda ctx: ctx.certificates_length),
)

Handshake = Struct(
    "Handshake",
    UBInt8("msg_type"),
    UBInt24("length"),
    Bytes("body", lambda ctx: ctx.length),
)

Alert = Struct(
    "Alert",
    UBInt8("level"),
    UBInt8("description"),
)

URLAndHash = Struct(
    "url_and_hash",
    SizeWithin(UBInt16("length"),
               min_size=1, max_size=2 ** 16 - 1),
    Bytes("url", lambda ctx: ctx.length),
    TLSOneOf(UBInt8('padding'), [1]),
    Bytes("sha1_hash", 20),
)

CertificateURL = Struct(
    "CertificateURL",
    EnumClass(UBInt8("type"), enums.CertChainType),
    TLSPrefixedArray("url_and_hash_list", URLAndHash),
)

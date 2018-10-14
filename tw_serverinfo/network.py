import logging
import secrets
import socket

from tw_serverinfo.models import Server


class Network(object):
    # www.teeworlds.com has no AAAA domain record and doesn't support IPv6 only requests
    PROTOCOL_FAMILY = socket.AF_INET

    # connection timeout in ms
    CONNECTION_TIMEOUT = 1000

    # sleep duration between checking if we received a packet in ms
    CONNECTION_SLEEP_DURATION = 50

    PACKETS = {
        'SERVERBROWSE_GETCOUNT': b'\xff\xff\xff\xffcou2',
        'SERVERBROWSE_COUNT': b'\xff\xff\xff\xffsiz2',
        'SERVERBROWSE_GETLIST': b'\xff\xff\xff\xffreq2',
        'SERVERBROWSE_LIST': b'\xff\xff\xff\xfflis2',
        'SERVERBROWSE_GETINFO_64_LEGACY': b'\xff\xff\xff\xfffstd',
        'SERVERBROWSE_INFO_64_LEGACY': b'\xff\xff\xff\xffdtsf',
        'SERVERBROWSE_GETINFO': b'\xff\xff\xff\xffgie3',
        'SERVERBROWSE_INFO': b'\xff\xff\xff\xffinf3',
        'SERVERBROWSE_INFO_EXTENDED': b'\xff\xff\xff\xffiext',
        'SERVERBROWSE_INFO_EXTENDED_MORE': b'\xff\xff\xff\xffiex+',
    }

    @staticmethod
    def send_packet(sock: socket.socket, data: bytes, extra_data: bytes, server: Server, add_token=True) -> None:
        """Generate or reuse a request token  and send the passed data with the request token to the passed socket
        Returns the updated server dict with additional token on game server types

        :type sock: socket.socket
        :type data: bytes
        :type extra_data: bytes
        :type server: dict
        :type add_token: bool
        :return:
        """
        if not server.request_token:
            server.request_token = secrets.token_bytes(nbytes=2)
            logging.log(logging.DEBUG, 'generated server request token: {token!r}'.format(token=server.request_token))

        packet = b'%s%s\0\0%s' % (extra_data, server.request_token, data)

        if add_token:
            if not server.token:
                server.token = secrets.token_bytes(nbytes=1)
                logging.log(logging.DEBUG, 'generated server token: {token!r}'.format(token=server.token))
            packet += server.token

        logging.log(logging.DEBUG, 'sending packet ({packet!r}) to {ip:s}:{port:d}'.format(packet=packet, ip=server.ip,
                                                                                           port=server.port))
        sock.sendto(packet, (server.ip, server.port))

    @staticmethod
    def receive_packet(sock: socket.socket, servers: list, callback: callable) -> bool:
        """Check if we received a packet if yes check for the servers with the ip and port
        and pass the server together with the data to the processing function given as a callback

        :param sock:
        :param servers:
        :param callback:
        :return:
        """
        try:
            data, addr = sock.recvfrom(2048, 0)
        except BlockingIOError:
            return False

        logging.log(logging.DEBUG, 'received data ({data!r}) from {ip:s}:{port:d}'.format(data=data, ip=addr[0],
                                                                                          port=addr[1]))
        for server in servers:  # type: Server
            if server.ip == addr[0] and server.port == addr[1]:
                callback(data, server)
                return True
        return False

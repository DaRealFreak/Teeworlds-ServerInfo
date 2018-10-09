import secrets
import socket


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
    def send_packet(sock: socket.socket, data: bytes, server: dict):
        """Generate or reuse a request token  and send the passed data with the request token to the passed socket

        :type sock: socket.socket
        :type data: bytes
        :type server: dict
        :return:
        """
        if 'request_token' not in server:
            server['request_token'] = secrets.token_bytes(nbytes=2)

        packet = b'xe%s\0\0%s' % (server['request_token'], data)

        if server['type'] == 'game':
            if 'token' not in server:
                server['token'] = secrets.token_bytes(nbytes=1)
            packet += server['token']

        sock.sendto(packet, (server['ip'], server['port']))
        return server

    @staticmethod
    def receive_packet(sock: socket.socket, servers: dict, callback: callable):
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

        for key, server in servers.items():
            if server['ip'] == addr[0] and server['port'] == addr[1]:
                callback(data, server)

        return True

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import sys
import ssl
import socket
import time
import traceback
import websocket
import logging as logs

from contextlib import closing
from threading import Thread
from websocket import create_connection, WebSocket

from knack.util import CLIError
from knack.log import get_logger
logger = get_logger(__name__)


class TunnelWebSocket(WebSocket):
    def recv_frame(self):
        frame = super(TunnelWebSocket, self).recv_frame()
        logger.info('Received frame: %s', frame)
        return frame

    def recv(self):
        data = super(TunnelWebSocket, self).recv()
        logger.info('Received websocket data: %s', data)
        return data

    def send_binary(self, data):
        super(TunnelWebSocket, self).send_binary(data)


class TunnelServer(object):
    def __init__(self, local_addr, local_port, remote_addr, remote_user_name, remote_password):
        self.local_addr = local_addr
        self.local_port = local_port
        if not self.is_port_open():
            raise CLIError('Defined port is currently unavailable')
        self.remote_addr = remote_addr
        self.remote_user_name = remote_user_name
        self.remote_password = remote_password
        logger.info('Creating a socket on port: %s', self.local_port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logger.info('Setting socket options')
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        logger.info('Binding to socket on local address and port')
        self.sock.bind((self.local_addr, self.local_port))
        logger.info('Finished initialization')

    def create_basic_auth(self):
        from base64 import b64encode, b64decode
        basic_auth_string = '{}:{}'.format(self.remote_user_name, self.remote_password).encode()
        basic_auth_string = b64encode(basic_auth_string).decode('utf-8')
        return basic_auth_string

    def is_port_open(self):
        is_port_open = False
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            if sock.connect_ex(('', self.local_port)) == 0:
                logger.info('Port %s is NOT open', self.local_port)
            else:
                logger.warning('Port %s is open', self.local_port)
                is_port_open = True
            return is_port_open

    def is_port_set_to_default(self):
        import sys
        import certifi
        import urllib3
        try:
            import urllib3.contrib.pyopenssl
            urllib3.contrib.pyopenssl.inject_into_urllib3()
        except ImportError:
            pass

        http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
        headers = urllib3.util.make_headers(basic_auth='{0}:{1}'.format(self.remote_user_name, self.remote_password))
        url = 'https://{}{}'.format(self.remote_addr, '.scm.azurewebsites.net/AppServiceTunnel/Tunnel.ashx?GetStatus')
        r = http.request(
            'GET',
            url,
            headers=headers,
            preload_content=False
        )
        if r.status != 200:
            raise CLIError("Failed to connect to '{}' with status code '{}' and reason '{}'".format(url, r.status, r.reason))
        msg = r.read().decode('utf-8')
        logger.info('Status response message: %s', msg)
        if 'FAIL' in msg.upper():
            logger.warning('WARNING - Remote debugging may not be setup properly. Reponse content: %s', msg)
        if '2222' in msg:
            return True
        return False

    def listen(self):
        self.sock.listen(100)
        index = 0
        basic_auth_string = self.create_basic_auth()
        while True:
            self.client, address = self.sock.accept()
            self.client.settimeout(60)
            host = 'wss://{}{}'.format(self.remote_addr, '.scm.azurewebsites.net/AppServiceTunnel/Tunnel.ashx')
            basic_auth_header = 'Authorization: Basic {}'.format(basic_auth_string)
            cli_logger = get_logger()  # get CLI logger which has the level set through command lines
            is_verbose = any(handler.level <= logs.INFO for handler in cli_logger.handlers)
            if is_verbose:
                logger.info('Websocket tracing enabled')
                websocket.enableTrace(True)
            else:
                logger.warning('Websocket tracing disabled, use --verbose flag to enable')
                websocket.enableTrace(False)
            self.ws = create_connection(host,
                                        sockopt=((socket.IPPROTO_TCP, socket.TCP_NODELAY, 1),),
                                        class_=TunnelWebSocket,
                                        header=[basic_auth_header],
                                        sslopt={'cert_reqs': ssl.CERT_NONE},
                                        enable_multithread=True)
            logger.info('Websocket, connected status: %s', self.ws.connected)

            index = index + 1
            logger.info('Got debugger connection... index: %s', index)
            debugger_thread = Thread(target=self.listen_to_client, args=(self.client, self.ws, index))
            web_socket_thread = Thread(target=self.listen_to_web_socket, args=(self.client, self.ws, index))
            debugger_thread.start()
            web_socket_thread.start()
            logger.info('Both debugger and websocket threads started...')
            logger.warning('Successfully started local server..')
            debugger_thread.join()
            web_socket_thread.join()
            logger.info('Both debugger and websocket threads stopped...')
            logger.warning('Stopped local server..')

    def listen_to_web_socket(self, client, ws_socket, index):
        while True:
            try:
                logger.info('Waiting for websocket data, connection status: %s, index: %s', ws_socket.connected, index)
                data = ws_socket.recv()
                logger.info('Received websocket data: %s, index: %s', data, index)
                if data:
                    # Set the response to echo back the recieved data
                    response = data
                    logger.info('Sending to debugger, response: %s, index: %s', response, index)
                    client.sendall(response)
                    logger.info('Done sending to debugger, index: %s', index)
                else:
                    logger.info('Client disconnected!, index: %s', index)
                    client.close()
                    ws_socket.close()
                    break
            except:
                traceback.print_exc(file=sys.stdout)
                client.close()
                ws_socket.close()
                return False

    def listen_to_client(self, client, ws_socket, index):
        while True:
            try:
                logger.info('Waiting for debugger data, index: %s', index)
                buf = bytearray(4096)
                nbytes = client.recv_into(buf, 4096)
                logger.info('Received debugger data, nbytes: %s, index: %s', nbytes, index)
                if nbytes > 0:
                    responseData = buf[0:nbytes]
                    logger.info('Sending to websocket, response data: %s, index: %s', responseData, index)
                    ws_socket.send_binary(responseData)
                    logger.info('Done sending to websocket, index: %s', index)
                else:
                    logger.warn('Client disconnected %s', index)
                    client.close()
                    ws_socket.close()
                    break
            except:
                traceback.print_exc(file=sys.stdout)
                client.close()
                ws_socket.close()
                return False

    def start_server(self):
        logger.warning('Starting local server..')
        self.listen()

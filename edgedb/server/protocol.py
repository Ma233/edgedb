##
# Copyright (c) 2016 MagicStack Inc.
# All rights reserved.
#
# See LICENSE for details.
##


import asyncio
import enum
import json
import sys


from edgedb.lang import edgeql
from edgedb.server import pgsql as backend
from edgedb.server import executor
from edgedb.server import planner

from edgedb.lang.schema import database as s_db
from edgedb.lang.schema import delta as s_delta
from edgedb.lang.schema import deltas as s_deltas

from edgedb.lang.common.debug import debug


class ConnectionState(enum.Enum):
    NOT_CONNECTED = 0
    NEW = 1
    READY = 2


class ProtocolError(Exception):
    pass


def is_ddl(plan):
    return isinstance(plan, s_delta.Command) and \
        not isinstance(plan, s_db.DatabaseCommand) and \
        not isinstance(plan, s_deltas.DeltaCommand)


class Protocol(asyncio.Protocol):
    def __init__(self, pg_cluster, loop):
        self._pg_cluster = pg_cluster
        self._loop = loop
        self.pgconn = None
        self.state = ConnectionState.NOT_CONNECTED

    def connection_made(self, transport):
        self.transport = transport
        self.state = ConnectionState.NEW

    def connection_lost(self, exc):
        self.transport.close()
        if self.pgconn is not None:
            self.pgconn.terminate()

    def data_received(self, data):
        msg = json.loads(data.decode('utf-8'))
        self.process_message(msg)

    def process_message(self, message):
        if message['__type__'] == 'init':
            database = message.get('database')
            user = message.get('user')

            if not database or not user:
                raise ProtocolError('invalid startup packet')

            fut = self._loop.create_task(self._pg_cluster.connect(
                database=database, user=user, loop=self._loop
            ))

            fut.add_done_callback(self._on_pg_connect)

        elif message['__type__'] == 'query':
            if self.state != ConnectionState.READY:
                raise ProtocolError('unexpected message: query')

            query = message.get('query')
            if not query:
                raise ProtocolError('invalid query message')

            fut = self._loop.create_task(self._run_query(query))
            fut.add_done_callback(self._on_query_done)

        elif message['__type__'] == 'script':
            if self.state != ConnectionState.READY:
                raise ProtocolError('unexpected message: script')

            script = message.get('script')
            if not script:
                raise ProtocolError('invalid script message')

            fut = self._loop.create_task(self._run_script(script))
            fut.add_done_callback(self._on_script_done)

    def send_message(self, msg):
        self.transport.write(json.dumps(msg).encode('utf-8'))

    def send_error(self, err):
        import traceback
        import edgedb.lang.common.markup
        edgedb.lang.common.markup.dump(vars(err))
        traceback.print_exception(
            type(err), err, err.__traceback__, file=sys.stderr)
        self.send_message({
            '__type__': 'error',
            'data': {
                'code': getattr(err, 'code', 0),
                'message': str(err)
            }
        })

    @debug
    async def _run_script(self, script):
        statements = edgeql.parse_block(script)

        results = []

        for statement in statements:
            """LOG [statement] Executing EdgeQL statement
            print(edgeql.generate_source(statement, pretty=True))
            """
            plan = planner.plan_statement(statement, self.backend)
            result = await executor.execute_plan(plan, self.backend)
            if result is not None and isinstance(result, list):
                loaded = []
                for row in result:
                    if isinstance(row, str):
                        # JSON result
                        row = json.loads(row)
                    loaded.append(row)
                result = loaded

            """LOG [result] Statement result
            print(result)
            """
            results.append(result)

        return results

    def _on_pg_connect(self, fut):
        try:
            self.pgconn = fut.result()
        except asyncio.CancelledError:
            return
        except Exception as e:
            self.send_error(e)
            return

        fut = self._loop.create_task(backend.open_database(
            self.pgconn
        ))

        fut.add_done_callback(self._on_edge_connect)

    def _on_edge_connect(self, fut):
        try:
            self.backend = fut.result()
        except asyncio.CancelledError:
            return
        except Exception as e:
            self.send_error(e)
            return

        self.state = ConnectionState.READY

        self.send_message({
            '__type__': 'authresult',
            'result': 'OK'
        })

    def _on_script_done(self, fut):
        try:
            result = fut.result()
        except asyncio.CancelledError:
            return
        except Exception as e:
            self.send_error(e)
            return

        self.state = ConnectionState.READY

        self.send_message({
            '__type__': 'result',
            'result': result
        })
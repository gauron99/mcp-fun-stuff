import logging
import os
import signal
import hypercorn.config
import hypercorn.asyncio
import asyncio


DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_LISTEN_ADDRESS = "127.0.0.1:8080"

def serve(f):
    return ASGIApplication(f()).serve()

class ASGIApplication():
    def __init__(self, f):
        self.f = f
        self.stop_event = asyncio.Event()
        if hasattr(self.f, "handle") is not True:
            raise AttributeError("Function must implement a 'handle' method.")

        # Inform the user via logs that defaults will be used for health
        # endpoints if no matchin methods were provided.
        if hasattr(self.f, "alive") is not True:
            logging.info(
                "function does not implement 'alive'. Using default " +
                "implementation for liveness checks."
            )

        if hasattr(self.f, "ready") is not True:
            logging.info(
                "function does not implement 'ready'. Using default " +
                "implementation for readiness checks."
            )

    def serve(self):
        """serve serving this ASGIhandler, delegating implementation of
           methods as necessary to the wrapped Function instance"""
        cfg = hypercorn.config.Config()
        cfg.bind = [os.getenv('LISTEN_ADDRESS', DEFAULT_LISTEN_ADDRESS)]

        logging.debug(f"function starting on {cfg.bind}")
        return asyncio.run(self._serve(cfg))

    async def _serve(self, cfg):
        loop = asyncio.get_event_loop()
        loop.add_signal_handler(signal.SIGINT, self._handle_signal)
        loop.add_signal_handler(signal.SIGTERM, self._handle_signal)

        await hypercorn.asyncio.serve(self, cfg)

    def _handle_signal(self):
        logging.info("Signal received: initiating shutdown")
        self.stop_event.set()

    async def on_start(self):
        """on_start handles the ASGI server start event, delegating control
           to the internal Function instance if it has a "start" method."""
        if hasattr(self.f, "start"):
            self.f.start(os.environ.copy())
        else:
            logging.info("function does not implement 'start'. Skipping.")

    async def on_stop(self):
        if hasattr(self.f, "stop"):
            self.f.stop()
        else:
            logging.info("function does not implement 'stop'. Skipping.")
        self.stop_event.set()

    async def __call__(self, scope, receive, send):
        if scope['type'] == 'lifespan':
            while True:
                message = await receive()
                if message['type'] == 'lifespan.startup':
                    await self.on_start()
                    await send({'type': 'lifespan.startup.complete'})
                elif message['type'] == 'lifespan.shutdown':
                    await self.on_stop()
                    await send({'type': 'lifespan.shutdown.complete'})
                    return
                else:
                    break

        # Assert request is HTTP
        if scope["type"] != "http":
            await send_exception(send, 400,
                                 "Functions currently only support ASGI/HTTP " +
                                 f"connections. Got {scope['type']}"
                                 )
            return

        # Route request
        try:
            if scope['path'] == '/health/liveness':
                await self.handle_liveness(scope, receive, send)
            elif scope['path'] == '/health/readiness':
                await self.handle_readiness(scope, receive, send)
            else:
                await self.f.handle(scope, receive, send)
        except Exception as e:
            await send_exception(send, 500, f"Error: {e}")



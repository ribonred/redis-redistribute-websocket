from abc import ABC, abstractmethod
import asyncio
from asyncio.log import logger
import aiohttp
from aiohttp import ClientSession
from aiohttp.client import _WSRequestContextManager
from .config import CREDS, Credentials, Redis
from utils.enums import Action, Status
import json
import aioredis
import logging
logger = logging.getLogger(__name__)


class AbstractBasePublisher(ABC):
    @classmethod
    @abstractmethod
    def get_iex_publisher(cls):
        pass

    @classmethod
    @abstractmethod
    def get_sip_publisher(cls):
        pass


class AbstractPublisher(ABC):
    session: ClientSession
    baseurl: str
    credentials: Credentials
    connected: bool = False
    authenticated: bool = False

class BasePublisher(AbstractPublisher):
    credentials = CREDS
    ws :_WSRequestContextManager
    publisher :aioredis.client.PubSub
    group_prefix="asgi__group__"

    def __init__(self, baseurl: str, symbols: list[str]=[]):
        self.baseurl = baseurl
        self.symbols = symbols
        self.session = ClientSession
        self.redisconfig = Redis
    
    def assign_symbols(self, symbols:list[str]):
        self.symbols = symbols

    async def authenticate(self):
        auth_data = {
            "action": "auth",
            "key": f"{CREDS.KEY}",
            "secret": f"{CREDS.SECRET}",
        }
        logger.info("authenticating")
        await self.ws.send_str(json.dumps(auth_data))
    
    async def switch(self,key, obj):
        return obj.get(key,None)
    
    async def main(self):
        if not self.symbols:
            logger.critical("no symbols to subscribe")
            raise NotImplemented("Symbols must be set")
        self.redis = aioredis.from_url(self.redisconfig.full_url)
        self.session = self.session()
        async with self.session.ws_connect(self.baseurl) as ws:
               async for msg in ws:
                    match msg.type:
                        case (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                            break
                        case (aiohttp.WSMsgType.TEXT):
                            await self.handle_message(json.loads(msg.data),ws)
    
    async def handle_message(self, msg:list[dict],ws):
        try:
            messages = msg[0]
            match await self.switch("T",messages):
                case Status.SUCCESS.value:
                    self.ws = ws
                    await self.success_handler(messages)
                case Status.ERROR.value:
                    print("error connection")
                case Status.SUBSCRIBTION.value:
                    logger.info("subscription accepted")
                    # asyncio.ensure_future(self.test_publish())
                case Status.QUOTES.value:
                    await self.publish(messages)
                case _:
                    logger.warning("unknown message")
                    
                    
        except IndexError as e:
            logger.critical("schema invalid \n {} \n".format(msg))
            logger.critical(e.with_traceback())
            
            raise IndexError("invalid payload schema")
        
    async def success_handler(self, msg:dict):
        match await self.switch("msg",msg):
            case Action.CONNECTED.value:
                self.connected =True
                if not self.authenticated:
                    await self.authenticate()
            case Action.AUTHENTICATED.value:
                self.authenticated = True
                logger.info("authenticated")
                await self.subscribe()
                
    async def subscribe(self):
        subscribe_data = {"action": "subscribe", "quotes": self.symbols}
        await self.ws.send_str(json.dumps(subscribe_data))
    
    async def publish(self, msg:dict):
        msg["type"] = "market_event"
        msg["channels"] = "{}{}".format(self.group_prefix,msg["S"])
        asyncio.ensure_future(self.redis.publish(msg["channels"],json.dumps(msg)))
    
    async def test_publish(self):
        count = 0
        while True:
            data_to= {"new":f"{count}","type":"market_event"}
            print("sending")
            await asyncio.sleep(3)
            await self.redis.publish("asgi__group__DOCU",json.dumps(data_to))
            count+=1
    
    
    
       
        


class IexPublisher(BasePublisher):
    pass


class SipPublisher(BasePublisher):
    pass


class Publisher(AbstractBasePublisher):
    demo_base_url = "stream.data.sandbox.alpaca.markets"
    base_url = "stream.data.alpaca.markets"
    api_ver = "v2"
    protocol = "wss"
    source = ["iex", "sip"]

    @classmethod
    def get_iex_publisher(cls, demo=False, api_ver=None, protocol=None):
        cls.protocol = protocol or cls.protocol
        cls.api_ver = api_ver or cls.api_ver
        if demo:
            return IexPublisher(
                f"{cls.protocol}://{cls.demo_base_url}/{cls.api_ver}/{cls.source[0]}"
            )
        return IexPublisher(
            f"{cls.protocol}://{cls.base_url}/{cls.api_ver}/{cls.source[0]}"
        )

    @classmethod
    def get_sip_publisher(cls, demo=False, api_ver=None, protocol=None):
        cls.protocol = protocol or cls.protocol
        cls.api_ver = api_ver or cls.api_ver
        if demo:
            return SipPublisher(
                f"{cls.protocol}://{cls.demo_base_url}/{cls.api_ver}/{cls.source[1]}"
            )
        return SipPublisher(
            f"{cls.protocol}://{cls.base_url}/{cls.api_ver}/{cls.source[1]}"
        )

from abc import ABC, abstractmethod
import asyncio
import aiohttp
from aiohttp import ClientSession
from aiohttp.client import _WSRequestContextManager
from .config import CREDS, Credentials, REDIS, RPC_URL
from xmlrpc.client import ServerProxy
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
    """_summary_

    Args:
        AbstractPublisher (_type_): Base publisher to listen stream market

    Raises:
        NotImplemented: this class should have list of symbols to subscribe
        IndexError: this will raises whenever schema of websocket response changes

    Returns:
        _type_: there is no return value
    """
    credentials = CREDS
    redisconfig = REDIS
    ws :_WSRequestContextManager
    group_prefix="asgi__group__"

    def __init__(self, baseurl: str, symbols: list[str]=[]):
        self.baseurl = baseurl
        self.symbols = symbols
        self.session = ClientSession
    
    def assign_symbols(self, symbols:list[str]):
        self.symbols = symbols
    
    def assign_symbols_from_rpc(self):
        # TODO: multicurrency later
        logger.info(
            "assigning symbols from rpc server {}".format(RPC_URL)
        )
        try:
            server: ServerProxy = ServerProxy(RPC_URL)
            self.symbols = server.get_listed_ticker("usd")
        except Exception:
            return self.assign_symbols(["UPS", "CF"])

    async def authenticate(self):
        auth_data = {
            "action": "auth",
            "key": f"{CREDS.KEY}",
            "secret": f"{CREDS.SECRET}",
        }
        logger.info("authenticating")
        logger.info(self.baseurl)
        logger.debug(auth_data)
        await self.ws.send_str(json.dumps(auth_data))
    
    async def switch(self,key, obj):
        return obj.get(key,None)
    
    async def main(self):
        if not self.symbols:
            logger.critical("no symbols to subscribe")
            raise NotImplemented("Symbols must be set")
        # make redis connection
        self.redis = aioredis.from_url(self.redisconfig.full_url)
        await self.redis.set("streaming_ticker", str(self.symbols))
        logger.info(f"stream ticker set to {len(self.symbols)} symbols")
        # invoking sessions for websocket
        self.session = self.session()
        async with self.session.ws_connect(self.baseurl) as ws:
               async for msg in ws:
                   # please notice
                   # match syntax (only in python >= 3.10)
                    match msg.type:
                        case (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                            break
                        case (aiohttp.WSMsgType.TEXT):
                            asyncio.create_task(self.handle_message(json.loads(msg.data),ws))
    
    async def handle_message(self, msg:list[dict],ws):
        try:
            messages = msg[0]
            match await self.switch("T",messages):
                case Status.SUCCESS.value:
                    self.ws = ws
                    await self.success_handler(messages)
                case Status.ERROR.value:
                    # if error occurs, websocket will close automatically by the server
                    # TODO: recreate connection handshake
                    logger.error("connection error")
                    logger.error(msg)
                case Status.SUBSCRIBTION.value:
                    # indicate if subscription is successful
                    logger.info("subscription accepted")
                    logger.info("Listen incoming data ...")
                    # asyncio.ensure_future(self.test_publish())
                case Status.QUOTES.value:
                    # publish to redis
                    await self.publish(messages)
                case Status.DAYS.value:
                    logger.info(messages)
                case None:
                    logger.error("unknown message")
                    logger.error(msg)
                    
                    
                    
        except IndexError as e:
            # exit connection
            # TODO: create a report notification
            logger.critical("schema invalid \n {} \n".format(msg))
            await self.session.close()
            
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
        """_summary_
        for now only quotes are supported
        we will add more as is needed
        """
        subscribe_data = {"action": "subscribe", "trades": self.symbols,"bars":self.symbols}
        await self.ws.send_str(json.dumps(subscribe_data))
    
    async def publish(self, msg:dict):
        msg["type"] = "market_event"
        msg["channels"] = "{}{}".format(self.group_prefix,msg["S"])
        # ensure_future is used to ensure that the task is executed in the event loop
        # this wrapper function is non-blocking for couroutine
        await self.redis.publish(msg["channels"],json.dumps(msg))
        
    
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
    """_summary_

    Args:
        AbstractBasePublisher (_type_): this is wrapper of publisher
        demo (bool): this is to choose using sandbox or production
        api_ver (str): this is to choose using api version
        protocol (str): this is to choose using protocol we can use https (SSE) / wss

    Returns:
        _type_: publisher object
    """
    demo_base_url = "stream.data.sandbox.alpaca.markets"
    base_url = "stream.data.alpaca.markets"
    api_ver = "v2"
    protocol = "wss"
    source = ["iex", "sip"]

    @classmethod
    def get_iex_publisher(cls, demo:bool=False, api_ver:str|None=None, protocol:str|None=None):
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
    def get_sip_publisher(cls, demo:bool=False, api_ver:str|None=None, protocol:str|None=None):
        cls.protocol = protocol or cls.protocol
        cls.api_ver = api_ver or cls.api_ver
        if demo:
            return SipPublisher(
                f"{cls.protocol}://{cls.demo_base_url}/{cls.api_ver}/{cls.source[1]}"
            )
        return SipPublisher(
            f"{cls.protocol}://{cls.base_url}/{cls.api_ver}/{cls.source[1]}"
        )

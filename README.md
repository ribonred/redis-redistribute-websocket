# STREAM PROXY FOR MARKET PRICE :
## requirements:
- python 3.10.1
- linux os
- redis server

### explaination:
the proxy server will request all asklora USD ticker to alpaca in one channel. stream response from alpaca will be managed by proxy server and create channel in redis server using pubsub for each ticker. pubsub is real time publish and receive data <br/>
<br/>
Backend will manage the request from apps/user/consumer. if consumer or other backends needs streaming data we are not making new request to alpaca, instead we route it to stock channel in Redis Server. each consumer/backends can subcribe as many channel they want to listen. could be user favorite list of stock , list asklora topstock , all stock.
<br/>
## Supported Channel:
- &check; Quotes
- &#9746; Trades
- &#9746; News
- &#9746; stock status

```mermaid
  stateDiagram
    TICKER
    PROXY --> REQUEST
    REQUEST --> TICKER
    TICKER --> ALPACA
    ALPACA --> RESPONSE


    state TICKER{
        AAPL
        MSFT
        GOOGL
        AAL
    }
    RESPONSE --> PROXY_ACTION
    PROXY_ACTION --> REDIS_SERVER
    state split_ticker{
        direction TB
        aapl
        msft
        googl
    }
    state PROXY_ACTION{
        direction TB
        receive --> split_ticker
        split_ticker --> create_ticker_channel
        create_ticker_channel --> publish
    }
    state REDIS_SERVER{
        direction TB

        AAPL_CHANNEL
        MSFT_CHANNEL
        GOOGL_CHANNEL
        AAL_CHANNEL
    }
    state ASKLORA_BACKEND{
        ROUTE
    }
    state CONSUMER{
        direction TB
        [*] --> SUBSCRIBE
    }
    state SUBSCRIBE{
        AAPL.O
        MSFT.O
        AAL.O

    }
    OTHERBACKEND --> REDIS_SERVER
    state OTHERBACKEND{
        BACKEND_A 
        BACKEND_B 
        BACKEND_C
    }

    SUBSCRIBE --> ASKLORA_BACKEND
    ASKLORA_BACKEND --> ROUTE
    
    ROUTE --> REDIS_SERVER
    REDIS_SERVER --> ROUTE
    ROUTE --> STREAM
    STREAM --> FRONTEND
    STREAM --> MOBILE
    FRONTEND --> CONSUMER
    MOBILE --> CONSUMER

```

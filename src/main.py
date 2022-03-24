from common import Publisher
import asyncio


if __name__ == "__main__":
    pubs = Publisher.get_iex_publisher(demo=True)
    pubs.assign_symbols(["UPS", "CF", "EBAY", "DOCU", "VRSN"])
    try:
        asyncio.run(pubs.main())
    except KeyboardInterrupt:
        asyncio.run(pubs.session.close())

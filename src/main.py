from core import Publisher, config
import asyncio


if __name__ == "__main__":
    pubs = Publisher.get_sip_publisher(demo=config.CONF.demo)
    pubs.assign_symbols(["UPS", "CF", "VRSSEEN"])
    try:
        asyncio.run(pubs.main())
    except KeyboardInterrupt:
        asyncio.run(pubs.session.close())
    except Exception:
        asyncio.run(pubs.session.close())

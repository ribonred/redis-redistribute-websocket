use pyo3::{create_exception, exceptions::PyException};

create_exception!(redisrust, ConnectionError, PyException);
create_exception!(redisrust, ArgumentError, PyException);
create_exception!(redisrust, RedisError, PyException);
create_exception!(redisrust, PoolEmpty, PyException);
create_exception!(redisrust, PubSubClosed, PyException);

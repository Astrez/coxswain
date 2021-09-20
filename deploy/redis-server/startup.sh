redis-server --daemonize yes && sleep 1
redis-cli < /redis/rbac.redis
redis-cli save
redis-cli shutdown
# redis-server --requirepass passwordHere
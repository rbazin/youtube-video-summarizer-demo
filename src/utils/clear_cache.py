from redis import Redis

def clear_cache():
    r = Redis(host="redis-ytb-summarizer", port=6379, db=0)

    r.execute_command('FLUSHALL ASYNC')

if __name__ == '__main__':
    clear_cache()
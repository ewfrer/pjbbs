import memcache
#缓存
mc = memcache.Client(['127.0.0.1'])

def saveCache(key,value,time=0):
    mc.set(key=key,val=value,time=time)

def getCache(key):
    return mc.get(key)

def delete(key):
    mc.delete(key)
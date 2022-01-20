from threadpools import ThreadPools
import requests

urls = ["https://jsonplaceholder.typicode.com/todos/{}".format(i) for i in range(30)]
pool = ThreadPools(30)
r = requests.session()
def get(url):
    resp = r.get(url)
    return resp.json()
pool.map(get, urls)
pool.destroy()


pool = ThreadPools(30)
r = requests.session()
def get():
    resp = r.get("https://jsonplaceholder.typicode.com/todos/1")
    return resp.json()
pool.add_task(get)
pool.destroy()

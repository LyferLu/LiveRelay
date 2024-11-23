import asyncio
import json
import anyio
import ffmpeg
from jsonpath_ng.ext import parse
import httpx
import streamlink
from streamlink.options import Options

class LiveRelay:
    def __init__(self, config: dict, stream: dict, task_queue: asyncio.Queue):
        self.index = stream['index']
        self.id = stream['id']
        platform = stream['platform']
        name = stream.get('name', self.id)
        self.flag = f'[{platform}][{name}]'
        self.rtmp_server = config['RTMPServer']
        self.task_queue = task_queue
        self.headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        self.client = self.get_client()
    


    async def start(self):
        self.ssl = True
        while True:
            
            if self.task_queue.full():
                task = await self.task_queue.get()
                task_obj = task['task_obj']
                if task_obj.done() or self.index < task['index']:
                    task_obj.cancel()
                    try:
                        await task_obj
                    except asyncio.CancelledError:
                        print('任務已被取消')
                    self.task_queue.task_done()
                    continue
                else:
                    await self.task_queue.put(task)
                
                # print('Task Done')

            else:
                stream = await self.run()
                if stream:
                    task_obj = asyncio.create_task(self.relay_stream(stream))
                    await self.task_queue.put({"index": self.index, "task_obj": task_obj})
                     
            # print(f"{self.id}------{self.task_queue.qsize()}")
            await asyncio.sleep(10)  # 每10秒檢查一次

    async def run(self):
        pass

    async def request(self, method, url, **kwargs):
        try:
            response = await self.client.request(method, url, **kwargs)
            return response
        except httpx.ProtocolError as error:
            raise ConnectionError(f'{self.flag}直播检测请求协议错误\n{error}')
        except httpx.HTTPStatusError as error:
            raise ConnectionError(
                f'{self.flag}直播检测请求状态码错误\n{error}\n{response.text}')
        except anyio.EndOfStream as error:
            raise ConnectionError(f'{self.flag}直播检测代理错误\n{error}')
        except httpx.HTTPError as error:
           print(f'网络异常 重试...')
           raise ConnectionError(f'{self.flag}直播检测请求错误\n{repr(error)}')
        
    def get_client(self):
        client_kwargs = {
            'http2': True,
            'timeout': 10,
            'limits': httpx.Limits(max_keepalive_connections=100, keepalive_expiry=10 * 2),
            'headers': self.headers,
        }
        return httpx.AsyncClient(**client_kwargs)
        
    def get_streamlink(self):
        session = streamlink.session.Streamlink({
            'stream-segment-timeout': 60,
            'hls-segment-queue-threshold': 10
        })
        ssl = self.ssl
        # logger.info(f'是否验证SSL：{ssl}')
        session.set_option('http-ssl-verify', ssl)
        if self.headers:
            session.set_option('http-headers', self.headers)
        # if self.cookies:
        #     session.set_option('http-cookies', self.cookies)
        return session
    
    async def relay_stream(self, stream):
        # 推流的實現
        # print('Relay Stream')
        process = (
            ffmpeg
            .input(stream.to_url())
            .output(f"{self.rtmp_server}", format='flv', vcodec='copy', acodec='copy', **{'bsf:a': 'aac_adtstoasc'})
            .global_args('-loglevel', 'error')
            .global_args('-vsync', '1')
            .global_args('-async', '1')
            .run_async(pipe_stdout=True, pipe_stderr=True)
        )

        try:
            # 等待推流过程完成
            await asyncio.to_thread(process.wait)
        except asyncio.CancelledError:
            process.terminate()
            await asyncio.to_thread(process.wait)

        # # 打开流
        # fd = stream.open()

        # # 创建管道并使用ffmpeg处理
        # process = (
        #     ffmpeg
        #     .input('pipe:0')
        #     .output('rtmp://142.171.74.94:1935/live', format='flv', vcodec='copy', acodec='copy')
        #     .run_async(pipe_stdin=True)
        # )

        # try:
        #     while True:
        #         data = fd.read(1024)
        #         if not data:
        #             break
        #         process.stdin.write(data)
        # except Exception as e:
        #     print(f"发生错误：{e}")
        # except asyncio.CancelledError:
        #     process.terminate()
        #     await asyncio.to_thread(process.wait)
        # finally:
        #     fd.close()
        #     process.stdin.close()
        #     await asyncio.to_thread(process.wait)



class Youtube(LiveRelay):
    async def run(self):
        # print('Youtube')
        response = (await self.request(
            method='POST',
            url='https://www.youtube.com/youtubei/v1/browse',
            params={
                'key': 'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8',
                'prettyPrint': False
            },
            json={
                'context': {
                    'client': {
                        'hl': 'zh-CN',
                        'clientName': 'MWEB',
                        'clientVersion': '2.20230101.00.00',
                        'timeZone': 'Asia/Shanghai'
                    }
                },
                'browseId': self.id,
                'params': 'EgdzdHJlYW1z8gYECgJ6AA%3D%3D'
            }
        )).json()

        jsonpath_results = parse('$..videoWithContextRenderer').find(response)
        for match in jsonpath_results:
            video = match.value
            if '"style": "LIVE"' in json.dumps(video):
                video_id = video['videoId']
                url = f"https://www.youtube.com/watch?v={video_id}"
                title = video['headline']['runs'][0]['text']
                # if url not in recording:
                # stream = self.get_streamlink().streams(url).get('best')
                stream = streamlink.streams(url).get('best')

                if stream:
                    return stream
                else:
                    return None
        return None
        
class Twitch(LiveRelay):
    async def run(self):
        url = f'https://www.twitch.tv/{self.id}'
        # if url not in recording:
        response = (await self.request(
            method='POST',
            url='https://gql.twitch.tv/gql',
            headers={'Client-Id': 'kimne78kx3ncx6brgo4mv6wki5h1ko'},
            json=[{
                'operationName': 'StreamMetadata',
                'variables': {'channelLogin': self.id},
                'extensions': {
                    'persistedQuery': {
                        'version': 1,
                        'sha256Hash': 'a647c2a13599e5991e175155f798ca7f1ecddde73f7f341f39009c14dbf59962'
                    }
                }
            }]
        )).json()
        if response[0]['data']['user']['stream']:
            title = response[0]['data']['user']['lastBroadcast']['title']
            options = Options()
            options.set('disable-ads', True)
            # stream = self.get_streamlink().streams(url, options).get('best')  # HLSStream[mpegts]
            stream = streamlink.streams(url).get('best')

            if stream:
                return stream
            else:
                return None
        return None

def load_config(file_name):
    with open(file_name, "r") as f:
        return json.load(f)
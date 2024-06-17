import multiprocessing
from multiprocessing import shared_memory

# 辅助函数，将字符串列表编码为字节数组
def encode_strings(strings, max_str_length):
    encoded = bytearray()
    for string in strings:
        encoded.extend(string.encode('utf-8'))
        encoded.extend(b'\x00' * (max_str_length - len(string)))
    return encoded

# 辅助函数，将字节数组解码为字符串列表
def decode_strings(encoded, max_str_length, ignore_empty_str=True):
    strings = []
    for i in range(0, len(encoded), max_str_length):
        s = encoded[i:i+max_str_length].split(b'\x00', 1)[0].decode('utf-8')
        if not ignore_empty_str or s:
            strings.append(s)
    return strings

class SharedMemoryStrList(object):

    @staticmethod
    def create(name: str, strings: list, max_str_length: int, max_size: int):
        # 编码字符串数组
        encoded: bytearray = encode_strings(strings, max_str_length)
        # 创建共享内存块
        shm = shared_memory.SharedMemory(name=name, create=True, size=max_str_length*max_size)
        # 将编码后的字符串数组写入共享内存
        for i in range(len(encoded)):
            shm.buf[i] = encoded[i]
        shm.close()

    @staticmethod
    def read(name: str, max_str_length: int, ignore_empty_str=True):
        # 连接到共享内存
        shm = shared_memory.SharedMemory(name=name)
        buffer = shm.buf
        # 将 memoryview 转换为字节数组
        encoded = bytes(buffer[:])
        # 解码字符串数组
        strings = decode_strings(encoded, max_str_length, ignore_empty_str)
        shm.close()
        return strings
    
    @staticmethod
    def write(name: str, strings: list, max_str_length: int):
        # 连接到共享内存
        shm = shared_memory.SharedMemory(name=name)
        # 编码字符串数组
        encoded: bytearray = encode_strings(strings, max_str_length)
        # 将编码后的字符串数组写入共享内存
        for i in range(len(encoded)):
            shm.buf[i] = encoded[i]
        shm.close()

    @staticmethod
    def change(name:str, index: int, value: str):
        # 连接到共享内存
        shm = shared_memory.SharedMemory(name=name)
        buffer = shm.buf
        # 将 memoryview 转换为字节数组
        encoded = bytes(buffer[:])
        # 解码字符串数组
        strings = decode_strings(encoded, max_str_length, ignore_empty_str=False)
        strings[index] = value
        # 编码字符串数组
        encoded: bytearray = encode_strings(strings, max_str_length)
        # 将编码后的字符串数组写入共享内存
        for i in range(len(encoded)):
            shm.buf[i] = encoded[i]
        shm.close()
    
    @staticmethod
    def release(name: str):
        shm = shared_memory.SharedMemory(name=name)
        shm.unlink()
    

if __name__ == '__main__':

    def read_shared_data(name, max_str_length):
        strings = SharedMemoryStrList.read(name, max_str_length)
        print ("Read shared array:", strings)

    def write_shared_data(name, strings, max_str_length):
        SharedMemoryStrList.write(name, strings, max_str_length)
        print ("Write shared array:", strings)
        strings = SharedMemoryStrList.read(name, max_str_length)
        print ("Read shared array:", strings)

    name = 'teststrings'
    strings = ["hello", "world", "foo", "bar"]
    max_str_length = 20
    max_size = 100
    SharedMemoryStrList.create(name, strings, max_str_length, max_size)

    # 创建并启动子进程
    p = multiprocessing.Process(target=read_shared_data, args=(name, max_str_length))
    p.start()
    p.join()

    # 创建并启动子进程
    write_strings = ['aaaaa', 'bbbbb', 'cc', 'd']
    p = multiprocessing.Process(target=write_shared_data, args=(name, write_strings, max_str_length))
    p.start()
    p.join()

    SharedMemoryStrList.release(name)
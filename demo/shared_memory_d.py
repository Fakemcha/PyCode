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
def decode_strings(encoded, max_str_length):
    strings = []
    for i in range(0, len(encoded), max_str_length):
        strings.append(encoded[i:i+max_str_length].split(b'\x00', 1)[0].decode('utf-8'))
    return strings

def modify_shared_data(shm_name, max_str_length):
    # 连接到共享内存
    existing_shm = shared_memory.SharedMemory(name=shm_name)
    buffer = existing_shm.buf
    
    # 将 memoryview 转换为字节数组
    encoded = bytes(buffer[:])
    
    # 解码字符串数组
    strings = decode_strings(encoded, max_str_length)
    
    # 修改共享内存中的数据
    strings[0] = "aaabbbccccaaabbbcccc"
    strings[1] = "aaabbbccccaaabbbcccc"
    
    # 编码字符串数组
    encoded = encode_strings(strings, max_str_length)
    
    # 将编码后的字符串数组写回共享内存
    for i in range(len(encoded)):
        buffer[i] = encoded[i]
    
    # 关闭共享内存
    existing_shm.close()

if __name__ == '__main__':
    # 原始字符串数组
    strings = ["hello", "world", "foo", "bar"]
    # num_strings = len(strings)
    # max_str_length = max(len(s) for s in strings) + 1  # 加1以存储终止符
    max_str_length = 20  # 加1以存储终止符

    # 编码字符串数组
    encoded = encode_strings(strings, max_str_length)
    
    # 创建共享内存块
    shm = shared_memory.SharedMemory(create=True, size=len(encoded))
    
    # 将编码后的字符串数组写入共享内存
    for i in range(len(encoded)):
        shm.buf[i] = encoded[i]

    # 打印共享内存中的初始数据
    initial_strings = decode_strings(bytes(shm.buf[:]), max_str_length)
    print("Initial shared array:", initial_strings)
    
    # 创建并启动子进程
    p = multiprocessing.Process(target=modify_shared_data, args=(shm.name, max_str_length))
    p.start()
    p.join()

    # 打印修改后的共享内存数据
    modified_strings = decode_strings(bytes(shm.buf[:]), max_str_length)
    print("Modified shared array:", modified_strings)
    
    # 关闭并释放共享内存
    shm.close()
    shm.unlink()
